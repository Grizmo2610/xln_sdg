# XLN_SDG — Engine Architecture & Workflow

## Package Structure

```
xln_sdg/
│
├── main.py                  # Entrypoint: python main.py <command>
│
└── engine/
    ├── cli/
    │   └── commands.py          # Click commands: seed, run, status
    │
    ├── schema/
    │   ├── tables.py            # All table definitions: Oracle name, columns, PK, FK
    │   ├── columns.py           # All column names as constants
    │   └── join_map.py          # FK relationships between tables
    ├── db/
    │   └── client.py
    │
    ├── core/
    │   ├── base.py
    │   ├── pool.py
    │   └── clock.py
    │
    ├── generators/
    │   ├── reference.py
    │   ├── customer.py
    │   └── loan.py
    │
    └── pipeline/
        ├── seed.py
        └── daily.py

.env                         # ORACLE_HOST, ORACLE_PORT, ORACLE_USER, ...
```

---

## Module Responsibilities

### `schema/columns.py` — Column constants
All column names as Python variables. No hardcoded strings anywhere else.

```python
# Surrogate keys
DIM_KEY         = "DIMENSION_KEY"
DIM_ID          = "DIMENSION_ID"

# Common
DAYID           = "DAYID"
EFF_DATE        = "EFF_DATE"
EXP_DATE        = "EXP_DATE"

# DIM_XLN_CUST
CUST_KEY        = "DIMENSION_KEY"   # surrogate key for CUST
CUSTOMER        = "CUSTOMER"        # business key
SHORT_NAME      = "SHORT_NAME"
CUSTOMER_CLASS  = "CUSTOMER_CLASS"

# DIM_XLN_CONTRACT
CONTRACT_ID     = "DIMENSION_ID"    # surrogate key for CONTRACT
CONTRACT        = "CONTRACT"        # business key
DATASOURCE      = "DATASOURCE"
VALUE_DATE      = "VALUE_DATE"
MATURITY_DATE   = "MATURITY_DATE"

# FK columns in FCT
CUSTOMER_SK     = "CUSTOMER_SK"
CONTRACT_SK     = "CONTRACT_SK"
COMPANY_SK      = "COMPANY_SK"
PRODUCT_SK      = "PRODUCT_SK"
BUCKET_SK       = "BUCKET_SK"
CARD_SK         = "CARD_SK"
SALES_SK        = "SALES_SK"

# ... remaining columns
```

---

### `schema/tables.py` — Table definitions
Defines each table: Oracle name, column list, surrogate key, identity columns.

```python
from schema.columns import *
from dataclasses import dataclass

@dataclass(frozen=True)
class TableDef:
    oracle_name: str        # Oracle table name — change here only if renamed
    columns: tuple[str, ...]
    surrogate_key: str      # DIMENSION_KEY or DIMENSION_ID
    identity_cols: tuple[str, ...]  # Oracle-generated columns, excluded from INSERT

DIM_XLN_CUST = TableDef(
    oracle_name   = "DIM_XLN_CUST",
    columns       = (CUST_KEY, CUSTOMER, SHORT_NAME, ...),
    surrogate_key = CUST_KEY,
    identity_cols = (),
)

DIM_XLN_CONTRACT = TableDef(
    oracle_name   = "DIM_XLN_CONTRACT",
    columns       = (CONTRACT_ID, CONTRACT, DATASOURCE, VALUE_DATE, ...),
    surrogate_key = CONTRACT_ID,
    identity_cols = (),
)

FCT_XLN_ACTIVE_LOAN = TableDef(
    oracle_name   = "FCT_XLN_ACTIVE_LOAN",
    columns       = (DAYID, CONTRACT, CUSTOMER_SK, CONTRACT_SK, ...),
    surrogate_key = None,
    identity_cols = (),
)

# Registry — look up by logical key
REGISTRY: dict[str, TableDef] = {
    "CUST":        DIM_XLN_CUST,
    "CONTRACT":    DIM_XLN_CONTRACT,
    "ACTIVE_LOAN": FCT_XLN_ACTIVE_LOAN,
    # ...
}
```

---

### `schema/join_map.py` — FK relationships
Defines joins between tables. Used by generators and PoolRegistry to know which columns to fetch.

```python
from schema.columns import *
from schema import tables as T

@dataclass(frozen=True)
class FKDef:
    from_table: str     # logical key of the table holding the FK
    fk_col: str         # FK column name
    to_table: str       # logical key of the DIM table
    to_col: str         # PK column of the DIM table

JOIN_MAP: list[FKDef] = [
    FKDef("ACTIVE_LOAN", CUSTOMER_SK, "CUST",     DIM_KEY),
    FKDef("ACTIVE_LOAN", CONTRACT_SK, "CONTRACT",  CONTRACT_ID),
    FKDef("ACTIVE_LOAN", COMPANY_SK,  "COMPANY",   DIM_KEY),
    FKDef("ACTIVE_LOAN", PRODUCT_SK,  "PRODUCT",   DIM_KEY),
    FKDef("ACTIVE_LOAN", BUCKET_SK,   "BUCKET",    DIM_ID),
    FKDef("ACTIVE_LOAN", CARD_SK,     "CARD",      DIM_KEY),
    FKDef("ACTIVE_LOAN", SALES_SK,    "SALECODE",  DIM_KEY),
    # ... other FCT tables
]

def required_pools(logical_key: str) -> list[str]:
    """Returns list of DIM tables that must be loaded before generating logical_key."""
    return [fk.to_table for fk in JOIN_MAP if fk.from_table == logical_key]
```

---

### `main.py` — Entrypoint
- Initialises Click app
- Imports and registers all commands from `cli/commands.py`
- Contains no business logic

---

### `cli/commands.py` — Commands (Click)

**`seed`** — Generate data for the first time from `START_DATE`
```
python main.py seed [--start-date 2023-01-01]
```
- Calls `SeedPipeline.run(start_date)`
- Used when Oracle has no data yet

**`run`** — Run daily pipeline up to a given date
```
python main.py run --date 2024-06-30
```
- Calls `SimClock` to determine which dates need to be run
- Calls `DailyPipeline.run(date)` for each date

**`status`** — Check data status in Oracle
```
python main.py status
```
- Queries `MAX(DAYID)` from all FCT tables
- Prints latest data date, row counts, and any missing tables

---

### `db/client.py` — OracleClient
- Loads config from `.env` (host, port, user, password, service_name)
- `connect()` / `close()` / context manager (`__enter__`, `__exit__`)
- `execute(sql, params)` — raw execute
- `select(sql, params) → pl.DataFrame` — fetches results as Polars DataFrame
- `insert(table_name, df, chunk_size)` — bulk insert, auto-chunked
- `fetch_pool(table_name, columns, where) → pl.DataFrame` — lightweight fetch of FK columns only

---

### `core/base.py` — BaseGenerator
- Abstract class for all generators
- `required_pools() → list[str]` — declares which pools must exist before running
- `generate(run_date, pool, n) → pl.DataFrame` — generates data
- Validates pools before generating, raises clearly if any are missing

---

### `core/pool.py` — PoolRegistry
- Receives `OracleClient`
- `get(table_name, columns) → pl.DataFrame` — fetches from Oracle, caches within session
- `refresh(table_name)` — re-fetches from Oracle (after an insert)
- `invalidate(table_name)` — clears cache
- Never loads full tables — fetches only the FK columns needed

---

### `core/clock.py` — SimClock
- `from_date`, `to_date` — time range to run
- `last_loaded_date(db) → date | None` — queries `MAX(DAYID)` from Oracle
- `dates_to_run(db) → Iterator[date]` — yields each date that has no data yet

---

### `generators/reference.py` — ReferenceGenerator
**Generates fully independent tables:** Company, Product, Salecode
- Requires no pool input
- Runs once at seed time; daily runs perform SCD2 churn only
- `generate(run_date, n) → pl.DataFrame`

---

### `generators/customer.py` — CustomerGenerator
**Generates Customer + Contract together in one self-contained batch**

Reason for grouping: `DIM_XLN_CONTRACT` has no `CUSTOMER_SK` column,
but the Customer ↔ Contract relationship is enforced here
using the real-world distribution (82% / 11% / 7%).

Flow:
```
1. Generate N customers
2. For each customer, sample contract count from distribution
3. Expand → generate exactly the right number of contracts, no more, no less
4. Return (customer_df, contract_df, mapping: contract_id → customer_id)
```

Output:
- `customer_df` → INSERT into DIM_XLN_CUST
- `contract_df` → INSERT into DIM_XLN_CONTRACT
- `mapping` → passed to LoanGenerator to enforce FK integrity

---

### `generators/loan.py` — LoanGenerator
**Generates Card + all FCT tables from contract context**

Inputs:
- `contract_pool` (fetched from Oracle or from CustomerGenerator output)
- `customer_pool` (fetched from Oracle)
- `mapping: contract_id → customer_id`
- `prev_state` (queried from Oracle for day D-1, see below)

**State management — Option A (query Oracle):**
```
Day D needs the state from day D-1 (DPD, BALANCE, STATE per contract)
→ SELECT CONTRACT, DPD, BALANCE, BALANCE_PD, STATE
  FROM FCT_XLN_ACTIVE_LOAN
  WHERE DAYID = D-1
→ Used to compute new DPD and balance for day D
→ Released from memory once day D generation is complete
```

Generates:
- `DIM_XLN_CARD` — VS contracts only
- `FCT_XLN_ACTIVE_LOAN` — 1 row per contract per day
- `FCT_XLN_REPAYSCHEDULE`
- `FCT_XLN_LOAN_TXN`
- `FCT_XLN_CREDIT_FEE`
- `FCT_XLN_BAD_DEBT`
- `FCT_XLN_INT_WRITE_OFF`
- `FCT_XLN_AFTER_COB_COLLECTION`

Every contract is guaranteed at least one FCT row — no orphan contracts.

---

### `pipeline/seed.py` — SeedPipeline
Runs on first execution when Oracle has no data.

```
Step 1: ReferenceGenerator → INSERT Company, Product, Salecode
Step 2: PoolRegistry.refresh(Company, Product, Salecode)
Step 3: CustomerGenerator → INSERT Customer, Contract (in batches)
Step 4: PoolRegistry.refresh(Customer, Contract)
Step 5: LoanGenerator → INSERT Card + all FCT tables for each day from START_DATE to run_date
```

---

### `pipeline/daily.py` — DailyPipeline
Runs daily, receives `--date` from CLI.

```
Step 1: SimClock.dates_to_run() → determine which dates are missing
Step 2: For each day D:
    a. ReferenceGenerator — SCD2 churn
    b. CustomerGenerator — generate new customers + contracts for the day
       → INSERT immediately, no RAM retained
    c. PoolRegistry.refresh() — fetch latest pool from Oracle
    d. OracleClient.select(FCT_ACTIVE_LOAN WHERE DAYID = D-1)
       → load prev_state (DPD, BALANCE, STATE per contract)
    e. LoanGenerator(prev_state) — generate FCT for day D
       → INSERT immediately
    f. Release prev_state from memory
```

---

## Overall Workflow

```
main.py run --date 2024-06-30
         │
         ▼
    SimClock
    MAX(DAYID) = 2024-06-25
    → dates to run: 2024-06-26 → 2024-06-30
         │
         ▼ (each day)
    ┌─────────────────────────────────────────┐
    │  ReferenceGenerator (SCD2 churn)        │
    │    Company / Product / Salecode         │
    └──────────────┬──────────────────────────┘
                   │ INSERT → Oracle
                   ▼
    ┌─────────────────────────────────────────┐
    │  CustomerGenerator                      │
    │    N new customers                      │
    │      → sample contract count/customer   │
    │      → generate exact number of         │
    │        contracts needed                 │
    │    OUTPUT: customer_df, contract_df,    │
    │            contract→customer mapping    │
    └──────────────┬──────────────────────────┘
                   │ INSERT → Oracle
                   │ PoolRegistry.refresh()
                   ▼
    ┌─────────────────────────────────────────┐
    │  Query prev_state from Oracle           │
    │    SELECT CONTRACT, DPD, BALANCE,       │
    │           BALANCE_PD, STATE             │
    │    FROM FCT_XLN_ACTIVE_LOAN             │
    │    WHERE DAYID = D-1                    │
    └──────────────┬──────────────────────────┘
                   │ prev_state (in RAM, day D only)
                   ▼
    ┌─────────────────────────────────────────┐
    │  LoanGenerator(prev_state)              │
    │    fetch contract_pool from Oracle      │
    │    compute new DPD, balance from D-1    │
    │    generate Card (VS only)              │
    │    generate FCT_ACTIVE_LOAN (all)       │
    │    generate FCT_LOAN_TXN                │
    │    generate FCT_REPAYSCHEDULE           │
    │    generate FCT_CREDIT_FEE              │
    │    generate FCT_BAD_DEBT / WRITE_OFF    │
    │    generate FCT_AFTER_COB               │
    └──────────────┬──────────────────────────┘
                   │ INSERT → Oracle
                   │ release prev_state
                   ▼
              Day D complete
              → move to day D+1
```

---

## Design Principles

| Principle | Description |
|---|---|
| No orphan | CustomerGenerator ensures every contract has a customer. LoanGenerator ensures every contract has at least one FCT row. |
| No local temp | No local files or temp tables. Pools are fetched directly from Oracle. |
| Low RAM | Each day is processed and released. Day D-1 state is queried from Oracle when needed and released immediately after day D generation completes. |
| Restartable | If interrupted, resume from `MAX(DAYID) + 1`. |
| Reusable | Each generator can be called independently given a pool. No hardcoded dependencies in the pipeline. |
| Single source of truth | All table names, column names, and FK relationships are defined in `schema/`. One change propagates everywhere. No hardcoded strings in generators, pipelines, or the client. |