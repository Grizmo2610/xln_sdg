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
def cli(log_level: str) -> None:
    """XLN Synthetic Data Generator."""
    logging.basicConfig(
        level       = log_level.upper(),
        format      = "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt     = "%Y-%m-%d %H:%M:%S",
        stream      = sys.stdout,
    )


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

    with OracleClient() as db:
        from engine.pipeline.seed import SeedPipeline
        SeedPipeline(db).run(start_date=start, end_date=end, n_customers=customers)

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

    with OracleClient() as db:
        clock  = SimClock(to_date=to_date)
        dates  = list(clock.dates_to_run(db))

        if not dates:
            click.secho("Already up to date — nothing to run.", fg="yellow")
            return

        click.echo(f"Dates to process: {dates[0]} → {dates[-1]} ({len(dates)} days)")

        from engine.pipeline.daily import DailyPipeline
        pipeline = DailyPipeline(db)
        for d in dates:
            pipeline.run(run_date=d, n_customers=customers)

    click.secho(f"Daily pipeline complete: {len(dates)} days processed.", fg="green")


# =============================================================================
# status
# =============================================================================

@cli.command()
def status() -> None:
    """
    Print data status: latest DAYID, row counts, and missing tables.
    """
    fct_keys = list(T.FCT_TABLES)

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

            max_day  = db.max_dayid(table) or "—"
            row_cnt  = db.row_count(table)
            click.echo(f"  {table.oracle_name:<38} {max_day:<12} {row_cnt:>12,}")

        click.echo()

        if missing_tables:
            click.secho(
                f"⚠  {len(missing_tables)} table(s) missing in Oracle.",
                fg="yellow",
            )
        else:
            click.secho("✓  All tables present.", fg="green")