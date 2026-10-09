from __future__ import annotations
from dataclasses import dataclass
from engine.schema.columns import (
    DIM_KEY, DIM_ID, CONTRACT_ID,
    CUSTOMER_SK, CONTRACT_SK, XLN_CONTRACT_SK,
    COMPANY_SK, PRODUCT_SK, BUCKET_SK, CARD_SK, SALES_SK,
    SEAB_PRODUCTS_SK,
    CUSTOMER, SHORT_NAME, CONTRACT, COMPANY_CODE, PRODUCT_CODE, DATASOURCE, CO_CODE,
    CATEGORY, VALUE_DATE, MATURITY_DATE, SOURCE_TYPE,
)


@dataclass(frozen=True)
class FKDef:
    from_table: str
    fk_col: str
    to_table: str
    to_col: str
    confirmed: bool = True  # False = AI-inferred, needs review


JOIN_MAP: list[FKDef] = [
    # FCT_XLN_ACTIVE_LOAN
    FKDef("ACTIVE_LOAN", XLN_CONTRACT_SK, "CONTRACT",  CONTRACT_ID),
    FKDef("ACTIVE_LOAN", CUSTOMER_SK,     "CUST",      DIM_KEY),
    FKDef("ACTIVE_LOAN", PRODUCT_SK,      "PRODUCT",   DIM_KEY),
    FKDef("ACTIVE_LOAN", BUCKET_SK,       "BUCKET",    DIM_ID),
    FKDef("ACTIVE_LOAN", COMPANY_SK,      "COMPANY",   DIM_KEY),
    FKDef("ACTIVE_LOAN", CARD_SK,         "CARD",      DIM_KEY),
    FKDef("ACTIVE_LOAN", SALES_SK,        "SALECODE",  DIM_KEY),

    # FCT_XLN_LOAN_TXN  (AI-inferred)
    FKDef("LOAN_TXN", XLN_CONTRACT_SK,  "CONTRACT",    CONTRACT_ID, confirmed=False),
    FKDef("LOAN_TXN", CUSTOMER_SK,      "CUST",        DIM_KEY,     confirmed=False),
    FKDef("LOAN_TXN", COMPANY_SK,       "COMPANY",     DIM_KEY,     confirmed=False),
    FKDef("LOAN_TXN", PRODUCT_SK,       "PRODUCT",     DIM_KEY,     confirmed=False),
    FKDef("LOAN_TXN", SEAB_PRODUCTS_SK, "SEAB_PRODUCT",DIM_KEY,     confirmed=False),

    # FCT_XLN_CREDIT_FEE
    FKDef("CREDIT_FEE", COMPANY_SK,  "COMPANY", DIM_KEY),
    FKDef("CREDIT_FEE", CUSTOMER_SK, "CUST",    DIM_KEY),

    # FCT_XLN_BAD_DEBT
    FKDef("BAD_DEBT", CUSTOMER_SK, "CUST",    DIM_KEY),
    FKDef("BAD_DEBT", COMPANY_SK,  "COMPANY", DIM_KEY),
    FKDef("BAD_DEBT", PRODUCT_SK,  "PRODUCT", DIM_KEY),

    # FCT_XLN_INT_WRITE_OFF
    FKDef("INT_WRITE_OFF", COMPANY_SK,  "COMPANY", DIM_KEY),
    FKDef("INT_WRITE_OFF", CUSTOMER_SK, "CUST",    DIM_KEY),

    # FCT_XLN_REPAYSCHEDULE
    FKDef("REPAYSCHEDULE", CUSTOMER_SK,    "CUST",     DIM_KEY),
    FKDef("REPAYSCHEDULE", XLN_CONTRACT_SK,"CONTRACT", CONTRACT_ID),
    FKDef("REPAYSCHEDULE", COMPANY_SK,     "COMPANY",  DIM_KEY),
    FKDef("REPAYSCHEDULE", SALES_SK,       "SALECODE", DIM_KEY),

    # FCT_XLN_AFTER_COB_COLLECTION, FCT_XLN_LOAN_COLLECTION,
    # FCT_XLN_GROUP_HIST, FCT_XLN_THONGTIN_TACNGHIEP — no FK mapping
]


def required_pools(logical_key: str) -> list[str]:
    """Return DIM logical keys that must be loaded before generating `logical_key`."""
    return [fk.to_table for fk in JOIN_MAP if fk.from_table == logical_key]


def fk_defs_for(logical_key: str) -> list[FKDef]:
    """Return all FKDef entries where from_table == logical_key."""
    return [fk for fk in JOIN_MAP if fk.from_table == logical_key]


# BUCKET pool needs OVD_NO beyond the PK for DPD→bucket_sk lookup.
BUCKET_POOL_COLS: list[str] = ["DIMENSION_ID", "OVD_NO"]

EXTRA_POOL_COLS: dict[str, list[str]] = {
    "CUST":     [CUSTOMER, SHORT_NAME],
    "CONTRACT": [CONTRACT, DATASOURCE, CO_CODE, CATEGORY,
                 VALUE_DATE, MATURITY_DATE, SOURCE_TYPE],
    "COMPANY":  [COMPANY_CODE],
    "PRODUCT":  [PRODUCT_CODE],
}


def pool_columns_for(dim_logical_key: str) -> list[str]:
    """Return the minimal column set to fetch for a DIM pool."""
    if dim_logical_key == "BUCKET":
        return BUCKET_POOL_COLS
    cols: set[str] = set()
    for fk in JOIN_MAP:
        if fk.to_table == dim_logical_key:
            cols.add(fk.to_col)
    cols.update(EXTRA_POOL_COLS.get(dim_logical_key, []))
    return sorted(cols)
