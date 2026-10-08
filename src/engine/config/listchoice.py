"""
config/listchoice.py
All categorical lookup lists and maps used by generators.
Edit here — never hardcode strings in generators.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Geography
# ---------------------------------------------------------------------------

# city_code → city display name (ASCII uppercase for T24)
CITY_NAMES: dict[str, str] = {
    "HN":    "HA NOI",
    "HCM":   "HO CHI MINH",
    "HP":    "HAI PHONG",
    "DN":    "DA NANG",
    "CT":    "CAN THO",
    "BD":    "BINH DUONG",
    "BH":    "BIEN HOA",
    "LA":    "LONG AN",
    "TN":    "THAI NGUYEN",
    "VT":    "VUNG TAU",
    "HUE":   "HUE",
    "OTHER": "OTHER",
}

# city_code → {district_code: district_name}
CITY_DISTRICT_MAP: dict[str, dict[str, str]] = {
    "HN": {
        "Q01": "HOAN KIEM",
        "Q02": "TAY HO",
        "Q03": "DONG DA",
        "Q04": "HAI BA TRUNG",
        "Q05": "BA DINH",
        "Q06": "CAU GIAY",
        "Q07": "THANH XUAN",
        "Q08": "HOANG MAI",
        "Q09": "LONG BIEN",
        "Q10": "HA DONG",
    },
    "HCM": {
        "Q01": "QUAN 1",
        "Q03": "QUAN 3",
        "Q05": "QUAN 5",
        "Q07": "QUAN 7",
        "Q10": "QUAN 10",
        "QBT": "BINH THANH",
        "QGV": "GO VAP",
        "QPH": "PHU NHUAN",
        "QTD": "THU DUC",
        "QBT2":"BINH TAN",
    },
    "HP": {
        "QLC": "LE CHAN",
        "QNQ": "NGO QUYEN",
        "QHB": "HAI BAI TRUNG",
        "QKA": "KIEN AN",
    },
    "DN": {
        "QHC": "HAI CHAU",
        "QTK": "THANH KHE",
        "QST": "SON TRA",
        "QNG": "NGU HANH SON",
        "QLD": "LIEN CHIEU",
    },
    "CT": {
        "QNK": "NINH KIEU",
        "QBT": "BINH THUY",
        "QCR": "CAI RANG",
    },
    "OTHER": {
        "Q01": "QUAN 1",
        "Q02": "QUAN 2",
    },
}

# (city_code, city_name, district_code, district_name) — used by CustomerGenerator
CITY_LIST: list[tuple[str, str, str, str]] = [
    ("HN",  "HA NOI",       "Q01", "HOAN KIEM"),
    ("HN",  "HA NOI",       "Q03", "DONG DA"),
    ("HN",  "HA NOI",       "Q06", "CAU GIAY"),
    ("HCM", "HO CHI MINH",  "Q01", "QUAN 1"),
    ("HCM", "HO CHI MINH",  "QBT", "BINH THANH"),
    ("HCM", "HO CHI MINH",  "QTD", "THU DUC"),
    ("DN",  "DA NANG",      "QHC", "HAI CHAU"),
    ("HP",  "HAI PHONG",    "QLC", "LE CHAN"),
    ("CT",  "CAN THO",      "QNK", "NINH KIEU"),
]

# ---------------------------------------------------------------------------
# Contract / loan
# ---------------------------------------------------------------------------

DATASOURCES: list[str]   = ["LD", "MG", "PD", "AC", "VS"]
SOURCE_TYPES: list[str]  = ["LOAN", "MD", "CC"]
CURRENCIES: list[str]    = ["VND", "USD"]
SECURED_VALS: list[str]  = ["Y", "N"]
CATEGORIES: list[str]    = ["CAT01", "CAT02", "CAT03", "CAT04"]
FREQ_CODES: list[str]    = ["M", "Q", "Y"]
TERMS: list[str]         = ["12M", "24M", "36M", "60M", "84M"]

# customer ↔ contract distribution: 82% 1 contract, 11% 2, 7% 3
# Represented as a pool to sample from (8×1 + 2×2 + 1×3)
CONTRACT_COUNT_POOL: list[int] = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3]

# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------

CUSTOMER_CLASSES: list[str] = ["R", "C", "I"]
CUSTOMER_GROUPS: list[str]  = ["I", "C"]          # Individual / Corporate
SECTORS: list[str]          = ["A", "B", "C", "D", "G", "K"]
SEGMENTS: list[str]         = ["MASS", "AFFLUENT", "SME", "CORP"]
GENDERS: list[str]          = ["M", "F"]
LEGAL_DOCS: list[str]       = ["CMND", "CCCD", "HC"]
EMPLOYMENTS: list[str]      = ["ACTIVE", "RESIGNED"]

# ---------------------------------------------------------------------------
# Card
# ---------------------------------------------------------------------------

CARD_TYPES: list[str]    = ["VISA", "MASTERCARD", "NAPAS"]
CARD_STATUSES: list[str] = ["CARD OK", "INACTIVE", "BLOCKED"]

# ---------------------------------------------------------------------------
# Loan transaction
# ---------------------------------------------------------------------------

# VARCHAR2 in FCT_XLN_LOAN_TXN and FCT_XLN_CREDIT_FEE
TRANS_CODES: list[str]   = ["130", "131", "133", "420", "434",
                              "750", "751", "752", "802", "804"]
REPAY_TYPES: list[str]   = ["PRINCIPAL", "INTEREST", "FEE"]
FEE_NAMES: list[str]     = ["Phi quan ly", "Phi phat sinh",
                              "Phi tra no truoc han", "Phi BH"]
PL_CATS: list[str]       = ["PL001", "PL002", "PL003"]

# DPD → nhóm nợ (SBV classification)
DPD_CLASSIFICATION: list[tuple[int, str]] = [
    (0,   "N01"),
    (10,  "N02"),
    (30,  "N03"),
    (90,  "N04"),
    (180, "N05"),
]
