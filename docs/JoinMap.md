# XLN_DTM — Join Map (FCT → DIM)

> Auto-generated: 2026-05-06  
> Source: `data/business_metadata/xln_dtm/_xln_dtm_data_model_source_v1.md`  
> Script: `scripts/extract/generate_join_map.py`

Bức tranh tổng quát về mối quan hệ giữa các bảng FACT và DIMENSION trong XLN_DTM.
Dùng khi: setup OAS Physical Layer, debug data lineage, viết JOIN query.

**Ký hiệu:**
- ✅ FK đã xác nhận từ ER diagram chính thức
- 🤖 FK do AI suy luận — cần review
- ⬜ Chưa có FK mapping trong source
- 📄 Link → file doc chi tiết (DDL + profiling + FK section)

---

## 04 Lending / Loan

| FCT Table | FK Column | → DIM Table | DIM PK | Status | Doc |
|---|---|---|---|---|---|
| `FCT_XLN_ACTIVE_LOAN` | `CONTRACT_SK` | `DIM_XLN_CONTRACT` | `DIMENSION_ID` | ✅ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_ACTIVE_LOAN.md) |
|  | `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` | ✅ |  |
|  | `PRODUCT_SK` | `DIM_XLN_PRODUCT` | `DIMENSION_KEY` | ✅ |  |
|  | `BUCKET_SK` | `DIM_XLN_BUCKET` | `DIMENSION_ID` | ✅ |  |
|  | `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` | ✅ |  |
|  | `CARD_SK` | `DIM_XLN_CARD` | `DIMENSION_KEY` | ✅ |  |
|  | `SALES_SK` | `DIM_XLN_SALECODE` | `DIMENSION_KEY` | ✅ |  |
| `FCT_XLN_LOAN_COLLECTION` | — | — | — | ⬜ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_LOAN_COLLECTION.md) |
| `FCT_XLN_LOAN_TXN` | `XLN_CONTRACT_SK` | `DIM_XLN_CONTRACT` | `DIMENSION_ID` | 🤖 | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_LOAN_TXN.md) |
|  | `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` | 🤖 |  |
|  | `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` | 🤖 |  |
|  | `PRODUCT_SK` | `DIM_XLN_PRODUCT` | `DIMENSION_KEY` | 🤖 |  |
|  | `SEAB_PRODUCTS_SK` | `DIM_XLN_SEAB_PRODUCT` | `DIMENSION_KEY` | 🤖 |  |

## 05 Card / Thẻ

| FCT Table | FK Column | → DIM Table | DIM PK | Status | Doc |
|---|---|---|---|---|---|
| `FCT_XLN_CARD_ALLOCATION_DAILY` | `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` | ✅ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_CARD_ALLOCATION_DAILY.md) |
|  | `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` | ✅ |  |

## 06 Payment / Phí / Giao dịch

| FCT Table | FK Column | → DIM Table | DIM PK | Status | Doc |
|---|---|---|---|---|---|
| `FCT_XLN_CREDIT_FEE` | `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` | ✅ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_CREDIT_FEE.md) |
|  | `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` | ✅ |  |

## 10 Khác

| FCT Table | FK Column | → DIM Table | DIM PK | Status | Doc |
|---|---|---|---|---|---|
| `FCT_XLN_AFTER_COB_COLLECTION` | — | — | — | ⬜ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_AFTER_COB_COLLECTION.md) |
| `FCT_XLN_BAD_DEBT` | `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` | ✅ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_BAD_DEBT.md) |
|  | `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` | ✅ |  |
|  | `PRODUCT_SK` | `DIM_XLN_PRODUCT` | `DIMENSION_KEY` | ✅ |  |
| `FCT_XLN_CHUYEN_LUONG` | `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` | ✅ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_CHUYEN_LUONG.md) |
| `FCT_XLN_GROUP_HIST` | — | — | — | ⬜ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_GROUP_HIST.md) |
| `FCT_XLN_INT_WRITE_OFF` | `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` | ✅ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_INT_WRITE_OFF.md) |
|  | `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` | ✅ |  |
| `FCT_XLN_MD` | `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` | ✅ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_MD.md) |
|  | `CONTRACT_MD_SK` | `DIM_XLN_MD` | `DIMENSION_KEY` | ✅ |  |
|  | `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` | ✅ |  |
|  | `LIMIT_SK` | `DIM_XLN_LIMIT` | `DIMENSION_KEY` | ✅ |  |
|  | `COLLATERAL_SK` | `DIM_XLN_COLLATERAL` | `DIMENSION_KEY` | ✅ |  |
|  | `PRODUCT_SK` | `DIM_XLN_PRODUCT` | `DIMENSION_KEY` | ✅ |  |
| `FCT_XLN_OVERDUE_DATE` | `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` | ✅ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_OVERDUE_DATE.md) |
|  | `CONTRACT_SK` | `DIM_XLN_CONTRACT` | `DIMENSION_ID` | ✅ |  |
| `FCT_XLN_REPAYSCHEDULE` | `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` | ✅ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_REPAYSCHEDULE.md) |
|  | `CONTRACT_SK` | `DIM_XLN_CONTRACT` | `DIMENSION_ID` | ✅ |  |
|  | `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` | ✅ |  |
|  | `SALES_SK` | `DIM_XLN_SALECODE` | `DIMENSION_KEY` | ✅ |  |
| `FCT_XLN_THONGTIN_TACNGHIEP` | — | — | — | ⬜ | [📄](docs/data-dictionary/datamart/xln_dtm/FCT_XLN_THONGTIN_TACNGHIEP.md) |

---

## Tổng kết

| | Count |
|---|---|
| Tổng FCT tables | 14 |
| ✅ Có FK — confirmed | 9 |
| 🤖 Có FK — AI-inferred | 1 |
| ⬜ Chưa có FK mapping | 4 |
