# =============================================================================
# cli/commands.py
# Click commands: seed, run, status.
# No business logic here — delegates to pipeline and core modules.
# =============================================================================

from __future__ import annotations

import logging
import sys
from datetime import date, datetime

import click

from engine.db.client import OracleClient
from engine.core.clock import SimClock
from engine.schema import tables as T

logger = logging.getLogger(__name__)


# =============================================================================
# CLI group
# =============================================================================

@click.group()
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    show_default=True,
    help="Logging verbosity.",
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    default=False,
    help="Enable DEBUG logging with full tracebacks (overrides --log-level).",
)
def cli(log_level: str, verbose: bool) -> None:
    """XLN Synthetic Data Generator."""
    effective_level = "DEBUG" if verbose else log_level.upper()
    logging.basicConfig(
        level   = effective_level,
        format  = "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S",
        stream  = sys.stdout,
    )
    if verbose:
        logger.debug("Verbose mode enabled — full tracebacks will be shown.")


# =============================================================================
# seed
# =============================================================================

@cli.command()
@click.option(
    "--start-date",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="First simulation date (YYYY-MM-DD).",
)
@click.option(
    "--end-date",
    default=None,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Last simulation date. Defaults to today.",
)
@click.option(
    "--customers", "-n",
    default=1_000,
    show_default=True,
    help="Number of customers to seed.",
)
def seed(start_date: datetime, end_date: datetime | None, customers: int) -> None:
    """
    Seed Oracle from scratch.

    Generates reference data, customers, contracts, and all FCT tables
    from START_DATE to END_DATE. Use when Oracle has no data yet.
    """
    start = start_date.date()
    end   = end_date.date() if end_date else date.today()

    click.echo(f"Seeding {start} → {end} ({customers:,} customers) …")

    try:
        with OracleClient() as db:
            from engine.pipeline.seed import SeedPipeline
            SeedPipeline(db).run(start_date=start, end_date=end, n_customers=customers)
    except ConnectionError as exc:
        logger.error("Cannot connect to Oracle: %s", exc)
        logger.debug("Connection error details:", exc_info=True)
        sys.exit(1)
    except Exception as exc:
        logger.error("Seed pipeline failed: %s", exc)
        logger.debug("Full traceback:", exc_info=True)
        sys.exit(1)

    click.secho("Seed complete.", fg="green")


# =============================================================================
# run
# =============================================================================

@cli.command()
@click.option(
    "--date", "run_date",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Run daily pipeline up to this date (inclusive).",
)
@click.option(
    "--customers", "-n",
    default=50,
    show_default=True,
    help="New customers to add per day.",
)
def run(run_date: datetime, customers: int) -> None:
    """
    Run the daily pipeline up to RUN_DATE.

    Picks up from MAX(DAYID) + 1 day and generates data for each
    missing day through RUN_DATE.
    """
    to_date = run_date.date()
    click.echo(f"Running daily pipeline → {to_date} …")

    try:
        with OracleClient() as db:
            clock = SimClock(to_date=to_date)
            dates = list(clock.dates_to_run(db))

            if not dates:
                click.secho("Already up to date — nothing to run.", fg="yellow")
                return

            click.echo(f"Dates to process: {dates[0]} → {dates[-1]} ({len(dates)} days)")

            from engine.pipeline.daily import DailyPipeline
            pipeline = DailyPipeline(db)
            for d in dates:
                try:
                    pipeline.run(run_date=d, n_customers=customers)
                except Exception as exc:
                    logger.error("[%s] Daily pipeline failed: %s", d, exc)
                    logger.debug("Full traceback:", exc_info=True)
                    sys.exit(1)

    except ConnectionError as exc:
        logger.error("Cannot connect to Oracle: %s", exc)
        logger.debug("Connection error details:", exc_info=True)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as exc:
        logger.error("Run command failed: %s", exc)
        logger.debug("Full traceback:", exc_info=True)
        sys.exit(1)

    click.secho(f"Daily pipeline complete: {len(dates)} days processed.", fg="green")


# =============================================================================
# reset
# =============================================================================

@cli.command()
@click.option(
    "--yes", "-y",
    is_flag=True,
    default=False,
    help="Skip confirmation prompt.",
)
def reset(yes: bool) -> None:
    """
    Delete ALL data from every table and reset Oracle identity columns.

    Deletes FCT tables first, then DIM tables to respect FK order.
    Resets any Oracle GENERATED AS IDENTITY columns back to START WITH 1.
    """
    if not yes:
        click.echo("This will DELETE ALL DATA from every XLN_DTM table.")
        confirmed = click.prompt("Type YES to confirm", default="")
        if confirmed != "YES":
            click.secho("Aborted.", fg="yellow")
            return

    # Delete order: FCT first, then DIM (FK safety)
    # DIM order: dependents before referenced tables
    from engine.schema import tables as T

    FCT_ORDER = [
        T.FCT_XLN_ACTIVE_LOAN,
        T.FCT_XLN_REPAYSCHEDULE,
        T.FCT_XLN_LOAN_TXN,
        T.FCT_XLN_CREDIT_FEE,
        T.FCT_XLN_BAD_DEBT,
        T.FCT_XLN_INT_WRITE_OFF,
        T.FCT_XLN_AFTER_COB_COLLECTION,
    ]

    DIM_ORDER = [
        T.DIM_XLN_CUST_PII,        # depends on CUST
        T.DIM_XLN_CARD,
        T.DIM_XLN_CUST,
        T.DIM_XLN_CONTRACT,
        T.DIM_XLN_COMPANY,
        T.DIM_XLN_PRODUCT,
        T.DIM_XLN_SALECODE,
        T.DIM_XLN_BUCKET,
        T.DIM_XLN_CALENDAR,
        T.DIM_XLN_LOAN_TXN_CODE,
    ]

    # Tables that use Oracle GENERATED AS IDENTITY — must be reset after DELETE
    # Syntax: ALTER TABLE <name> MODIFY <col> GENERATED BY DEFAULT AS IDENTITY (START WITH 1)
    IDENTITY_RESETS: list[tuple[str, str]] = [
        (T.DIM_XLN_BUCKET.oracle_name, "DIMENSION_ID"),
    ]

    try:
        with OracleClient() as db:
            total_deleted = 0

            click.echo("\nDeleting FCT tables …")
            for table in FCT_ORDER:
                if not db.table_exists(table.oracle_name):
                    click.echo(f"  {table.oracle_name} — not found, skipping.")
                    continue
                n = db.row_count(table)
                db.execute(f"DELETE FROM {table.oracle_name}")
                click.echo(f"  {table.oracle_name:<45} {n:>10,} rows deleted.")
                total_deleted += n

            click.echo("\nDeleting DIM tables …")
            for table in DIM_ORDER:
                if not db.table_exists(table.oracle_name):
                    click.echo(f"  {table.oracle_name} — not found, skipping.")
                    continue
                n = db.row_count(table)
                db.execute(f"DELETE FROM {table.oracle_name}")
                click.echo(f"  {table.oracle_name:<45} {n:>10,} rows deleted.")
                total_deleted += n

            click.echo("\nResetting identity columns …")
            for oracle_name, col in IDENTITY_RESETS:
                if not db.table_exists(oracle_name):
                    click.echo(f"  {oracle_name}.{col} — table not found, skipping.")
                    continue
                sql = (
                    f"ALTER TABLE {oracle_name} MODIFY {col} "
                    f"GENERATED BY DEFAULT AS IDENTITY (START WITH 1)"
                )
                db.execute(sql)
                click.echo(f"  {oracle_name}.{col} — reset to START WITH 1.")

            click.echo()
            click.secho(
                f"Reset complete — {total_deleted:,} rows deleted, "
                f"{len(IDENTITY_RESETS)} identity column(s) reset.",
                fg="green",
            )

    except ConnectionError as exc:
        logger.error("Cannot connect to Oracle: %s", exc)
        logger.debug("Connection error details:", exc_info=True)
        sys.exit(1)
    except Exception as exc:
        logger.error("Reset failed: %s", exc)
        logger.debug("Full traceback:", exc_info=True)
        sys.exit(1)


# =============================================================================
# status
# =============================================================================

@cli.command()
def status() -> None:
    """
    Print data status: latest DAYID, row counts, and missing tables.
    """
    fct_keys = list(T.FCT_TABLES)

    try:
        with OracleClient() as db:
            click.echo(f"\n{'TABLE':<40} {'MAX DAYID':<12} {'ROWS':>12}")
            click.echo("-" * 67)

            missing_tables: list[str] = []

            for key in sorted(fct_keys):
                table = T.get(key)

                if not db.table_exists(table.oracle_name):
                    missing_tables.append(table.oracle_name)
                    click.secho(f"  {table.oracle_name:<38} {'MISSING':<12}", fg="red")
                    continue

                max_day = db.max_dayid(table) or "—"
                row_cnt = db.row_count(table)
                click.echo(f"  {table.oracle_name:<38} {max_day:<12} {row_cnt:>12,}")

            click.echo()

            if missing_tables:
                click.secho(
                    f"⚠  {len(missing_tables)} table(s) missing in Oracle.",
                    fg="yellow",
                )
            else:
                click.secho("✓  All tables present.", fg="green")

    except ConnectionError as exc:
        logger.error("Cannot connect to Oracle: %s", exc)
        logger.debug("Connection error details:", exc_info=True)
        sys.exit(1)
    except Exception as exc:
        logger.error("Status command failed: %s", exc)
        logger.debug("Full traceback:", exc_info=True)
        sys.exit(1)
