# =============================================================================
# schema/join_map.py
# FK relationships between FCT and DIM tables.
# Source of truth: JoinMap.md (XLN_DTM Join Map FCT → DIM)
#
# Legend:
#   ✅ confirmed FK  — included as-is
#   🤖 AI-inferred   — included with comment, should be reviewed
#   ⬜ no FK data     — FCT_XLN_AFTER_COB_COLLECTION, omitted from JOIN_MAP
# =============================================================================

from __future__ import annotations
from dataclasses import dataclass
from engine.schema.columns import (
    DIM_KEY, DIM_ID, CONTRACT_ID,
    CUSTOMER_SK, CONTRACT_SK, XLN_CONTRACT_SK,
    COMPANY_SK, PRODUCT_SK, BUCKET_SK, CARD_SK, SALES_SK,
    SEAB_PRODUCTS_SK,
)


@dataclass(frozen=True)
class FKDef:
    from_table: str     # logical key of the FCT table
    fk_col: str         # FK column in from_table
    to_table: str       # logical key of the DIM table
    to_col: str         # PK column in the DIM table
    confirmed: bool = True  # False = AI-inferred, needs review


# =============================================================================
# JOIN_MAP — one entry per FK relationship
# =============================================================================

JOIN_MAP: list[FKDef] = [

    # -------------------------------------------------------------------------
    # FCT_XLN_ACTIVE_LOAN  ✅ all confirmed
    # -------------------------------------------------------------------------
    FKDef("ACTIVE_LOAN", CONTRACT_SK,  "CONTRACT", CONTRACT_ID),
    FKDef("ACTIVE_LOAN", CUSTOMER_SK,  "CUST",     DIM_KEY),
    FKDef("ACTIVE_LOAN", PRODUCT_SK,   "PRODUCT",  DIM_KEY),
    FKDef("ACTIVE_LOAN", BUCKET_SK,    "BUCKET",   DIM_ID),
    FKDef("ACTIVE_LOAN", COMPANY_SK,   "COMPANY",  DIM_KEY),
    FKDef("ACTIVE_LOAN", CARD_SK,      "CARD",     DIM_KEY),
    FKDef("ACTIVE_LOAN", SALES_SK,     "SALECODE", DIM_KEY),

    # -------------------------------------------------------------------------
    # FCT_XLN_LOAN_TXN  🤖 all AI-inferred
    # Note: FK col is XLN_CONTRACT_SK (not CONTRACT_SK) per DDD
    # -------------------------------------------------------------------------
    FKDef("LOAN_TXN", XLN_CONTRACT_SK, "CONTRACT", CONTRACT_ID, confirmed=False),
    FKDef("LOAN_TXN", CUSTOMER_SK,     "CUST",     DIM_KEY,     confirmed=False),
    FKDef("LOAN_TXN", COMPANY_SK,      "COMPANY",  DIM_KEY,     confirmed=False),
    FKDef("LOAN_TXN", PRODUCT_SK,      "PRODUCT",  DIM_KEY,     confirmed=False),
    FKDef("LOAN_TXN", SEAB_PRODUCTS_SK,"SEAB_PRODUCT", DIM_KEY, confirmed=False),  # DIM not in model yet

    # -------------------------------------------------------------------------
    # FCT_XLN_CREDIT_FEE  ✅ confirmed
    # -------------------------------------------------------------------------
    FKDef("CREDIT_FEE", COMPANY_SK,  "COMPANY", DIM_KEY),
    FKDef("CREDIT_FEE", CUSTOMER_SK, "CUST",    DIM_KEY),

    # -------------------------------------------------------------------------
    # FCT_XLN_BAD_DEBT  ✅ confirmed
    # -------------------------------------------------------------------------
    FKDef("BAD_DEBT", CUSTOMER_SK, "CUST",    DIM_KEY),
    FKDef("BAD_DEBT", COMPANY_SK,  "COMPANY", DIM_KEY),
    FKDef("BAD_DEBT", PRODUCT_SK,  "PRODUCT", DIM_KEY),

    # -------------------------------------------------------------------------
    # FCT_XLN_INT_WRITE_OFF  ✅ confirmed
    # -------------------------------------------------------------------------
    FKDef("INT_WRITE_OFF", COMPANY_SK,  "COMPANY", DIM_KEY),
    FKDef("INT_WRITE_OFF", CUSTOMER_SK, "CUST",    DIM_KEY),

    # -------------------------------------------------------------------------
    # FCT_XLN_REPAYSCHEDULE  ✅ confirmed
    # -------------------------------------------------------------------------
    FKDef("REPAYSCHEDULE", CUSTOMER_SK, "CUST",     DIM_KEY),
    FKDef("REPAYSCHEDULE", CONTRACT_SK, "CONTRACT", CONTRACT_ID),
    FKDef("REPAYSCHEDULE", COMPANY_SK,  "COMPANY",  DIM_KEY),
    FKDef("REPAYSCHEDULE", SALES_SK,    "SALECODE", DIM_KEY),

    # -------------------------------------------------------------------------
    # FCT_XLN_AFTER_COB_COLLECTION  ⬜ no FK mapping — omitted
    # FCT_XLN_LOAN_COLLECTION        ⬜ no FK mapping — omitted
    # FCT_XLN_GROUP_HIST             ⬜ no FK mapping — omitted
    # FCT_XLN_THONGTIN_TACNGHIEP     ⬜ no FK mapping — omitted
    # -------------------------------------------------------------------------
]


# =============================================================================
# Helper functions
# =============================================================================

def required_pools(logical_key: str) -> list[str]:
    """Return DIM logical keys that must be loaded before generating `logical_key`."""
    return [fk.to_table for fk in JOIN_MAP if fk.from_table == logical_key]


def fk_defs_for(logical_key: str) -> list[FKDef]:
    """Return all FKDef entries where from_table == logical_key."""
    return [fk for fk in JOIN_MAP if fk.from_table == logical_key]


def pool_columns_for(dim_logical_key: str) -> list[str]:
    """
    Return the minimal set of columns to fetch from a DIM table
    to satisfy all FK references pointing to it.
    Always includes the DIM PK column.
    """
    cols: set[str] = set()
    for fk in JOIN_MAP:
        if fk.to_table == dim_logical_key:
            cols.add(fk.to_col)
    return sorted(cols)
