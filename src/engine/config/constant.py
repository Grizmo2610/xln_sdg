"""
config/constant.py
Global scalar constants — sizes, thresholds, noise, limits.
Edit here to tune the generator globally.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Seed / daily volume anchors
# ---------------------------------------------------------------------------

# Initial customer count for seed run.
# All RATIOS in propensity.py are multiplied by this.
INIT_CUSTOMERS: int = 2_000

# New customers added per daily run.
DAILY_NEW_CUSTOMERS: int = 20

# Number of sales staff to seed initially.
N_SALES_SEED: int = 80

# New sales staff added per daily run (SCD2 churn).
N_SALES_DAILY: int = 2

# Batch size for CustomerGenerator (avoid OOM on large seeds).
CUSTOMER_BATCH_SIZE: int = 500

# ---------------------------------------------------------------------------
# Surrogate-key pools for VietnameseFaker name pre-generation
# ---------------------------------------------------------------------------
FAKER_MALE_POOL_SIZE: int   = 5_000
FAKER_FEMALE_POOL_SIZE: int = 5_000

# ---------------------------------------------------------------------------
# Volumetry noise
# ---------------------------------------------------------------------------

# +/- noise applied to every volumetry estimate (Normal distribution σ).
# 0.05 = ±5 % typical, capped at ±15 % (3σ clip in VolumetryManager).
VOLUMETRY_NOISE_PCT: float = 0.05

# ---------------------------------------------------------------------------
# Loan / contract generation
# ---------------------------------------------------------------------------

# Loan amount range (VND)
LOAN_AMT_MIN: int = 10_000_000
LOAN_AMT_MAX: int = 500_000_000

# Daily principal repayment range (VND) — amount amortised per day in simulation
DAILY_REPAY_MIN: int = 0
DAILY_REPAY_MAX: int = 500_000

# Fee amount range (VND)
FEE_AMT_MIN: int = 10_000
FEE_AMT_MAX: int = 500_000

# Write-off amount range (VND)
WRITE_OFF_AMT_MIN: int = 100_000
WRITE_OFF_AMT_MAX: int = 5_000_000

# Interest rate range (annual, decimal)
INTEREST_RATE_MIN: float = 0.06
INTEREST_RATE_MAX: float = 0.18

# Overdue penalty rate range (annual, decimal)
OVD_RATE_MIN: float = 0.15
OVD_RATE_MAX: float = 0.24

# DPD threshold to classify a contract as bad debt
BAD_DEBT_DPD_THRESHOLD: int = 90

# Card expiry horizon (years from value_date)
CARD_EXPIRY_YEARS: int = 3

# Max repayment schedule rows per contract per day
MAX_REPAY_ROWS: int = 3

# Max loan transaction rows per contract per day
MAX_TXN_ROWS: int = 2

# ---------------------------------------------------------------------------
# Customer open-date range for seed
# ---------------------------------------------------------------------------
CUST_OPEN_DATE_START_YEAR: int = 2015

# ---------------------------------------------------------------------------
# SCD2 end-of-time sentinel (active records)
# ---------------------------------------------------------------------------
# Use None (NULL) to mark active rows — downstream handles it as open-ended.
# If your DWH requires a sentinel date instead, set EXP_DATE_SENTINEL here.
EXP_DATE_SENTINEL = None
