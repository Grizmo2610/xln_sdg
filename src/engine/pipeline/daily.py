from __future__ import annotations

import logging
from datetime import date, timedelta

from engine.db.client import OracleClient
from engine.core.pool import PoolRegistry
from engine.schema import tables as T
from engine.schema.columns import CONTRACT, NO_DAYS_OVERDUE, BALANCE, BALANCE_PD
from engine.generators.reference import ReferenceGenerator
from engine.generators.customer import CustomerGenerator
from engine.generators.loan import LoanGenerator

logger = logging.getLogger(__name__)

_N_SALES_CHURN = 2

class DailyPipeline:
    """
    Incremental daily pipeline. Called once per missing day by cli/commands.py.
    """

    def __init__(self, db: OracleClient) -> None:
        self._db       = db
        self._pool     = PoolRegistry(db)
        self._ref_gen  = ReferenceGenerator()
        self._cust_gen = CustomerGenerator()
        self._loan_gen = LoanGenerator()

        self._card_sk_off:  int | None = None
        self._sales_sk_off: int | None = None

    # Public

    def run(self, run_date: date, n_customers: int) -> None:
        logger.info(
            "[%s] DailyPipeline starting — new_customers=%d", run_date, n_customers
        )

        # a. SCD2 churn — add new sales staff
        logger.info("[%s] Step a: SCD2 churn (Salecode) …", run_date)
        try:
            new_sales = self._ref_gen.scd2_churn(
                run_date        = run_date,
                n_new           = _N_SALES_CHURN,
                sk_offset_sales = self._next_sales_sk(),
            )
            if not new_sales.is_empty():
                self._db.insert(T.DIM_XLN_SALECODE, new_sales)
                self._sales_sk_off = (self._sales_sk_off or 0) + len(new_sales)
                self._pool.refresh("SALECODE")
                logger.info("[%s] Step a: added %d new sales staff.", run_date, len(new_sales))
            else:
                logger.info("[%s] Step a: no new sales staff.", run_date)
        except Exception as exc:
            logger.error("[%s] Step a failed (SCD2 churn): %s", run_date, exc)
            logger.debug("Step a error details:", exc_info=True)
            raise

        # b. New customers + contracts
        logger.info("[%s] Step b: generating %d new customers + contracts …", run_date, n_customers)
        try:
            cust_result = self._cust_gen.generate(
                run_date           = run_date,
                pool               = self._pool,
                n                  = n_customers,
                sk_offset_cust     = self._next_cust_sk(),
                sk_offset_contract = self._next_contract_sk(),
            )
            self._db.insert(T.DIM_XLN_CUST,    cust_result["CUST"])
            self._db.insert(T.DIM_XLN_CUST_PII, cust_result["CUST_PII"])
            self._db.insert(T.DIM_XLN_CONTRACT, cust_result["CONTRACT"])
            logger.info(
                "[%s] Step b: inserted %d customers, %d contracts.",
                run_date, len(cust_result["CUST"]), len(cust_result["CONTRACT"]),
            )
        except Exception as exc:
            logger.error("[%s] Step b failed (CustomerGenerator): %s", run_date, exc)
            logger.debug("Step b error details:", exc_info=True)
            raise

        # c. Refresh pools
        logger.info("[%s] Step c: refreshing pools (CUST, CONTRACT) …", run_date)
        try:
            self._pool.refresh("CUST", "CONTRACT")
            logger.info("[%s] Step c: done.", run_date)
        except Exception as exc:
            logger.error("[%s] Step c failed (pool refresh): %s", run_date, exc)
            logger.debug("Step c error details:", exc_info=True)
            raise

        # d. Load prev_state from D-1
        prev_date = run_date - timedelta(days=1)
        logger.info("[%s] Step d: loading prev_state from FCT_XLN_ACTIVE_LOAN (DAYID=%s) …", run_date, prev_date)
        try:
            prev_state = self._db.fetch_pool(
                T.FCT_XLN_ACTIVE_LOAN,
                columns=[CONTRACT, NO_DAYS_OVERDUE, BALANCE, BALANCE_PD],
                where  ="DAYID = :1",
                params =[prev_date],
            )
            if prev_state.is_empty():
                logger.info("[%s] Step d: no prev_state found (first day or no data for %s).", run_date, prev_date)
                prev_state = None
            else:
                logger.info("[%s] Step d: loaded %d contracts from prev_state.", run_date, len(prev_state))
        except Exception as exc:
            logger.error("[%s] Step d failed (loading prev_state for %s): %s", run_date, prev_date, exc)
            logger.debug("Step d error details:", exc_info=True)
            raise

        # e. Generate FCT tables
        logger.info("[%s] Step e: generating FCT tables (LoanGenerator) …", run_date)
        try:
            result = self._loan_gen.generate(
                run_date       = run_date,
                pool           = self._pool,
                mapping_df     = cust_result["_mapping"],
                prev_state     = prev_state,
                card_sk_offset = self._next_card_sk(),
            )
        except Exception as exc:
            logger.error("[%s] Step e failed (LoanGenerator): %s", run_date, exc)
            logger.debug("Step e error details:", exc_info=True)
            raise

        # f. INSERT FCT rows
        logger.info("[%s] Step f: inserting FCT tables …", run_date)
        try:
            if not result["CARD"].is_empty():
                logger.info("[%s] Step f: inserting DIM_XLN_CARD (%d rows) …", run_date, len(result["CARD"]))
                self._db.insert(T.DIM_XLN_CARD, result["CARD"])
                self._card_sk_off = (self._card_sk_off or 0) + len(result["CARD"])

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
                    "[%s] Step f: inserting %s (%d rows) …",
                    run_date, table.oracle_name, len(result[key]),
                )
                self._db.insert(table, result[key])

        except Exception as exc:
            logger.error("[%s] Step f failed (FCT insert): %s", run_date, exc)
            logger.debug("Step f error details:", exc_info=True)
            raise

        del prev_state
        logger.info("[%s] DailyPipeline complete.", run_date)

    # SK offset helpers

    def _next_cust_sk(self) -> int:
        row = self._db.select(
            f"SELECT NVL(MAX(DIMENSION_KEY), 0) FROM {T.DIM_XLN_CUST.oracle_name}"
        ).row(0)
        return int(row[0])

    def _next_contract_sk(self) -> int:
        row = self._db.select(
            f"SELECT NVL(MAX(DIMENSION_ID), 0) FROM {T.DIM_XLN_CONTRACT.oracle_name}"
        ).row(0)
        return int(row[0])

    def _next_card_sk(self) -> int:
        if self._card_sk_off is None:
            row = self._db.select(
                f"SELECT NVL(MAX(DIMENSION_KEY), 0) FROM {T.DIM_XLN_CARD.oracle_name}"
            ).row(0)
            self._card_sk_off = int(row[0])
        return self._card_sk_off

    def _next_sales_sk(self) -> int:
        if self._sales_sk_off is None:
            row = self._db.select(
                f"SELECT NVL(MAX(DIMENSION_KEY), 0) FROM {T.DIM_XLN_SALECODE.oracle_name}"
            ).row(0)
            self._sales_sk_off = int(row[0])
        return self._sales_sk_off
