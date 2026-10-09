from __future__ import annotations

from engine.config import weights as _W

RATIOS: dict[str, float] = {
    "DIM_XLN_CUST":     1.0,       # 1 customer per anchor unit
    "DIM_XLN_CONTRACT": 1.4,       # ~1.4 contracts per customer (82/11/7 dist)
    "DIM_XLN_CARD":     0.3,       # ~30% of contracts are VS (card-backed)
}

DAILY_RATES: dict[str, int] = {
    "DIM_XLN_CUST":     20,    # new customers per day
    "DIM_XLN_CONTRACT": 28,    # new contracts per day (~1.4 × 20)
    "FCT_XLN_LOAN_TXN": 0,     # driven by contract pool — not a fixed count
}

SCD2_RATIO: dict[str, float] = {
    "DIM_XLN_SALECODE": 0.002,   # ~0.2% of sales staff churns per day
    "DIM_XLN_CUST":     0.001,   # ~0.1% customer records get a new SCD2 version
}

HIST_RATE: dict[str, float] = {
    "DIM_XLN_SALECODE": 0.15,   # 15% of seeded staff already resigned
    "DIM_XLN_CUST":     0.05,   # 5% of seeded customers already expired
}

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

# Fraction of contracts that generate a CREDIT_FEE row each day
FEE_RATE: float = 0.40

# Fraction of bad-debt contracts that generate an INT_WRITE_OFF row each day
WRITE_OFF_RATE: float = 0.20

# Fraction of overdue contracts that appear in AFTER_COB_COLLECTION per day
COB_RATE: float = 1.0

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

DATASOURCE_WEIGHTS: list[float] = [0.0383, 0.0001, 0.2528, 0.0824, 0.5251, 0.1013]  # avg across 12 months from s4
SOURCE_TYPE_WEIGHTS: list[float] = [0.7915, 0.2085]  # avg across 12 months from s4

CONTRACT_COUNT_POOL: list[int] = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3]

# Monthly overrides
# Keys mirror any scalar / list / dict above.
# Missing key → falls back to base value.
#
# Example:
#   1: {                                # January — Tet effect
#       "p_default":      0.008,        # higher default
#       "p_cure":         0.10,         # lower cure
#       "DAILY_RATES":    {"DIM_XLN_CUST": 15, "DIM_XLN_CONTRACT": 21},
#       "FEMALE_RATIO":   0.45,
#       "CONTRACT_COUNT_POOL": [1,1,1,1,1,1,1,2,2,3],
#   },
MONTHLY_OVERRIDES: dict[int, dict] = {
    1: {  # January
        "DAILY_RATES": {
            "DIM_XLN_CUST": 4399,
            "DIM_XLN_CONTRACT": 1687,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3],
        "p_default": 0.012709,
        "p_cure": 0.101532,
        "p_worsen": 0.002712,
        "p_prepay": 1.5e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 52.5,
        "pe_per_day_min": 226.0,
        "pe_per_day_max": 128154.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 15781.0,
        "FEE_RATE": 0.0001,
        "WRITE_OFF_RATE": 0.0002,
        "COB_RATE": 0.0789,
        "SOURCE_TYPE_WEIGHTS": [0.8761, 0.1239],
        "FEMALE_RATIO": 0.5205,
        # array weights → see engine/config/weights.py
    },
    2: {  # February
        "DAILY_RATES": {
            "DIM_XLN_CUST": 3706,
            "DIM_XLN_CONTRACT": 1308,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3],
        "p_default": 0.013714,
        "p_cure": 0.128984,
        "p_worsen": 0.002693,
        "p_prepay": 2.7e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 143.0,
        "pe_per_day_max": 129031.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 15845.0,
        "FEE_RATE": 0.0002,
        "WRITE_OFF_RATE": 0.0002,
        "COB_RATE": 0.0975,
        "SOURCE_TYPE_WEIGHTS": [0.9042, 0.0958],
        "FEMALE_RATIO": 0.5539,
        # array weights → see engine/config/weights.py
    },
    3: {  # March
        "DAILY_RATES": {
            "DIM_XLN_CUST": 3392,
            "DIM_XLN_CONTRACT": 1572,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3],
        "p_default": 0.012533,
        "p_cure": 0.116318,
        "p_worsen": 0.002707,
        "p_prepay": 2.1e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 248.0,
        "pe_per_day_max": 130870.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 16339.0,
        "FEE_RATE": 0.0002,
        "WRITE_OFF_RATE": 0.0003,
        "COB_RATE": 0.0836,
        "SOURCE_TYPE_WEIGHTS": [0.8596, 0.1404],
        "FEMALE_RATIO": 0.512,
        # array weights → see engine/config/weights.py
    },
    4: {  # April
        "DAILY_RATES": {
            "DIM_XLN_CUST": 4441,
            "DIM_XLN_CONTRACT": 1625,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3],
        "p_default": 0.012398,
        "p_cure": 0.11922,
        "p_worsen": 0.003055,
        "p_prepay": 2.4e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 279.0,
        "pe_per_day_max": 132611.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 16628.0,
        "FEE_RATE": 0.0002,
        "WRITE_OFF_RATE": 0.0002,
        "COB_RATE": 0.0894,
        "SOURCE_TYPE_WEIGHTS": [0.8503, 0.1497],
        "FEMALE_RATIO": 0.4656,
        # array weights → see engine/config/weights.py
    },
    5: {  # May
        "DAILY_RATES": {
            "DIM_XLN_CUST": 3895,
            "DIM_XLN_CONTRACT": 1556,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3],
        "p_default": 0.011932,
        "p_cure": 0.113774,
        "p_worsen": 0.002467,
        "p_prepay": 2.7e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 309.0,
        "pe_per_day_max": 134046.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 16996.0,
        "FEE_RATE": 0.0002,
        "WRITE_OFF_RATE": 0.0002,
        "COB_RATE": 0.0851,
        "SOURCE_TYPE_WEIGHTS": [0.8613, 0.1387],
        "FEMALE_RATIO": 0.3785,
        # array weights → see engine/config/weights.py
    },
    6: {  # June
        "DAILY_RATES": {
            "DIM_XLN_CUST": 3613,
            "DIM_XLN_CONTRACT": 1884,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3],
        "p_default": 0.012181,
        "p_cure": 0.126563,
        "p_worsen": 0.004432,
        "p_prepay": 2.5e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 350.0,
        "pe_per_day_max": 135660.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 17430.0,
        "FEE_RATE": 0.0002,
        "WRITE_OFF_RATE": 0.0002,
        "COB_RATE": 0.0883,
        "SOURCE_TYPE_WEIGHTS": [0.7902, 0.2098],
        "FEMALE_RATIO": 0.378,
        # array weights → see engine/config/weights.py
    },
    7: {  # July
        "DAILY_RATES": {
            "DIM_XLN_CUST": 2741,
            "DIM_XLN_CONTRACT": 1456,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3],
        "p_default": 0.012031,
        "p_cure": 0.132597,
        "p_worsen": 0.003097,
        "p_prepay": 1.9e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 362.0,
        "pe_per_day_max": 136988.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 17522.0,
        "FEE_RATE": 0.0002,
        "WRITE_OFF_RATE": 0.0001,
        "COB_RATE": 0.0859,
        "SOURCE_TYPE_WEIGHTS": [0.8696, 0.1304],
        "FEMALE_RATIO": 0.4063,
        # array weights → see engine/config/weights.py
    },
    8: {  # August
        "DAILY_RATES": {
            "DIM_XLN_CUST": 4129,
            "DIM_XLN_CONTRACT": 2683,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3],
        "p_default": 0.012173,
        "p_cure": 0.120301,
        "p_worsen": 0.002766,
        "p_prepay": 2.3e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 348.0,
        "pe_per_day_max": 137831.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 17214.0,
        "FEE_RATE": 0.0002,
        "WRITE_OFF_RATE": 0.0002,
        "COB_RATE": 0.0913,
        "SOURCE_TYPE_WEIGHTS": [0.834, 0.166],
        "FEMALE_RATIO": 0.364,
        # array weights → see engine/config/weights.py
    },
    9: {  # September
        "DAILY_RATES": {
            "DIM_XLN_CUST": 3626,
            "DIM_XLN_CONTRACT": 3278,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        "p_default": 0.01472,
        "p_cure": 0.057345,
        "p_worsen": 0.001212,
        "p_prepay": 2.8e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 428.0,
        "pe_per_day_max": 130639.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 12920.0,
        "FEE_RATE": 0.0002,
        "WRITE_OFF_RATE": 0.0002,
        "COB_RATE": 0.074,
        "SOURCE_TYPE_WEIGHTS": [0.8659, 0.1341],
        "FEMALE_RATIO": 0.3632,
        # array weights → see engine/config/weights.py
    },
    10: {  # October
        "DAILY_RATES": {
            "DIM_XLN_CUST": 3229,
            "DIM_XLN_CONTRACT": 2583,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3],
        "p_default": 0.013571,
        "p_cure": 0.036269,
        "p_worsen": 0.000794,
        "p_prepay": 2.5e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 544.0,
        "pe_per_day_max": 121648.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 9646.0,
        "FEE_RATE": 0.0002,
        "WRITE_OFF_RATE": 0.0002,
        "COB_RATE": 0.0568,
        "SOURCE_TYPE_WEIGHTS": [0.8014, 0.1986],
        "FEMALE_RATIO": 0.5212,
        # array weights → see engine/config/weights.py
    },
    11: {  # November
        "DAILY_RATES": {
            "DIM_XLN_CUST": 2386,
            "DIM_XLN_CONTRACT": 2863,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3],
        "p_default": 0.012667,
        "p_cure": 0.030437,
        "p_worsen": 0.001455,
        "p_prepay": 2.1e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 621.0,
        "pe_per_day_max": 119232.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 9032.0,
        "FEE_RATE": 0.0001,
        "WRITE_OFF_RATE": 0.0002,
        "COB_RATE": 0.0507,
        "SOURCE_TYPE_WEIGHTS": [0.5057, 0.4943],
        "FEMALE_RATIO": 0.55,
        # array weights → see engine/config/weights.py
    },
    12: {  # December
        "DAILY_RATES": {
            "DIM_XLN_CUST": 2817,
            "DIM_XLN_CONTRACT": 3169,
        },
        "CONTRACT_COUNT_POOL": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3],
        "p_default": 0.011517,
        "p_cure": 0.045995,
        "p_worsen": 0.022794,
        "p_prepay": 2.6e-05,
        "interest_min": 0.0,
        "interest_max": 34.0,
        "ovd_rate_min": 10.05,
        "ovd_rate_max": 51.0,
        "pe_per_day_min": 645.0,
        "pe_per_day_max": 120754.0,
        "ps_per_day_min": 0.0,
        "ps_per_day_max": 9286.0,
        "FEE_RATE": 0.0001,
        "WRITE_OFF_RATE": 0.0003,
        "COB_RATE": 0.0542,
        "SOURCE_TYPE_WEIGHTS": [0.4798, 0.5202],
        "FEMALE_RATIO": 0.5676,
        # array weights → see engine/config/weights.py
    },
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
        "DATASOURCE_WEIGHTS":   list(_W.DATASOURCE_WEIGHTS[month]),
        "SOURCE_TYPE_WEIGHTS":  list(SOURCE_TYPE_WEIGHTS),
        "CARD_TYPE_WEIGHTS":    list(_W.CARD_TYPE_WEIGHTS[month]),
        "CONTRACT_COUNT_POOL":  list(CONTRACT_COUNT_POOL),
        "CITY_WEIGHTS":         list(_W.CITY_WEIGHTS[month]),
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

def get_hazard(month: int) -> dict[str, float]:
    """Return effective hazard params for a given month (subset of get_monthly)."""
    cfg = get_monthly(month)
    return {k: cfg[k] for k in HAZARD}