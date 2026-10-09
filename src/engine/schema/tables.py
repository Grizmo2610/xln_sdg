
from __future__ import annotations
from dataclasses import dataclass
from engine.schema.columns import *


@dataclass(frozen=True)
class TableDef:
    """Immutable descriptor for one Oracle table."""

    oracle_name: str
    columns: tuple[str, ...]
    surrogate_key: str | None
    identity_cols: tuple[str, ...] = ()

    @property
    def insert_columns(self) -> tuple[str, ...]:
        excluded = set(self.identity_cols)
        return tuple(c for c in self.columns if c not in excluded)



DIM_XLN_CUST = TableDef(
    oracle_name   = "DIM_XLN_CUST",
    columns       = (
        CUST_KEY, CUSTOMER, SHORT_NAME, CUSTOMER_CLASS,
        CONTACT_DATE, PORTFOLIO,
        DISTRICT_CODE, DISTRICT_NAME, CITY_CODE, CITY_NAME,
        STATUS_DATE, EMPLOYMENT, CUSTOMER_GROUP, SEAB_CU_SEGMENT,
        SECTOR, ACCOUNT_OFFICER, ACCOUNT_OFFICER_NAME,
        EFF_DATE, EXP_DATE,
    ),
    surrogate_key = CUST_KEY,
)

DIM_XLN_CUST_PII = TableDef(
    oracle_name   = "DIM_XLN_CUST_PII",
    columns       = (
        CUST_KEY, CUSTOMER,
        DATE_OF_BIRTH, GENDER,
        LEGAL_ID, LEGAL_DOC_NAME, LEGAL_ISS_DATE,
        PHONE_T24, EMAIL_T24, ADDRESS_T24,
        SB_ID, EFF_DATE, EXP_DATE,
    ),
    surrogate_key = CUST_KEY,
)

DIM_XLN_CONTRACT = TableDef(
    oracle_name   = "DIM_XLN_CONTRACT",
    columns       = (
        CONTRACT_ID, CONTRACT, DATASOURCE, CONTRACT_REF,
        CATEGORY, CURRENCY, COLLATERAL_DESC,
        VALUE_DATE, MATURITY_DATE,
        INT_LIQ_ACCT, MORTGAGE_ACCOUNT, CHRG_LIQ_ACCT,
        SECURED, CO_CODE, REMARKS,
        FREQUENCY, FREQUENCY_DAY, FREQUENCY_PR,
        TERM, LIMIT_REF, SEAB_LOS_ID,
        REF_CONTRACT_REF, SOURCE_TYPE,
        EFF_DATE, EXP_DATE,
        CAMPAIGN_ID, REF_VALUE_DATE, REF_MAT_DATE,
        REF_CONTRACT_AMT, REF_CONTRACT_CCY,
    ),
    surrogate_key = CONTRACT_ID,
)

DIM_XLN_COMPANY = TableDef(
    oracle_name   = "DIM_XLN_COMPANY",
    columns       = (
        COMPANY_KEY, COMPANY_CODE, COMPANY_NAME,
        BRANCH_CODE, BRANCH_NAME, COMPANY_NAME_VN,
        BRANCH_CITY, BRANCH_PROVINCE,
        REGION_CODE, REGION_NAME,
        EFF_DATE, EXP_DATE,
    ),
    surrogate_key = COMPANY_KEY,
)

DIM_XLN_PRODUCT = TableDef(
    oracle_name   = "DIM_XLN_PRODUCT",
    columns       = (
        PRODUCT_KEY, PRODUCT_CODE, PRODUCT_NAME, PRODUCT_GROUP,
        EFF_DATE, EXP_DATE,
    ),
    surrogate_key = PRODUCT_KEY,
)

DIM_XLN_BUCKET = TableDef(
    oracle_name   = "DIM_XLN_BUCKET",
    columns       = (
        BUCKET_ID, OVD_NO, BUCKET_CODE, SBV_GROUP, DESCRIPTION,
        EFF_DATE, EXP_DATE,
    ),
    surrogate_key = BUCKET_ID,
)

DIM_XLN_CARD = TableDef(
    oracle_name   = "DIM_XLN_CARD",
    columns       = (
        CARD_KEY, CARD_ID, MAIN_ID,
        VALUE_DATE, CARD_STATUS, CARD_TYPE, LIMIT_DES,
        EFF_DATE, EXP_DATE,
        CUSTOMER_ID, CARD_EXPIRE, ACCOUNT_ID,
    ),
    surrogate_key = CARD_KEY,
)

DIM_XLN_SALECODE = TableDef(
    oracle_name   = "DIM_XLN_SALECODE",
    columns       = (
        SALES_KEY, SALES_ID, SALES_NAME, SALES_CONTACT,
        T24_USER_NAME, SB_ID, STATUS_DATE, EMPLOYMENT,
        EFF_DATE, EXP_DATE,
    ),
    surrogate_key = SALES_KEY,
)

DIM_XLN_LOAN_TXN_CODE = TableDef(
    oracle_name   = "DIM_XLN_LOAN_TXN_CODE",
    columns       = (
        TXN_CODE_ID, TRANS_CODE, TRANS_NAME,
        TRANS_TYPE, LOAN_TYPE, TRANS_NAME_XLN,
    ),
    surrogate_key = TXN_CODE_ID,
)

DIM_XLN_CALENDAR = TableDef(
    oracle_name   = "DIM_XLN_CALENDAR",
    columns       = (
        CAL_ID, DAYID,
        DAY, MONTH, YEAR,
        DAY_NAME, HOLIDAY,
        NO_DAY_MTD, NO_DAY_YTD,
        LAST_DAY_OF_MONTH, NO_DAY_OF_MONTH,
        NO_DAY_OF_QUARTER, NO_DAY_OF_YEAR,
    ),
    surrogate_key = CAL_ID,
)



FCT_XLN_ACTIVE_LOAN = TableDef(
    oracle_name   = "FCT_XLN_ACTIVE_LOAN",
    columns       = (
        DAYID, CONTRACT, PD_CONTRACT,
        DISBURSEMENT_AMT, NO_DAYS_OVERDUE, PD_NO,
        BALANCE, BALANCE_PD, BALANCE_IN, BALANCE_PE, BALANCE_PS,
        TOTAL_BALANCE, TOTAL_EXPOSURE, TOTAL_OVD,
        DEBT_SETTLEMENT, BOM_DPD, YESTERDAY_DPD, MAX_OVD,
        INTEREST, OVD_RATE,
        FIRST_ACTIVED_DATE, LAST_ACTIVED_DATE,
        CAMPAIGN_ID, MAX_OVD_IN_MONTH,
        # FK columns
        CUSTOMER_SK, XLN_CONTRACT_SK, COMPANY_SK, PRODUCT_SK,
        BUCKET_SK, CARD_SK, SALES_SK,
    ),
    surrogate_key = None,
)

FCT_XLN_REPAYSCHEDULE = TableDef(
    oracle_name   = "FCT_XLN_REPAYSCHEDULE",
    columns       = (
        DAYID, CONTRACT, REPAYMENT_TYPE, REPAYMENT_DATE, REPAYMENT_AMT,
        REPAYMENT_ACCT, PAY_ACCT_BAL,
        SCH_FREQ, SCH_FREQ_CODE,
        BALANCE, BALANCE_PD, BALANCE_IN, BALANCE_PE, BALANCE_PS, BAL_PD_TOTAL,
        # FK columns
        CUSTOMER_SK, XLN_CONTRACT_SK, COMPANY_SK, SALES_SK,
    ),
    surrogate_key = None,
)

FCT_XLN_LOAN_TXN = TableDef(
    oracle_name   = "FCT_XLN_LOAN_TXN",
    columns       = (
        DAYID, CUSTOMER, CONTRACT_MAIN, CONTRACT, CURRENCY,
        TRANS_DATE, TRANS_CODE, TRANS_AMOUNT_LCY,
        PRIN_BALANCE, PRIN_OVERDUE, IN_OVERDUE, PE, PS, PE_PS,
        NO_DAY_OVERDUE, CO_CODE, CATEGORY, SEAB_PRODUCTS, PRODUCT,
        CLASSIFICATION, SEAB_PARTNER, MIS_DAO, CURR_MIS_DAO,
        MIS_DAO1_NAME, CUR_MIS_DAO_NAME,
        ADDITION_CODE, ADDITION_VALUE,
        SALE_TYPE, SALE_ID, SALE_NAME,
        BROKER_TYPE, BROKER_ID, BROKER_NAME,
        CAMPAIGN_ID, SUB_PRODUCT, SUB_PRODUCT_NAME,
        SUB_CATEGORY, SUB_CATEGORY_NAME,
        SOURCE, TRANS_AMOUNT,
        # FK columns
        XLN_CONTRACT_SK, CUSTOMER_SK, COMPANY_SK, PRODUCT_SK, SEAB_PRODUCTS_SK,
    ),
    surrogate_key = None,
)

FCT_XLN_CREDIT_FEE = TableDef(
    oracle_name   = "FCT_XLN_CREDIT_FEE",
    columns       = (
        DAYID, ENTRY_ID, CUSTOMER, PL_CATEGORY, TRANS_CODE,
        CCY, COMPANY, FEE_AMT, FEE_AMT_LCY, FEE_NAME, FEE_ID,
        CUSTOMER_NAME, COMPANY_NAME,
        # FK columns
        CUSTOMER_SK, COMPANY_SK,
    ),
    surrogate_key = None,
)

FCT_XLN_BAD_DEBT = TableDef(
    oracle_name   = "FCT_XLN_BAD_DEBT",
    columns       = (
        DAYID, CONTRACT_MD, CUSTOMER_ID, CATEGORY, CCY,
        PRINCIPAL_AMT, CO_CODE, REC_STATUS, VALUE_DATE,
        FIRST_PRINCIPAL_AMT,
        # FK columns
        CUSTOMER_SK, COMPANY_SK, PRODUCT_SK,
    ),
    surrogate_key = None,
)

FCT_XLN_INT_WRITE_OFF = TableDef(
    oracle_name   = "FCT_XLN_INT_WRITE_OFF",
    columns       = (
        DAYID, ENTRY_ID, CUSTOMER_ID, PL_CATEGORY,
        AMOUNT, AMOUNT_LCY, CURRENCY, NARRATIVE, NARRATIVE_ALL,
        COMPANY_CODE, CUSTOMER_NAME, COMPANY_NAME,
        # FK columns
        CUSTOMER_SK, COMPANY_SK,
    ),
    surrogate_key = None,
)

# FCT_XLN_AFTER_COB_COLLECTION uses Vietnamese column names from the DDL.
# This table is denormalized (no FK surrogates) — columns are raw strings
# matching the actual Oracle DDL (ddd.md § 6.2.7).
# Only the subset used by LoanGenerator is listed; extend as needed.
_COB_DAYID          = "DAYID"
_COB_MA_KH          = "MA_KHACH_HANG"
_COB_TEN_KH         = "TEN_KHACH_HANG"
_COB_SO_HD          = "SO_HOP_DONG"
_COB_NGAY_MO        = "NGAY_MO"
_COB_DAO_HAN        = "DAO_HAN"
_COB_LOAI_TIEN      = "LOAI_TIEN"
_COB_LOAI_GD        = "LOAI_GIAO_DICH"
_COB_SO_TIEN_GD     = "SO_TIEN_GIAO_DICH"
_COB_CATEGORY       = "CATEGORY"
_COB_SECTOR         = "SECTOR"
_COB_SEAB_PARTNER   = "SEAB_PARTNER"
_COB_CAMPAIGN_ID    = "CAMPAIGN_ID"
_COB_CONTRACT_REF   = "CONTRACT_REF"
_COB_REF_VALUE_DATE = "REF_VALUE_DATE"
_COB_REF_MAT_DATE   = "REF_MAT_DATE"

FCT_XLN_AFTER_COB_COLLECTION = TableDef(
    oracle_name   = "FCT_XLN_AFTER_COB_COLLECTION",
    columns       = (
        _COB_DAYID, _COB_MA_KH, _COB_TEN_KH,
        _COB_SO_HD, _COB_NGAY_MO, _COB_DAO_HAN,
        _COB_LOAI_TIEN, _COB_CATEGORY, _COB_SECTOR,
        _COB_SEAB_PARTNER, _COB_CAMPAIGN_ID,
        _COB_CONTRACT_REF, _COB_REF_VALUE_DATE, _COB_REF_MAT_DATE,
        # no FK surrogate columns — ⬜ in JoinMap
    ),
    surrogate_key = None,
)



REGISTRY: dict[str, TableDef] = {
    # DIM
    "CUST":             DIM_XLN_CUST,
    "CUST_PII":         DIM_XLN_CUST_PII,
    "CONTRACT":         DIM_XLN_CONTRACT,
    "COMPANY":          DIM_XLN_COMPANY,
    "PRODUCT":          DIM_XLN_PRODUCT,
    "BUCKET":           DIM_XLN_BUCKET,
    "CARD":             DIM_XLN_CARD,
    "SALECODE":         DIM_XLN_SALECODE,
    "CALENDAR":         DIM_XLN_CALENDAR,
    "LOAN_TXN_CODE":    DIM_XLN_LOAN_TXN_CODE,
    # FCT
    "ACTIVE_LOAN":          FCT_XLN_ACTIVE_LOAN,
    "REPAYSCHEDULE":        FCT_XLN_REPAYSCHEDULE,
    "LOAN_TXN":             FCT_XLN_LOAN_TXN,
    "CREDIT_FEE":           FCT_XLN_CREDIT_FEE,
    "BAD_DEBT":             FCT_XLN_BAD_DEBT,
    "INT_WRITE_OFF":        FCT_XLN_INT_WRITE_OFF,
    "AFTER_COB_COLLECTION": FCT_XLN_AFTER_COB_COLLECTION,
}

DIM_TABLES = {k for k, v in REGISTRY.items() if v.surrogate_key is not None}
FCT_TABLES = {k for k, v in REGISTRY.items() if v.surrogate_key is None}


def get(logical_key: str) -> TableDef:
    """Look up a TableDef by logical key. Raises KeyError with a clear message."""
    try:
        return REGISTRY[logical_key]
    except KeyError:
        valid = ", ".join(sorted(REGISTRY))
        raise KeyError(
            f"Unknown table key '{logical_key}'. Valid keys: {valid}"
        ) from None
