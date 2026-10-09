from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Optional

import numpy as np
import polars as pl

logger = logging.getLogger(__name__)

from engine.core.base import BaseGenerator
from engine.core.pool import PoolRegistry
from engine.core.hazard import HazardModel
from engine.core.sampling import SamplingEngine
from engine.config import propensity as prop
from engine.config import listchoice as L
from engine.config.constant import (
    LOAN_AMT_MIN, LOAN_AMT_MAX,
    DAILY_REPAY_MIN, DAILY_REPAY_MAX,
    FEE_AMT_MIN, FEE_AMT_MAX,
    WRITE_OFF_AMT_MIN, WRITE_OFF_AMT_MAX,
    CARD_EXPIRY_YEARS,
    BAD_DEBT_DPD_THRESHOLD,
    EXP_DATE_SENTINEL,
)
from engine.config.random import rng
from engine.schema.columns import (
    DAYID, EFF_DATE, EXP_DATE,
    CUST_KEY, CONTRACT_ID, COMPANY_KEY, PRODUCT_KEY, BUCKET_ID,
    CARD_KEY, SALES_KEY,
    CUSTOMER, SHORT_NAME, CITY_CODE,
    CONTRACT, DATASOURCE, VALUE_DATE, MATURITY_DATE, CO_CODE,
    CATEGORY, CURRENCY, SOURCE_TYPE, CAMPAIGN_ID,
    CARD_ID, MAIN_ID, CARD_STATUS, CARD_TYPE, LIMIT_DES,
    CUSTOMER_ID, CARD_EXPIRE, ACCOUNT_ID,
    CUSTOMER_SK, CONTRACT_SK, XLN_CONTRACT_SK,
    COMPANY_SK, PRODUCT_SK, BUCKET_SK, CARD_SK, SALES_SK,
    PD_CONTRACT, DISBURSEMENT_AMT, NO_DAYS_OVERDUE, PD_NO,
    BALANCE, BALANCE_PD, BALANCE_IN, BALANCE_PE, BALANCE_PS,
    TOTAL_BALANCE, TOTAL_EXPOSURE, TOTAL_OVD,
    DEBT_SETTLEMENT, BOM_DPD, YESTERDAY_DPD, MAX_OVD,
    INTEREST, OVD_RATE, FIRST_ACTIVED_DATE, LAST_ACTIVED_DATE,
    MAX_OVD_IN_MONTH,
    REPAYMENT_TYPE, REPAYMENT_DATE, REPAYMENT_AMT,
    REPAYMENT_ACCT, PAY_ACCT_BAL, SCH_FREQ, SCH_FREQ_CODE,
    BALANCE_IN, BAL_PD_TOTAL,
    CONTRACT_MAIN, TRANS_DATE, TRANS_CODE, TRANS_AMOUNT_LCY,
    PRIN_BALANCE, PRIN_OVERDUE, IN_OVERDUE, PE, PS, PE_PS,
    NO_DAY_OVERDUE, CLASSIFICATION, SEAB_PARTNER,
    MIS_DAO, CURR_MIS_DAO, MIS_DAO1_NAME, CUR_MIS_DAO_NAME,
    ADDITION_CODE, ADDITION_VALUE,
    SALE_TYPE, SALE_ID, SALE_NAME,
    BROKER_TYPE, BROKER_ID, BROKER_NAME,
    SUB_PRODUCT, SUB_PRODUCT_NAME, SUB_CATEGORY, SUB_CATEGORY_NAME,
    SEAB_PRODUCTS, SEAB_PRODUCTS_SK, CATEGORY_SK, SOURCE, TRANS_AMOUNT,
    PRODUCT,
    ENTRY_ID, PL_CATEGORY, COMPANY, FEE_AMT, FEE_AMT_LCY, FEE_NAME, FEE_ID,
    CUSTOMER_NAME, COMPANY_NAME, CCY,
    CONTRACT_MD, PRINCIPAL_AMT, REC_STATUS, FIRST_PRINCIPAL_AMT,
    AMOUNT, AMOUNT_LCY, NARRATIVE, NARRATIVE_ALL, COMPANY_CODE,
    SECTOR,
)

# Helpers

def _rid(prefix: str = "", n: int = 8) -> str:
    return prefix + "".join(str(rng.integers(0, 10)) for _ in range(n))

def _classify(dpd: int) -> str:
    group = "N01"
    for threshold, label in L.DPD_CLASSIFICATION:
        if dpd >= threshold:
            group = label
    return group

def _build_lookup(df: pl.DataFrame, key_col: str, val_col: str) -> dict:
    return dict(zip(df[key_col].to_list(), df[val_col].to_list()))

def _df(rows: list[dict]) -> pl.DataFrame:
    return pl.DataFrame(rows) if rows else pl.DataFrame()

# LoanGenerator

class LoanGenerator(BaseGenerator):

    def required_pools(self) -> list[str]:
        return ["CUST", "CONTRACT", "COMPANY", "PRODUCT", "BUCKET", "SALECODE"]

    def generate(
        self,
        run_date: date,
        pool: PoolRegistry,
        n: int = 0,
        mapping_df: Optional[pl.DataFrame] = None,
        prev_state: Optional[pl.DataFrame] = None,
        card_sk_offset: int = 0,
    ) -> dict[str, pl.DataFrame]:

        month = run_date.month
        cfg = prop.get_monthly(month)
        hazard = cfg

        # 1. Load pools
        cust_df     = pool.get("CUST")
        contract_df = pool.get("CONTRACT")
        company_df  = pool.get("COMPANY")
        product_df  = pool.get("PRODUCT")
        bucket_df   = pool.get("BUCKET")
        sale_df     = pool.get("SALECODE")

        # 2. Build lookup dicts
        cust_sk_map     = _build_lookup(cust_df,     CUSTOMER,    CUST_KEY)
        cust_name_map   = _build_lookup(cust_df,     CUSTOMER,    SHORT_NAME)  # real name lookup
        contract_sk_map = _build_lookup(contract_df, CONTRACT,    CONTRACT_ID)
        company_sks     = company_df[COMPANY_KEY].to_list()
        product_sks     = product_df[PRODUCT_KEY].to_list()
        sale_sks        = sale_df[SALES_KEY].to_list()
        bucket_map      = _build_lookup(bucket_df, "OVD_NO", BUCKET_ID)

        def _bucket_sk(dpd: int) -> int:
            return bucket_map.get(dpd, bucket_map.get(0))

        # 3. Contract → customer mapping
        contract_to_cust: dict[str, str] = {}
        if mapping_df is not None and not mapping_df.is_empty():
            contract_to_cust = _build_lookup(mapping_df, CONTRACT, CUSTOMER)

        all_custs = cust_df[CUSTOMER].to_list()
        for cid in contract_df[CONTRACT].to_list():
            if cid not in contract_to_cust:
                contract_to_cust[cid] = str(rng.choice(all_custs))

        # 4. Prev state lookup
        prev: dict[str, dict] = {}
        if prev_state is not None and not prev_state.is_empty():
            for row in prev_state.iter_rows(named=True):
                prev[row[CONTRACT]] = {
                    "dpd":        row.get(NO_DAYS_OVERDUE, 0) or 0,
                    "balance":    row.get(BALANCE, 0) or 0,
                    "balance_pd": row.get(BALANCE_PD, 0) or 0,
                    "state":      row.get("STATE", "NORMAL") or "NORMAL",
                }

        # 5. Pre-sample ALL random values vectorised — one call per array
        n_contracts = len(contract_df)
        rand_vals        = rng.random(n_contracts)
        fee_flags        = rng.random(n_contracts) < cfg["FEE_RATE"]
        wo_flags         = rng.random(n_contracts) < cfg["WRITE_OFF_RATE"]
        company_sk_arr   = rng.choice(company_sks,           size=n_contracts)
        product_sk_arr   = rng.choice(product_sks,           size=n_contracts)
        sale_sk_arr      = rng.choice(sale_sks,              size=n_contracts)
        disb_amt_arr     = rng.integers(LOAN_AMT_MIN,        LOAN_AMT_MAX + 1,       size=n_contracts)
        init_bal_arr     = rng.integers(LOAN_AMT_MIN,        LOAN_AMT_MAX + 1,       size=n_contracts)
        daily_repay_arr  = rng.integers(DAILY_REPAY_MIN,     DAILY_REPAY_MAX + 1,    size=n_contracts)
        balance_in_arr   = rng.integers(0,                   500_001,                size=n_contracts)
        interest_arr     = rng.uniform(hazard["interest_min"], hazard["interest_max"], size=n_contracts)
        ovd_rate_arr     = rng.uniform(hazard["ovd_rate_min"], hazard["ovd_rate_max"], size=n_contracts)
        pe_arr           = rng.integers(hazard["pe_per_day_min"], hazard["pe_per_day_max"] + 1, size=n_contracts)
        ps_arr           = rng.integers(hazard["ps_per_day_min"], hazard["ps_per_day_max"] + 1, size=n_contracts)
        next_repay_days  = rng.integers(1, 31,                  size=n_contracts)
        n_repay_arr      = rng.integers(1, 4,                   size=n_contracts)
        fee_amt_arr      = rng.integers(FEE_AMT_MIN,    FEE_AMT_MAX + 1,         size=n_contracts)
        wo_amt_arr       = rng.integers(WRITE_OFF_AMT_MIN, WRITE_OFF_AMT_MAX + 1, size=n_contracts)
        card_status_arr  = rng.choice(L.CARD_STATUSES,      size=n_contracts)
        card_type_arr    = rng.choice(L.CARD_TYPES,         size=n_contracts)
        sector_arr       = rng.choice(L.SECTORS,            size=n_contracts)
        pl_cat_arr       = rng.choice(L.PL_CATS_FEE,        size=n_contracts)
        fee_tcode_arr    = rng.choice(L.TRANS_CODES,        size=n_contracts)
        fee_name_arr     = rng.choice(L.FEE_NAMES,          size=n_contracts)
        wo_pl_cat_arr    = rng.choice(L.PL_CATS_WO,         size=n_contracts)
        n_txn_arr        = rng.integers(1, 3,               size=n_contracts)

        # 5b. Run HazardModel ONCE on the full batch (vectorised)
        contracts_list = contract_df[CONTRACT].to_list()
        datasource_list = [r.get(DATASOURCE, "LD") or "LD" for r in contract_df.iter_rows(named=True)]
        maturity_list   = [r.get(MATURITY_DATE) or (run_date + timedelta(days=365)) for r in contract_df.iter_rows(named=True)]

        state_list  = [prev.get(c, {}).get("state", "NORMAL") or "NORMAL" for c in contracts_list]
        dpd_list    = [int(prev.get(c, {}).get("dpd", 0))                  for c in contracts_list]

        hazard_df = pl.DataFrame({
            "STATE":         state_list,
            "DPD":           dpd_list,
            "MATURITY_DATE": maturity_list,
            "random_val":    rand_vals.tolist(),
            "p_prepay":      [hazard["p_prepay"]]    * n_contracts,
            "p_default":     [hazard["p_default"]]   * n_contracts,
            "p_cure":        [hazard["p_cure"]]       * n_contracts,
            "p_worsen":      [hazard["p_worsen"]]     * n_contracts,
        })
        hazard_df  = HazardModel.transition(hazard_df, run_date)
        hazard_df  = HazardModel.update_dpd(hazard_df)
        new_states = hazard_df["STATE"].to_list()
        new_dpds   = hazard_df["DPD"].to_list()

        # 6. Output accumulators
        card_rows, active_loan_rows, repay_rows = [], [], []
        txn_rows, fee_rows = [], []
        bad_debt_rows, write_off_rows, cob_rows = [], [], []
        card_sk_seq = card_sk_offset

        # 7. Main loop — one pass per contract
        for idx, contract_row in enumerate(contract_df.iter_rows(named=True)):
          try:
            contract_id = contract_row[CONTRACT]
            datasource  = contract_row.get(DATASOURCE, "LD") or "LD"
            co_code     = contract_row.get(CO_CODE, "HN") or "HN"
            val_date    = contract_row.get(VALUE_DATE) or run_date
            mat_date    = contract_row.get(MATURITY_DATE) or (run_date + timedelta(days=365))
            contract_sk = contract_sk_map.get(contract_id, 0)

            customer_id = contract_to_cust.get(contract_id, "")
            customer_sk = cust_sk_map.get(customer_id, 0)
            company_sk  = int(company_sk_arr[idx])
            product_sk  = int(product_sk_arr[idx])
            sale_sk     = int(sale_sk_arr[idx])

            # ---- State from previous day (precomputed in hazard_df) ----
            state_prev   = prev.get(contract_id, {})
            prev_dpd     = dpd_list[idx]
            prev_balance = int(state_prev.get("balance", int(init_bal_arr[idx])))
            prev_bal_pd  = int(state_prev.get("balance_pd", 0))
            new_state    = new_states[idx]
            dpd          = new_dpds[idx]

            # ---- Balances ----
            daily_repay = int(daily_repay_arr[idx])
            balance     = max(0, prev_balance - daily_repay)
            balance_pd  = prev_bal_pd if dpd > 0 else 0
            balance_pe  = int(pe_arr[idx]) if dpd > 0 else 0
            balance_ps  = int(ps_arr[idx]) if dpd > 0 else 0
            bucket_sk   = _bucket_sk(dpd)
            disb_amt    = int(disb_amt_arr[idx])
            total_bal   = balance + balance_pd
            total_ovd   = balance_pd + balance_pe + balance_ps
            total_exp   = total_bal + balance_pe + balance_ps

            # ---- DIM_XLN_CARD (VS only) ----
            card_exp    = val_date + timedelta(days=365 * CARD_EXPIRY_YEARS)
            card_sk_val = None
            if datasource == "VS":
                card_sk_seq += 1
                card_sk_val  = card_sk_seq
                card_rows.append({
                    CARD_KEY:    card_sk_seq,
                    CARD_ID:     _rid("CARD"),
                    MAIN_ID:     _rid("MAIN"),
                    VALUE_DATE:  val_date,
                    CARD_STATUS: str(card_status_arr[idx]),
                    CARD_TYPE:   str(card_type_arr[idx]),
                    LIMIT_DES:   _rid("POL", 4),
                    EFF_DATE:    val_date,
                    EXP_DATE:    EXP_DATE_SENTINEL,
                    CUSTOMER_ID: customer_id,
                    CARD_EXPIRE: f"{card_exp.month:02d}{str(card_exp.year)[-2:]}",
                    ACCOUNT_ID:  _rid("TK"),
                })

            # ---- FCT_XLN_ACTIVE_LOAN ----
            interest = round(float(interest_arr[idx]), 4)
            ovd_rate = round(float(ovd_rate_arr[idx]), 4)

            active_loan_rows.append({
                DAYID:              run_date,
                CONTRACT:           contract_id,
                PD_CONTRACT:        None,
                DISBURSEMENT_AMT:   disb_amt,
                NO_DAYS_OVERDUE:    dpd,
                PD_NO:              1 if dpd > 0 else 0,
                BALANCE:            balance,
                BALANCE_PD:         balance_pd,
                BALANCE_IN:         int(balance_in_arr[idx]) if dpd > 0 else 0,
                BALANCE_PE:         balance_pe,
                BALANCE_PS:         balance_ps,
                TOTAL_BALANCE:      total_bal,
                TOTAL_EXPOSURE:     total_exp,
                TOTAL_OVD:          total_ovd,
                DEBT_SETTLEMENT:    "0",
                BOM_DPD:            prev_dpd,
                YESTERDAY_DPD:      prev_dpd,
                MAX_OVD:            max(dpd, prev_dpd),
                INTEREST:           interest,
                OVD_RATE:           ovd_rate,
                FIRST_ACTIVED_DATE: val_date,
                LAST_ACTIVED_DATE:  run_date,
                CAMPAIGN_ID:        None,
                MAX_OVD_IN_MONTH:   max(dpd, prev_dpd),
                CUSTOMER_SK:        customer_sk,
                XLN_CONTRACT_SK:    contract_sk,
                COMPANY_SK:         company_sk,
                PRODUCT_SK:         product_sk,
                BUCKET_SK:          bucket_sk,
                CARD_SK:            card_sk_val,
                SALES_SK:           sale_sk,
                CUSTOMER:           customer_id,
                COMPANY_CODE:       co_code,
            })

            # ---- FCT_XLN_REPAYSCHEDULE ----
            next_repay = run_date + timedelta(days=int(next_repay_days[idx]))
            n_repay    = int(n_repay_arr[idx])
            repay_amt_batch = rng.integers(500_000, 5_000_001, size=n_repay)
            pay_bal_batch   = rng.integers(0, 10_000_001,       size=n_repay)
            freq_batch      = rng.choice(L.FREQ_CODES, size=n_repay)
            freq_code_batch = rng.choice(L.FREQ_CODES, size=n_repay)
            for ri, rtype in enumerate(rng.choice(L.REPAY_TYPES, size=n_repay, replace=False)):
                repay_rows.append({
                    DAYID:           run_date,
                    CONTRACT:        contract_id,
                    REPAYMENT_TYPE:  str(rtype),
                    REPAYMENT_DATE:  next_repay,
                    REPAYMENT_AMT:   int(repay_amt_batch[ri]),
                    REPAYMENT_ACCT:  _rid("TK"),
                    PAY_ACCT_BAL:    int(pay_bal_batch[ri]),
                    SCH_FREQ:        str(freq_batch[ri]),
                    SCH_FREQ_CODE:   str(freq_code_batch[ri]),
                    BALANCE:         balance,
                    BALANCE_PD:      balance_pd,
                    BALANCE_IN:      0,
                    BALANCE_PE:      balance_pe,
                    BALANCE_PS:      balance_ps,
                    BAL_PD_TOTAL:    total_ovd,
                    CUSTOMER_SK:     customer_sk,
                    XLN_CONTRACT_SK: contract_sk,
                    COMPANY_SK:      company_sk,
                    SALES_SK:        sale_sk,
                })

            # ---- FCT_XLN_LOAN_TXN ----
            n_txn = int(n_txn_arr[idx])
            txn_tcodes  = rng.choice(L.TRANS_CODES,   size=n_txn)
            txn_amounts = rng.integers(500_000, 10_000_001, size=n_txn)
            for ti in range(n_txn):
                tcode      = str(txn_tcodes[ti])
                txn_amount = int(txn_amounts[ti])
                txn_rows.append({
                    DAYID:             run_date,
                    CUSTOMER:          customer_id,
                    CONTRACT_MAIN:     contract_id,
                    CONTRACT:          contract_id,
                    CURRENCY:          "VND",
                    TRANS_DATE:        run_date,
                    TRANS_CODE:        tcode,
                    TRANS_AMOUNT_LCY:  txn_amount,
                    PRIN_BALANCE:      balance,
                    PRIN_OVERDUE:      balance_pd,
                    IN_OVERDUE:        0,
                    PE:                balance_pe,
                    PS:                balance_ps,
                    PE_PS:             balance_pe + balance_ps,
                    NO_DAY_OVERDUE:    dpd,
                    CO_CODE:           co_code,
                    CATEGORY:          contract_row.get(CATEGORY, "CAT01"),
                    SEAB_PRODUCTS:     None,
                    PRODUCT:           None,
                    CLASSIFICATION:    _classify(dpd),
                    SEAB_PARTNER:      None,
                    MIS_DAO:           None,
                    CURR_MIS_DAO:      None,
                    MIS_DAO1_NAME:     None,
                    CUR_MIS_DAO_NAME:  None,
                    ADDITION_CODE:     None,
                    ADDITION_VALUE:    None,
                    SALE_TYPE:         None,
                    SALE_ID:           None,
                    SALE_NAME:         None,
                    BROKER_TYPE:       None,
                    BROKER_ID:         None,
                    BROKER_NAME:       None,
                    CAMPAIGN_ID:       None,
                    SUB_PRODUCT:       None,
                    SUB_PRODUCT_NAME:  None,
                    SUB_CATEGORY:      None,
                    SUB_CATEGORY_NAME: None,
                    SOURCE:            datasource,
                    TRANS_AMOUNT:      txn_amount,
                    XLN_CONTRACT_SK:   contract_sk,
                    CONTRACT_SK:       contract_sk,
                    CUSTOMER_SK:       customer_sk,
                    COMPANY_SK:        company_sk,
                    PRODUCT_SK:        product_sk,
                    SEAB_PRODUCTS_SK:  None,
                    CATEGORY_SK:       None,
                })

            # ---- FCT_XLN_CREDIT_FEE ----
            if fee_flags[idx]:
                fee_amt = int(fee_amt_arr[idx])
                fee_rows.append({
                    DAYID:         run_date,
                    ENTRY_ID:      _rid("BT"),
                    CUSTOMER:      customer_id,
                    PL_CATEGORY:   str(pl_cat_arr[idx]),
                    TRANS_CODE:    str(fee_tcode_arr[idx]),
                    CCY:           "VND",
                    COMPANY:       co_code,
                    FEE_AMT:       fee_amt,
                    FEE_AMT_LCY:   fee_amt,
                    FEE_NAME:      str(fee_name_arr[idx]),
                    FEE_ID:        _rid("PHI", 4),
                    CUSTOMER_NAME: cust_name_map.get(customer_id, customer_id),
                    COMPANY_NAME:  co_code,
                    CUSTOMER_SK:   customer_sk,
                    COMPANY_SK:    company_sk,
                })

            # ---- FCT_XLN_BAD_DEBT (DPD >= threshold or state=BAD_DEBT) ----
            is_bad = dpd >= BAD_DEBT_DPD_THRESHOLD or new_state == "BAD_DEBT"
            if is_bad:
                bd_amt = balance + balance_pd
                bad_debt_rows.append({
                    DAYID:               run_date,
                    CONTRACT_MD:         contract_id,
                    CUSTOMER_ID:         customer_id,
                    CATEGORY:            contract_row.get(CATEGORY, "CAT01"),
                    CCY:                 "VND",
                    PRINCIPAL_AMT:       bd_amt,
                    CO_CODE:             co_code,
                    REC_STATUS:          "A",
                    VALUE_DATE:          val_date,
                    FIRST_PRINCIPAL_AMT: disb_amt,
                    CUSTOMER_SK:         str(customer_sk),   # VARCHAR2 in Oracle
                    COMPANY_SK:          str(company_sk),
                    PRODUCT_SK:          str(product_sk),
                })

                # ---- FCT_XLN_INT_WRITE_OFF ----
                if wo_flags[idx]:
                    wo_amt = int(wo_amt_arr[idx])
                    write_off_rows.append({
                        DAYID:         run_date,
                        ENTRY_ID:      _rid("BT"),
                        CUSTOMER_ID:   customer_id,
                        PL_CATEGORY:   str(wo_pl_cat_arr[idx]),
                        AMOUNT:        wo_amt,
                        AMOUNT_LCY:    wo_amt,
                        CURRENCY:      "VND",
                        NARRATIVE:     "THOAI LAI",
                        NARRATIVE_ALL: f"THOAI LAI HOP DONG {contract_id}",
                        COMPANY_CODE:  co_code,
                        CUSTOMER_NAME: cust_name_map.get(customer_id, customer_id),
                        COMPANY_NAME:  co_code,
                        CUSTOMER_SK:   customer_sk,
                        COMPANY_SK:    company_sk,
                    })

            # ---- FCT_XLN_AFTER_COB_COLLECTION ----
            if dpd > 0:
                cob_rows.append({
                    "DAYID":          run_date,
                    "MA_KHACH_HANG":  customer_id,
                    "TEN_KHACH_HANG": cust_name_map.get(customer_id, customer_id),
                    "SO_HOP_DONG":    contract_id,
                    "NGAY_MO":        val_date,
                    "DAO_HAN":        mat_date,
                    "LOAI_TIEN":      "VND",
                    "LOAI_GIAO_DICH": "OVERDUE",
                    "SO_TIEN_GIAO_DICH": total_ovd,
                    "SO_DU_HOP_DONG":    balance,
                    "MA_CHI_NHANH":   co_code,
                    "TEN_CHI_NHANH":  co_code,
                    "NGAY_GIAO_DICH": run_date,
                    "GHI_CHU":        None,
                    "SEGMENT":        None,
                    "SECTOR":         str(sector_arr[idx]),
                    "CATEGORY":       contract_row.get(CATEGORY, "CAT01"),
                    "NHOM_NH":        None, "TEN_NHOM_NH":   None,
                    "MA_NH":          None, "TEN_MA_NH":     None,
                    "MA_SPSB":        None, "TEN_MA_SPSB":   None,
                    "NHOM_NO":        _classify(dpd),
                    "GOC_QUA_HAN":    balance_pd,
                    "LAI_QUA_HAN":    balance_pe,
                    "LAI_PHAT_PE_PS": balance_pe + balance_ps,
                    "SO_NGAY_QUA_HAN": dpd,
                    "ACC_OFFICER":    None, "ACC_OFFICER_NAME": None,
                    "PORTFOLIO":      None,
                    "SEGMENT_CODE":   None, "SEGMENT_NAME":   None,
                    "CAMPAIGN_ID":    None, "CAMPAIGN_NAME":  None,
                    "SEAB_PARTNER":   None,
                    "MIS_DAO1":       None, "CURR_MIS_DAO":   None,
                    "ADDITION_CODE":  None, "ADDITION_VALUE": None,
                    "SALE_TYPE":      None, "SALE_ID":        None,
                    "SALE_NAME":      None,
                    "BROKER_TYPE":    None, "BROKER_ID":      None,
                    "BRKER_NAME":     None,
                    "CONTRACT_REF":   None,
                    "REF_VALUE_DATE": None, "REF_MAT_DATE":   None,
                    "REF_AMOUNT":     None, "REF_CURRENCY":   None,
                    "SUB_PRODUCT":    None, "SUB_NAME":       None,
                    "MIS_DAO1_NAME":  None, "CUR_MIS_DAO_NAME": None,
                    "SO_TIEN_PE":     balance_pe,
                    "SO_TIEN_PS":     balance_ps,
                })

          except Exception as exc:
            logger.error(
                "LoanGenerator [%s]: failed on contract=%s — %s",
                run_date, contract_row.get(CONTRACT, "?"), exc,
            )
            logger.debug("Contract loop error:", exc_info=True)
            raise

        return {
            "CARD":                 _df(card_rows),
            "ACTIVE_LOAN":          _df(active_loan_rows),
            "REPAYSCHEDULE":        _df(repay_rows),
            "LOAN_TXN":             _df(txn_rows),
            "CREDIT_FEE":           _df(fee_rows),
            "BAD_DEBT":             _df(bad_debt_rows),
            "INT_WRITE_OFF":        _df(write_off_rows),
            "AFTER_COB_COLLECTION": _df(cob_rows),
        }