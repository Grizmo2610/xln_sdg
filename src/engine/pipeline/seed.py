# =============================================================================
# pipeline/seed.py
# SeedPipeline — run once when Oracle has no data.
#
# Step 1: Static DIM tables (Calendar, Bucket, LoanTxnCode)
# Step 2: ReferenceGenerator → Company, Product, Salecode
# Step 3: CustomerGenerator  → Cust, CustPII, Contract (in batches)
# Step 4: PoolRegistry.refresh()
# Step 5: LoanGenerator      → Card + all FCT tables, day by day
# =============================================================================

from __future__ import annotations

import logging
from datetime import date, timedelta

from engine.db.client import OracleClient
from engine.core.pool import PoolRegistry
from engine.schema import tables as T
from engine.schema.columns import CONTRACT, NO_DAYS_OVERDUE, BALANCE, BALANCE_PD
from engine.models.base_dims import CalendarDimLoader, BucketDimLoader, LoanTxnCodeDimLoader
from engine.generators.reference import ReferenceGenerator
from engine.generators.customer import CustomerGenerator
from engine.generators.loan import LoanGenerator

logger = logging.getLogger(__name__)

_CUSTOMER_BATCH = 500
_N_SALES_SEED   = 80


class SeedPipeline:
    """
    One-time full seed: generates data from start_date through end_date.
    Assumes Oracle tables exist but are empty.
    """

    def __init__(self, db: OracleClient) -> None:
        self._db   = db
        self._pool = PoolRegistry(db)

    def run(self, start_date: date, end_date: date, n_customers: int) -> None:
        # If Oracle already has FCT data, resume from MAX(DAYID) + 1
        max_loaded = self._db.max_dayid(T.FCT_XLN_ACTIVE_LOAN)
        if max_loaded is not None:
            resume_from = max_loaded.date() + timedelta(days=1) if hasattr(max_loaded, "date") else max_loaded + timedelta(days=1)
            if resume_from > end_date:
                logger.info(
                    "SeedPipeline: data already loaded up to %s — nothing to do.",
                    max_loaded,
                )
                return
            logger.info(
                "SeedPipeline: data already loaded up to %s — resuming from %s.",
                max_loaded, resume_from,
            )
            start_date = resume_from

        logger.info(
            "SeedPipeline starting: start=%s end=%s customers=%d",
            start_date, end_date, n_customers,
        )

        # ------------------------------------------------------------------
        # Step 1: Static reference DIM tables
        # ------------------------------------------------------------------
        logger.info("Step 1/5: inserting static DIM tables (Calendar, Bucket, LoanTxnCode) …")
        try:
            for table, loader_fn in [
                (T.DIM_XLN_CALENDAR,      lambda: CalendarDimLoader().generate(start_date, end_date)),
                (T.DIM_XLN_BUCKET,        lambda: BucketDimLoader().generate()),
                (T.DIM_XLN_LOAN_TXN_CODE, lambda: LoanTxnCodeDimLoader().generate()),
            ]:
                if self._db.row_count(table) > 0:
                    logger.info("Step 1/5: %s already has data — skipping.", table.oracle_name)
                    continue
                self._db.insert(table, loader_fn())
            logger.info("Step 1/5: done.")
        except Exception as exc:
            logger.error("Step 1/5 failed (static DIM tables): %s", exc)
            logger.debug("Step 1 error details:", exc_info=True)
            raise

        # ------------------------------------------------------------------
        # Step 2: ReferenceGenerator
        # ------------------------------------------------------------------
        logger.info("Step 2/5: generating reference data (Company, Product, Salecode) …")
        try:
            ref_result = ReferenceGenerator().generate(
                run_date = start_date,
                pool     = self._pool,
                n_sales  = _N_SALES_SEED,
            )
            self._db.insert(T.DIM_XLN_COMPANY,  ref_result["COMPANY"])
            self._db.insert(T.DIM_XLN_PRODUCT,  ref_result["PRODUCT"])
            self._db.insert(T.DIM_XLN_SALECODE, ref_result["SALECODE"])
            self._pool.refresh("COMPANY", "PRODUCT", "SALECODE")
            logger.info("Step 2/5: done.")
        except Exception as exc:
            logger.error("Step 2/5 failed (reference data): %s", exc)
            logger.debug("Step 2 error details:", exc_info=True)
            raise

        # ------------------------------------------------------------------
        # Step 3: CustomerGenerator — batches
        # ------------------------------------------------------------------
        logger.info("Step 3/5: generating %d customers …", n_customers)
        cust_gen        = CustomerGenerator()
        cust_sk_off     = 0
        contract_sk_off = 0
        remaining       = n_customers

        while remaining > 0:
            batch_n    = min(_CUSTOMER_BATCH, remaining)
            batch_num  = (n_customers - remaining) // _CUSTOMER_BATCH + 1
            logger.info(
                "Step 3/5: batch %d — generating %d customers (offset cust=%d, contract=%d) …",
                batch_num, batch_n, cust_sk_off, contract_sk_off,
            )
            try:
                result = cust_gen.generate(
                    run_date           = start_date,
                    pool               = self._pool,
                    n                  = batch_n,
                    sk_offset_cust     = cust_sk_off,
                    sk_offset_contract = contract_sk_off,
                )
                self._db.insert(T.DIM_XLN_CUST,    result["CUST"])
                self._db.insert(T.DIM_XLN_CUST_PII, result["CUST_PII"])
                self._db.insert(T.DIM_XLN_CONTRACT, result["CONTRACT"])
            except Exception as exc:
                logger.error(
                    "Step 3/5 failed at batch %d (customers %d–%d): %s",
                    batch_num,
                    n_customers - remaining,
                    n_customers - remaining + batch_n,
                    exc,
                )
                logger.debug("Step 3 batch error details:", exc_info=True)
                raise

            cust_sk_off     += len(result["CUST"])
            contract_sk_off += len(result["CONTRACT"])
            remaining       -= batch_n
            logger.info(
                "Step 3/5: %d / %d customers seeded.",
                n_customers - remaining, n_customers,
            )

        logger.info("Step 3/5: done.")

        # ------------------------------------------------------------------
        # Step 4: Refresh pools
        # ------------------------------------------------------------------
        logger.info("Step 4/5: refreshing pools (CUST, CONTRACT, BUCKET) …")
        try:
            self._pool.refresh("CUST", "CONTRACT", "BUCKET")
            logger.info("Step 4/5: done.")
        except Exception as exc:
            logger.error("Step 4/5 failed (pool refresh): %s", exc)
            logger.debug("Step 4 error details:", exc_info=True)
            raise

        # ------------------------------------------------------------------
        # Step 5: LoanGenerator — one pass per day
        # ------------------------------------------------------------------
        total_days = (end_date - start_date).days + 1
        logger.info(
            "Step 5/5: generating FCT tables for %d days (%s → %s) …",
            total_days, start_date, end_date,
        )
        loan_gen    = LoanGenerator()
        card_sk_off = 0
        prev_state  = None
        current     = start_date
        day_num     = 0

        while current <= end_date:
            day_num += 1
            logger.info(
                "Step 5/5: [%s] day %d/%d — generating FCT tables …",
                current, day_num, total_days,
            )
            try:
                result = loan_gen.generate(
                    run_date       = current,
                    pool           = self._pool,
                    mapping_df     = None,
                    prev_state     = prev_state,
                    card_sk_offset = card_sk_off,
                )

                if not result["CARD"].is_empty():
                    logger.info("Step 5/5: [%s] inserting DIM_XLN_CARD …", current)
                    self._db.insert(T.DIM_XLN_CARD, result["CARD"])
                    card_sk_off += len(result["CARD"])

                for key, table in [
                    ("ACTIVE_LOAN",         T.FCT_XLN_ACTIVE_LOAN),
                    ("REPAYSCHEDULE",        T.FCT_XLN_REPAYSCHEDULE),
                    ("LOAN_TXN",             T.FCT_XLN_LOAN_TXN),
                    ("CREDIT_FEE",           T.FCT_XLN_CREDIT_FEE),
                    ("BAD_DEBT",             T.FCT_XLN_BAD_DEBT),
                    ("INT_WRITE_OFF",        T.FCT_XLN_INT_WRITE_OFF),
                    ("AFTER_COB_COLLECTION", T.FCT_XLN_AFTER_COB_COLLECTION),
                ]:
                    logger.info(
                        "Step 5/5: [%s] inserting %s (%d rows) …",
                        current, table.oracle_name, len(result[key]),
                    )
                    self._db.insert(table, result[key])

            except Exception as exc:
                logger.error(
                    "Step 5/5: [%s] FCT generation/insert failed: %s", current, exc
                )
                logger.debug("Step 5 day error details:", exc_info=True)
                raise

            # Fetch prev_state for the next day
            prev_state = self._db.fetch_pool(
                T.FCT_XLN_ACTIVE_LOAN,
                columns=[CONTRACT, NO_DAYS_OVERDUE, BALANCE, BALANCE_PD],
                where  ="DAYID = :1",
                params =[current],
            )
            if prev_state.is_empty():
                prev_state = None

            logger.info("Step 5/5: [%s] done.", current)
            current += timedelta(days=1)

        logger.info("SeedPipeline complete: %d days seeded.", total_days)
