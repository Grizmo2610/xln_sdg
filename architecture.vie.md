# XLN_SDG — Engine Architecture & Workflow

## Cấu trúc package

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

## Trách nhiệm từng module

### `schema/columns.py` — Column constants
Tất cả tên cột dưới dạng biến Python. Không hardcode string ở bất kỳ đâu khác.

```python
# Surrogate keys
DIM_KEY         = "DIMENSION_KEY"
DIM_ID          = "DIMENSION_ID"

# Common
DAYID           = "DAYID"
EFF_DATE        = "EFF_DATE"
EXP_DATE        = "EXP_DATE"

# DIM_XLN_CUST
CUST_KEY        = "DIMENSION_KEY"   # surrogate key của CUST
CUSTOMER        = "CUSTOMER"        # business key
SHORT_NAME      = "SHORT_NAME"
CUSTOMER_CLASS  = "CUSTOMER_CLASS"

# DIM_XLN_CONTRACT
CONTRACT_ID     = "DIMENSION_ID"    # surrogate key của CONTRACT
CONTRACT        = "CONTRACT"        # business key
DATASOURCE      = "DATASOURCE"
VALUE_DATE      = "VALUE_DATE"
MATURITY_DATE   = "MATURITY_DATE"

# FK columns trong FCT
CUSTOMER_SK     = "CUSTOMER_SK"
CONTRACT_SK     = "CONTRACT_SK"
COMPANY_SK      = "COMPANY_SK"
PRODUCT_SK      = "PRODUCT_SK"
BUCKET_SK       = "BUCKET_SK"
CARD_SK         = "CARD_SK"
SALES_SK        = "SALES_SK"

# ... tất cả columns còn lại
```

---

### `schema/tables.py` — Table definitions
Định nghĩa từng bảng: tên Oracle, list columns, surrogate key, identity columns.

```python
from schema.columns import *
from dataclasses import dataclass

@dataclass(frozen=True)
class TableDef:
    oracle_name: str        # tên bảng trên Oracle — sửa 1 chỗ này nếu đổi tên
    columns: tuple[str, ...]
    surrogate_key: str      # DIMENSION_KEY hoặc DIMENSION_ID
    identity_cols: tuple[str, ...]  # cột Oracle tự sinh, không INSERT

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

# Registry — tra cứu theo tên logic
REGISTRY: dict[str, TableDef] = {
    "CUST":        DIM_XLN_CUST,
    "CONTRACT":    DIM_XLN_CONTRACT,
    "ACTIVE_LOAN": FCT_XLN_ACTIVE_LOAN,
    # ...
}
```

---

### `schema/join_map.py` — FK relationships
Định nghĩa join giữa các bảng. Generator và PoolRegistry dùng để biết cần fetch columns nào.

```python
from schema.columns import *
from schema import tables as T

@dataclass(frozen=True)
class FKDef:
    from_table: str     # logical key của bảng chứa FK
    fk_col: str         # tên cột FK
    to_table: str       # logical key của bảng DIM
    to_col: str         # cột PK của DIM

JOIN_MAP: list[FKDef] = [
    FKDef("ACTIVE_LOAN", CUSTOMER_SK, "CUST",     DIM_KEY),
    FKDef("ACTIVE_LOAN", CONTRACT_SK, "CONTRACT",  CONTRACT_ID),
    FKDef("ACTIVE_LOAN", COMPANY_SK,  "COMPANY",   DIM_KEY),
    FKDef("ACTIVE_LOAN", PRODUCT_SK,  "PRODUCT",   DIM_KEY),
    FKDef("ACTIVE_LOAN", BUCKET_SK,   "BUCKET",    DIM_ID),
    FKDef("ACTIVE_LOAN", CARD_SK,     "CARD",      DIM_KEY),
    FKDef("ACTIVE_LOAN", SALES_SK,    "SALECODE",  DIM_KEY),
    # ... các FCT khác
]

def required_pools(logical_key: str) -> list[str]:
    """Trả về list DIM tables cần load trước khi sinh logical_key."""
    return [fk.to_table for fk in JOIN_MAP if fk.from_table == logical_key]
```

---

### `main.py` — Entrypoint
- Khởi tạo Click app
- Import và đăng ký tất cả commands từ `cli/commands.py`
- Không chứa business logic

---

### `cli/commands.py` — Commands (Click)

**`seed`** — Sinh data lần đầu từ `START_DATE`
```
python main.py seed [--start-date 2023-01-01]
```
- Gọi `SeedPipeline.run(start_date)`
- Dùng khi Oracle chưa có data

**`run`** — Chạy daily pipeline đến ngày chỉ định
```
python main.py run --date 2024-06-30
```
- Gọi `SimClock` → tính ngày cần chạy
- Gọi `DailyPipeline.run(date)` cho từng ngày

**`status`** — Kiểm tra trạng thái data trong Oracle
```
python main.py status
```
- Query `MAX(DAYID)` từ các FCT table
- In ra ngày data mới nhất, số rows, các bảng nào còn thiếu

---

### `db/client.py` — OracleClient
- Load config từ `.env` (host, port, user, password, service_name)
- `connect()` / `close()` / context manager (`__enter__`, `__exit__`)
- `execute(sql, params)` — raw execute
- `select(sql, params) → pl.DataFrame` — fetch kết quả về Polars
- `insert(table_name, df, chunk_size)` — bulk insert, tự chunk
- `fetch_pool(table_name, columns, where) → pl.DataFrame` — fetch nhẹ chỉ lấy FK columns cần thiết

---

### `core/base.py` — BaseGenerator
- Abstract class cho mọi generator
- `required_pools() → list[str]` — khai báo pool nào phải có trước
- `generate(run_date, pool, n) → pl.DataFrame` — sinh data
- Tự validate pool trước khi sinh, raise rõ ràng nếu thiếu

---

### `core/pool.py` — PoolRegistry
- Nhận `OracleClient`
- `get(table_name, columns) → pl.DataFrame` — fetch từ Oracle, cache trong session
- `refresh(table_name)` — fetch lại từ Oracle (sau khi insert xong)
- `invalidate(table_name)` — xóa cache
- Không load cả bảng — chỉ fetch đúng columns FK cần thiết

---

### `core/clock.py` — SimClock
- `from_date`, `to_date` — khoảng thời gian cần chạy
- `last_loaded_date(db) → date | None` — query `MAX(DAYID)` từ Oracle
- `dates_to_run(db) → Iterator[date]` — yield từng ngày chưa có data

---

### `generators/reference.py` — ReferenceGenerator
**Sinh các bảng độc lập hoàn toàn:** Company, Product, Salecode
- Không cần pool input
- Chạy 1 lần lúc seed, hàng ngày chỉ SCD2 churn
- `generate(run_date, n) → pl.DataFrame`

---

### `generators/customer.py` — CustomerGenerator
**Sinh Customer + Contract cùng nhau, 1 batch khép kín**

Lý do gộp: Contract không có `CUSTOMER_SK` trong DIM,
nhưng relationship Customer ↔ Contract được enforce tại đây
thông qua distribution thực tế (82% / 11% / 7%).

Flow:
```
1. Sinh N customers
2. Với mỗi customer, sample số contract theo distribution
3. Expand → sinh đúng số contracts cần, không thừa không thiếu
4. Trả ra (customer_df, contract_df, mapping: contract_id → customer_id)
```

Output:
- `customer_df` → INSERT vào DIM_XLN_CUST
- `contract_df` → INSERT vào DIM_XLN_CONTRACT
- `mapping` → pass sang LoanGenerator để enforce FK

---

### `generators/loan.py` — LoanGenerator
**Sinh Card + toàn bộ FCT từ contract context**

Nhận vào:
- `contract_pool` (fetch từ Oracle hoặc từ CustomerGenerator output)
- `customer_pool` (fetch từ Oracle)
- `mapping: contract_id → customer_id`
- `prev_state` (query từ Oracle ngày D-1, xem bên dưới)

**State management — Option A (query Oracle):**
```
Ngày D cần state của ngày D-1 (DPD, BALANCE, STATE của từng contract)
→ SELECT CONTRACT, DPD, BALANCE, BALANCE_PD, STATE
  FROM FCT_XLN_ACTIVE_LOAN
  WHERE DAYID = D-1
→ Dùng để tính DPD mới, balance mới cho ngày D
→ Giải phóng sau khi sinh xong ngày D
```

Sinh:
- `DIM_XLN_CARD` — chỉ VS contracts
- `FCT_XLN_ACTIVE_LOAN` — 1 row / contract / ngày
- `FCT_XLN_REPAYSCHEDULE`
- `FCT_XLN_LOAN_TXN`
- `FCT_XLN_CREDIT_FEE`
- `FCT_XLN_BAD_DEBT`
- `FCT_XLN_INT_WRITE_OFF`
- `FCT_XLN_AFTER_COB_COLLECTION`

Không có contract nào bị bỏ sót — mọi contract đều có ít nhất 1 FCT row.

---

### `pipeline/seed.py` — SeedPipeline
Chạy lần đầu khi Oracle chưa có data.

```
Step 1: ReferenceGenerator → INSERT Company, Product, Salecode
Step 2: PoolRegistry.refresh(Company, Product, Salecode)
Step 3: CustomerGenerator → INSERT Customer, Contract (theo batch)
Step 4: PoolRegistry.refresh(Customer, Contract)
Step 5: LoanGenerator → INSERT Card + tất cả FCT cho từng ngày từ START_DATE đến run_date
```

---

### `pipeline/daily.py` — DailyPipeline
Chạy mỗi ngày, nhận `--date` từ CLI.

```
Step 1: SimClock.dates_to_run() → biết ngày nào chưa có
Step 2: Với mỗi ngày D:
    a. ReferenceGenerator — SCD2 churn
    b. CustomerGenerator — sinh customer + contract mới trong ngày
       → INSERT ngay, không giữ RAM
    c. PoolRegistry.refresh() — fetch pool mới nhất từ Oracle
    d. OracleClient.select(FCT_ACTIVE_LOAN WHERE DAYID = D-1)
       → load prev_state (DPD, BALANCE, STATE của từng contract)
    e. LoanGenerator(prev_state) — sinh FCT cho ngày D
       → INSERT ngay
    f. Giải phóng prev_state khỏi RAM
```

---

## Workflow tổng quan

```
main.py run --date 2024-06-30
         │
         ▼
    SimClock
    MAX(DAYID) = 2024-06-25
    → cần chạy: 2024-06-26 → 2024-06-30
         │
         ▼ (mỗi ngày)
    ┌─────────────────────────────────────────┐
    │  ReferenceGenerator (SCD2 churn)        │
    │    Company / Product / Salecode         │
    └──────────────┬──────────────────────────┘
                   │ INSERT → Oracle
                   ▼
    ┌─────────────────────────────────────────┐
    │  CustomerGenerator                      │
    │    N customers mới                      │
    │      → sample contract count/customer   │
    │      → sinh đúng số contracts           │
    │    OUTPUT: customer_df, contract_df,    │
    │            contract→customer mapping    │
    └──────────────┬──────────────────────────┘
                   │ INSERT → Oracle
                   │ PoolRegistry.refresh()
                   ▼
    ┌─────────────────────────────────────────┐
    │  Query prev_state từ Oracle             │
    │    SELECT CONTRACT, DPD, BALANCE,       │
    │           BALANCE_PD, STATE             │
    │    FROM FCT_XLN_ACTIVE_LOAN             │
    │    WHERE DAYID = D-1                    │
    └──────────────┬──────────────────────────┘
                   │ prev_state (in RAM, ngày D only)
                   ▼
    ┌─────────────────────────────────────────┐
    │  LoanGenerator(prev_state)              │
    │    fetch contract_pool từ Oracle        │
    │    tính DPD mới, balance mới từ D-1     │
    │    sinh Card (VS only)                  │
    │    sinh FCT_ACTIVE_LOAN (mọi contract)  │
    │    sinh FCT_LOAN_TXN                    │
    │    sinh FCT_REPAYSCHEDULE               │
    │    sinh FCT_CREDIT_FEE                  │
    │    sinh FCT_BAD_DEBT / WRITE_OFF        │
    │    sinh FCT_AFTER_COB                   │
    └──────────────┬──────────────────────────┘
                   │ INSERT → Oracle
                   │ giải phóng prev_state
                   ▼
              Xong ngày D
              → sang ngày D+1
```

---

## Nguyên tắc thiết kế

| Nguyên tắc | Giải thích |
|---|---|
| No orphan | CustomerGenerator đảm bảo mọi contract có customer. LoanGenerator đảm bảo mọi contract có FCT row. |
| No local temp | Không dùng file local hay bảng tạm. Pool fetch trực tiếp từ Oracle. |
| Low RAM | Mỗi ngày xử lý xong là giải phóng. State ngày D-1 được query từ Oracle khi cần, giải phóng ngay sau khi sinh xong ngày D. |
| Restartable | Dừng giữa chừng, chạy lại từ `MAX(DAYID) + 1`. |
| Tái sử dụng | Từng generator có thể gọi độc lập nếu đã có pool. Không hardcode dependency vào pipeline. |
| Single source of truth | Mọi tên bảng, tên cột, FK relationship đều định nghĩa trong `schema/`. Sửa 1 chỗ, có hiệu lực toàn bộ. Không hardcode string ở generator, pipeline hay client. |