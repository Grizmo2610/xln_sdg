"""
config/propensity.py
All probability rates and volumetry ratios.

Structure:
  RATIOS            — seed-time: multiplied by INIT_CUSTOMERS → total DIM rows
  DAILY_RATES       — daily run: fixed count per day (before noise)
  SCD2_RATIO        — daily churn rate per active pool size
  HIST_RATE         — % of seed records that are historical (closed) vs active
  HAZARD            — loan state-transition probabilities (daily)
  FEE_RATE          — % of contracts that generate a credit fee row per day
  WRITE_OFF_RATE    — % of bad-debt contracts that generate a write-off row per day
  COB_RATE          — % of overdue contracts that appear in AFTER_COB_COLLECTION per day
  CITY_WEIGHTS      — sampling weights for CITY_LIST (customer geography)
  FEMALE_RATIO      — female fraction for gender sampling
  DATASOURCE_WEIGHTS— weights for DATASOURCES list
  SOURCE_TYPE_WEIGHTS—weights for SOURCE_TYPES list
  CONTRACT_COUNT_POOL— pool for sampling contracts-per-customer count

Monthly overrides:
  Each MONTHLY_OVERRIDES[month] is a flat dict of any key above.
  month = 1..12.  Missing keys fall back to the base value.
  Use get_monthly(month) to get the effective merged config for a given month.
  TODO: fill after analysing live portfolio data.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Volumetry — seed
# RATIOS[table] * INIT_CUSTOMERS = base row count at seed time
# ---------------------------------------------------------------------------
RATIOS: dict[str, float] = {
    "DIM_XLN_CUST":     1.0,       # 1 customer per anchor unit
    "DIM_XLN_CONTRACT": 1.4,       # ~1.4 contracts per customer (82/11/7 dist)
    "DIM_XLN_CARD":     0.3,       # ~30% of contracts are VS (card-backed)
}

# ---------------------------------------------------------------------------
# Volumetry — daily
# DAILY_RATES[table] = base row count per day (before noise)
# ---------------------------------------------------------------------------
DAILY_RATES: dict[str, int] = {
    "DIM_XLN_CUST":     20,    # new customers per day
    "DIM_XLN_CONTRACT": 28,    # new contracts per day (~1.4 × 20)
    "FCT_XLN_LOAN_TXN": 0,     # driven by contract pool — not a fixed count
}

# ---------------------------------------------------------------------------
# SCD2 daily churn rates
# churn_count = floor(SCD2_RATIO[table] * active_pool_size)
# ---------------------------------------------------------------------------
SCD2_RATIO: dict[str, float] = {
    "DIM_XLN_SALECODE": 0.002,   # ~0.2% of sales staff churns per day
    "DIM_XLN_CUST":     0.001,   # ~0.1% customer records get a new SCD2 version
}

# ---------------------------------------------------------------------------
# Historical rate at seed time
# HIST_RATE[table] = fraction of seed records that are already closed
# ---------------------------------------------------------------------------
HIST_RATE: dict[str, float] = {
    "DIM_XLN_SALECODE": 0.15,   # 15% of seeded staff already resigned
    "DIM_XLN_CUST":     0.05,   # 5% of seeded customers already expired
}

# ---------------------------------------------------------------------------
# Hazard model — daily loan state-transition probabilities
# States: NORMAL → OVERDUE → BAD_DEBT → (SETTLED terminal)
# All values are daily probabilities (not annual).
# ---------------------------------------------------------------------------
HAZARD: dict[str, float] = {
    "p_prepay":       0.001,
    "p_default":      0.005,
    "p_cure":         0.15,
    "p_worsen":       0.05,
    "interest_min":   0.06,
    "interest_max":   0.18,
    "ovd_rate_min":   0.15,
    "ovd_rate_max":   0.24,
    "pe_per_day_min": 0,
    "pe_per_day_max": 50_000,
    "ps_per_day_min": 0,
    "ps_per_day_max": 30_000,
}

# ---------------------------------------------------------------------------
# FCT row emission rates (per contract per day)
# ---------------------------------------------------------------------------

# Fraction of contracts that generate a CREDIT_FEE row each day
FEE_RATE: float = 0.40

# Fraction of bad-debt contracts that generate an INT_WRITE_OFF row each day
WRITE_OFF_RATE: float = 0.20

# Fraction of overdue contracts that appear in AFTER_COB_COLLECTION per day
COB_RATE: float = 1.0

# ---------------------------------------------------------------------------
# City sampling weights for new customers
# Order matches CITY_LIST in listchoice.py
# ---------------------------------------------------------------------------
CITY_WEIGHTS: list[float] = [
    0.20,  # HN  Hoan Kiem
    0.15,  # HN  Dong Da
    0.10,  # HN  Cau Giay
    0.15,  # HCM Quan 1
    0.10,  # HCM Binh Thanh
    0.08,  # HCM Thu Duc
    0.07,  # DN  Hai Chau
    0.07,  # HP  Le Chan
    0.08,  # CT  Ninh Kieu
]

# Female ratio for gender sampling
FEMALE_RATIO: float = 0.45

# ---------------------------------------------------------------------------
# Datasource / source_type weights for new contracts
# Aligned to DATASOURCES in listchoice.py: ["LD","MG","PD","AC","VS"]
# Aligned to SOURCE_TYPES in listchoice.py: ["LOAN","MD","CC"]
# ---------------------------------------------------------------------------
DATASOURCE_WEIGHTS: list[float] = [0.40, 0.20, 0.15, 0.10, 0.15]
SOURCE_TYPE_WEIGHTS: list[float] = [0.60, 0.20, 0.20]

# ---------------------------------------------------------------------------
# Contract count per customer pool
# 82% 1 contract, 11% 2 contracts, 7% 3 contracts
# Represented as a pool to sample from (8×1 + 2×2 + 1×3)
# ---------------------------------------------------------------------------
CONTRACT_COUNT_POOL: list[int] = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3]

# ---------------------------------------------------------------------------
# Monthly overrides
# Keys mirror any scalar / list / dict above.
# Missing key → falls back to base value.
# TODO: fill after analysing live portfolio data.
#
# Example:
#   1: {                                # January — Tet effect
#       "p_default":      0.008,        # higher default
#       "p_cure":         0.10,         # lower cure
#       "DAILY_RATES":    {"DIM_XLN_CUST": 15, "DIM_XLN_CONTRACT": 21},
#       "FEMALE_RATIO":   0.45,
#       "CONTRACT_COUNT_POOL": [1,1,1,1,1,1,1,2,2,3],
#   },
# ---------------------------------------------------------------------------
MONTHLY_OVERRIDES: dict[int, dict] = {
    # 1:  {"p_default": 0.008, "p_cure": 0.10},
    # 2:  {},
    # 3:  {},
    # 4:  {},
    # 5:  {},
    # 6:  {},
    # 7:  {"p_cure": 0.12},
    # 8:  {},
    # 9:  {},
    # 10: {},
    # 11: {},
    # 12: {"p_default": 0.007},
}


def get_monthly(month: int) -> dict:
    """
    Return the effective merged config for a given month (1–12).

    Returns a flat dict with all keys from this module, with any
    MONTHLY_OVERRIDES[month] values merged on top.

    Keys included:
      hazard keys (p_prepay, p_default, p_cure, p_worsen, interest_*, ovd_rate_*, pe/ps_*)
      FEE_RATE, WRITE_OFF_RATE, COB_RATE
      FEMALE_RATIO
      DATASOURCE_WEIGHTS, SOURCE_TYPE_WEIGHTS
      CONTRACT_COUNT_POOL
      CITY_WEIGHTS
      DAILY_RATES  (dict — merged shallowly per override key)
      SCD2_RATIO   (dict — merged shallowly)

    Usage in generators:
        cfg = prop.get_monthly(run_date.month)
        fee_flags = rng.random(n) < cfg["FEE_RATE"]
        hazard_p_default = cfg["p_default"]
        daily_custs = cfg["DAILY_RATES"]["DIM_XLN_CUST"]
    """
    overrides = MONTHLY_OVERRIDES.get(month, {})

    # Base flat config — hazard keys promoted to top level for convenience
    base: dict = {
        **HAZARD,
        "FEE_RATE":             FEE_RATE,
        "WRITE_OFF_RATE":       WRITE_OFF_RATE,
        "COB_RATE":             COB_RATE,
        "FEMALE_RATIO":         FEMALE_RATIO,
        "DATASOURCE_WEIGHTS":   list(DATASOURCE_WEIGHTS),
        "SOURCE_TYPE_WEIGHTS":  list(SOURCE_TYPE_WEIGHTS),
        "CONTRACT_COUNT_POOL":  list(CONTRACT_COUNT_POOL),
        "CITY_WEIGHTS":         list(CITY_WEIGHTS),
        "DAILY_RATES":          dict(DAILY_RATES),
        "SCD2_RATIO":           dict(SCD2_RATIO),
    }

    # Apply overrides — dict values are shallow-merged, scalars/lists replaced
    for key, val in overrides.items():
        if key in ("DAILY_RATES", "SCD2_RATIO") and isinstance(val, dict):
            base[key] = {**base[key], **val}
        else:
            base[key] = val

    return base


# ---------------------------------------------------------------------------
# Backwards-compat alias — existing callers of get_hazard() still work
# ---------------------------------------------------------------------------
def get_hazard(month: int) -> dict[str, float]:
    """Return effective hazard params for a given month (subset of get_monthly)."""
    cfg = get_monthly(month)
    return {k: cfg[k] for k in HAZARD}
