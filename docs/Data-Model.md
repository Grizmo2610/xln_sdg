# Báo cáo Thiết kế Mô hình Dữ liệu (Data Model) — XLN_DTM

> **Trạng thái:** Auto-generated từ DDD docx  
> **Nguồn:** `data/business_metadata/xln_dtm/DDD-Thiết kế chi tiết datamart XLN V1.0 phase 2.docx`  
> **Ngày tạo:** 2026-05-06  
> **Tổng bảng:** 17 (10 DIM + 7 FCT)  
> **Merged từ:** `_xln_dtm_data_model_source_v1.md` + `_xln_dtm_v11_source.md` (2026-05-06)

> **Ký hiệu:**
> - ✅ = FK đã xác nhận (từ mô tả cột trong DDD)
> - 🤖 = FK do AI suy luận từ tên cột `_SK` (cần review)

---

## Mục lục

### Dimension Tables

| # | Bảng | Số cột |
|:--|:-----|:-------|
| 1 | DIM_XLN_COMPANY | 12 |
| 2 | DIM_XLN_CONTRACT | 21 |
| 3 | DIM_XLN_CUST | 12 |
| 4 | DIM_XLN_CUST_PII | 13 |
| 5 | DIM_XLN_LOAN_TXN_CODE | 5 |
| 6 | DIM_XLN_PRODUCT | 6 |

### Fact Tables

| # | Bảng | Type | FK Count | FK Source |
|:--|:-----|:-----|:---------|:----------|
| 1 | FCT_XLN_AFTER_COB_COLLECTION | Fact | 0 | ⬜ No FK data |
| 2 | FCT_XLN_BAD_DEBT | Fact | 3 | ✅ 3 confirmed, 🤖 0 inferred |
| 3 | FCT_XLN_CREDIT_FEE | Fact | 2 | ✅ 2 confirmed, 🤖 0 inferred |
| 4 | FCT_XLN_INT_WRITE_OFF | Fact | 2 | ✅ 2 confirmed, 🤖 0 inferred |
| 5 | FCT_XLN_LOAN_TXN | Fact | 5 | ✅ 4 confirmed, 🤖 1 inferred |

---

---

## Bảng: DIM_XLN_COMPANY

- **Schema:** XLN_DTM
- **Type:** DIM

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:----|:--------|:-------------|:-----|:----------------|
| 1 | `DIMENSION_KEY` | NUMBER(25,0) |  | Surrogate Key |
| 2 | `COMPANY_CODE` | VARCHAR2(50) |  | Mã ĐVKD |
| 3 | `COMPANY_NAME` | VARCHAR2(200) |  | Tên ĐVKD |
| 4 | `BRANCH_CODE` | VARCHAR2(50) |  | Mã Chi nhánh |
| 5 | `BRANCH_NAME` | VARCHAR2(200) |  | Tên chi nhánh |
| 6 | `COMPANY_NAME_VN` | VARCHAR2(250) |  | Tên ĐVKD tiếng việt |
| 7 | `BRANCH_CITY` | VARCHAR2(50) |  | Mã tỉnh thành tương ứng chi nhánh |
| 8 | `BRANCH_PROVINCE` | VARCHAR2(50) |  | Tỉnh/TP tương ứng chi nhánh |
| 9 | `REGION_CODE` | VARCHAR2(50) |  | Mã khu vực |
| 10 | `REGION_NAME` | VARCHAR2(200) |  | Tên khu vực |
| 11 | `EXP_DATE` | DATE |  | Ngày hết hiệu lực bản ghi |
| 12 | `EFF_DATE` | DATE |  | Ngày hiệu lực bản ghi |

---

---

## Bảng: DIM_XLN_CONTRACT

- **Schema:** XLN_DTM
- **Type:** DIM

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:---:|:---|:---|:---|:---|
| 1 | `DIMENSION_ID` | NUMBER |  | Surrogate Key |
| 2 | `CONTRACT` | VARCHAR2(50) |  | Mã hợp đồng |
| 3 | `DATASOURCE` | VARCHAR2(30) |  | Nguồn dữ liệu: LD/MG/PD/AC/VS |
| 4 | `CONTRACT_REF` | VARCHAR2(50) |  | Mã HĐ REF |
| 5 | `CATEGORY` | VARCHAR2(50) |  | Mã category |
| 6 | `CURRENCY` | VARCHAR2(10) |  | Mã tiền tệ |
| 7 | `COLLATERAL_DESC` | VARCHAR2(500) |  | Mô tả tài sản bảo đảm |
| 8 | `VALUE_DATE` | DATE |  | Ngày mở khoản vay |
| 9 | `MATURITY_DATE` | DATE |  | Ngày hết hạn khoản vay |
| 10 | `INT_LIQ_ACCT` | VARCHAR2(50) |  | Tài khoản thanh toán lãi |
| 11 | `MORTGAGE_ACCOUNT` | VARCHAR2(50) |  | Tài khoản thế chấp |
| 12 | `CHRG_LIQ_ACCT` | VARCHAR2(50) |  | Tài khoản thanh toán phí |
| 13 | `SECURED` | VARCHAR2(10) |  | Thông tin khoản vay có tài sản bảo đảm |
| 14 | `CO_CODE` | VARCHAR2(50) |  | Mã ĐVKD quản lý khoản vay |
| 15 | `REMARKS` | VARCHAR2(500) |  | Ghi chú |
| 16 | `FREQUENCY` | VARCHAR2(50) |  | Tần suất |
| 17 | `FREQUENCY_DAY` | NUMBER |  | Ngày thực hiện theo tần suất |
| 18 | `FREQUENCY_PR` | VARCHAR2(50) |  | Thông tin kỳ/tần suất trả |
| 19 | `TERM` | VARCHAR2(50) |  | Kỳ hạn |
| 20 | `LIMIT_REF` | VARCHAR2(100) |  | Mã hạn mức |
| 21 | `SEAB_LOS_ID` | VARCHAR2(100) |  | Mã hồ sơ LOS |
| 22 | `REF_CONTRACT_REF` | VARCHAR2(50) |  | Mã ref hợp đồng MD |
| 23 | `SOURCE_TYPE` | VARCHAR2(50) |  | Loại hợp đồng (LOAN/MD...) |
| 24 | `EFF_DATE` | DATE |  | Ngày hiệu lực bản ghi |
| 25 | `EXP_DATE` | DATE |  | Ngày hết hiệu lực bản ghi |
| 26 | `CAMPAIGN_ID` | VARCHAR2(100) |  | Mã chiến dịch gắn với hợp đồng |
| 27 | `REF_VALUE_DATE` | DATE |  | Ngày mở hợp đồng tín dụng |
| 28 | `REF_MAT_DATE` | DATE |  | Ngày đáo hạn của hợp đồng tín dụng |
| 29 | `REF_CONTRACT_AMT` | NUMBER |  | Số tiền của hợp đồng tín dụng |
| 30 | `REF_CONTRACT_CCY` | VARCHAR2(50) |  | Loại tiền của hợp đồng tín dụng |
---

---

## Bảng: DIM_XLN_CUST

- **Schema:** XLN_DTM
- **Type:** DIM

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:---:|:---|:---|:---|:---|
| 1 | `DIMENSION_KEY` | NUMBER(25,0) |  | Surrogate Key |
| 2 | `CUSTOMER` | VARCHAR2(50) |  | Mã khách hàng |
| 3 | `SHORT_NAME` | VARCHAR2(200) |  | Tên khách hàng |
| 4 | `CUSTOMER_CLASS` | VARCHAR2(50) |  | Phân hạng khách hàng |
| 5 | `CONTACT_DATE` | DATE |  | Ngày mở của khách hàng |
| 6 | `PORTFOLIO` | VARCHAR2(50) |  | Mã portfolio của cán bộ QLKH |
| 7 | `DISTRICT_CODE` | VARCHAR2(50) |  | Mã quận/huyện |
| 8 | `DISTRICT_NAME` | VARCHAR2(200) |  | Tên quận/huyện |
| 9 | `CITY_CODE` | VARCHAR2(50) |  | Mã thành phố |
| 10 | `CITY_NAME` | VARCHAR2(200) |  | Tên thành phố |
| 11 | `STATUS_DATE` |  |  |  |
| 12 | `EMPLOYMENT` |  |  |  |
| 13 | `EFF_DATE` | DATE |  | Ngày hiệu lực bản ghi |
| 14 | `EXP_DATE` | DATE |  | Ngày hết hiệu lực bản ghi |
| 15 | `CUSTOMER_GROUP` |  |  |  |
| 16 | `SEAB_CU_SEGMENT` |  |  |  |
| 17 | `SECTOR` |  |  | Ngành nghề/lĩnh vực của khách hàng |
| 18 | `ACCOUNT_OFFICER` |  |  | Mã cán bộ quản lý khách hàng |
| 19 | `ACCOUNT_OFFICER_NAME` |  |  | Tên cán bộ quản lý khách hàng |

---

---

## Bảng: DIM_XLN_CUST_PII

- **Schema:** XLN_DTM
- **Type:** DIM

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:---:|:---|:---|:---|:---|
| 1 | `DIMENSION_KEY` | NUMBER(25,0) |  | Surrogate Key |
| 2 | `CUSTOMER` | VARCHAR2(200) |  | Mã khách hàng |
| 3 | `DATE_OF_BIRTH` | DATE |  | Ngày sinh khách hàng |
| 4 | `GENDER` | VARCHAR2(200) |  | Giới tính |
| 5 | `LEGAL_ID` | VARCHAR2(200) |  | Số CMT/ Hộ chiếu/ Đăng ký kinh doanh |
| 6 | `LEGAL_DOC_NAME` | VARCHAR2(200) |  | Loại giấy tờ tùy thân |
| 7 | `LEGAL_ISS_DATE` | DATE |  | Ngày cấp GTTT |
| 8 | `PHONE_T24` | VARCHAR2(200) |  | Số điện thoại khách hàng T24 |
| 9 | `EMAIL_T24` | VARCHAR2(200) |  | Email khách hàng T24 |
| 10 | `ADDRESS_T24` | VARCHAR2(400) |  | Địa chỉ khách hàng T24 |
| 11 | `SB_ID` | VARCHAR2(50) |  | Mã SB ID nếu là CBNV |
| 12 | `EFF_DATE` | DATE |  | Ngày hiệu lực bản ghi |
| 13 | `EXP_DATE` | DATE |  | Ngày hết hiệu lực bản ghi |
---

---

## Bảng: DIM_XLN_LOAN_TXN_CODE

- **Schema:** XLN_DTM
- **Type:** DIM

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:---:|:---|:---|:---|:---|
| 1 | `ID` | NUMBER(25,0) |  |  |
| 2 | `TRANS_CODE` | VARCHAR2(200) |  | Mã loại giao dịch |
| 3 | `TRANS_NAME` | VARCHAR2(255) |  | Tên loại giao dịch |
| 4 | `TRANS_TYPE` | VARCHAR2(40) |  | Phân loại giao dịch: giải ngân, thu nợ trong hạn, quá hạn |
| 5 | `LOAN_TYPE` | VARCHAR2(50) |  | Phân hệ: VS.. |
| 6 | `TRANS_NAME_XLN` |  |  |  |
---

---

## Bảng: DIM_XLN_PRODUCT

- **Schema:** XLN_DTM
- **Type:** DIM

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:----|:--------|:-------------|:-----|:----------------|
| 1 | `DIMENSION_KEY` | NUMBER |  | Surrogate Key |
| 2 | `PRODUCT_CODE` | VARCHAR2(50) |  | Mã sản phẩm |
| 3 | `PRODUCT_NAME` | VARCHAR2(255) |  | Tên sản phẩm |
| 4 | `PRODUCT_GROUP` | VARCHAR2(255) |  | Nhóm sản phẩm |
| 5 | `EXP_DATE` | DATE |  | Ngày hết hiệu lực bản ghi |
| 6 | `EFF_DATE` | DATE |  | Ngày hiệu lực bản ghi |

---

---

## Bảng: FCT_XLN_AFTER_COB_COLLECTION

- **Schema:** XLN_DTM
- **Type:** FCT

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:---:|:---|:---|:---|:---|
| 1 | `DAYID` | date, optional | PK | Ngày dữ liệu |
| 2 | `MA_KHACH_HANG` | varchar2(40), optional | PK | Mã khách hàng |
| 3 | `TEN_KHACH_HANG` | varchar2(200), optional |  | Tên đầy đủ của khách hàng |
| 4 | `SO_HOP_DONG` | varchar2(200), optional |  | Số hợp đồng tín dụng của khách hàng |
| 5 | `NGAY_MO` | date, optional |  | Ngày mở hợp đồng |
| 6 | `DAO_HAN` | date, optional |  | Ngày đáo hạn của hợp đồng tín dụng |
| 7 | `LOAI_TIEN` | varchar2(3), optional |  | Loại tiền tệ được sử dụng trong giao dịch |
| 8 | `LOAI_GIAO_DICH` | varchar2(50), optional |  | Loại giao dịch tín dụng |
| 9 | `SO_TIEN_GIAO_DICH` | number, optional |  | Số tiền của giao dịch tín dụng |
| 10 | `SO_DU_HOP_DONG` | number, optional |  | Số dư còn lại trong hợp đồng tín dụng |
| 11 | `MA_CHI_NHANH` | varchar2(30), optional |  | Mã chi nhánh ngân hàng quản lý hợp đồng |
| 12 | `TEN_CHI_NHANH` | varchar2(300), optional |  | Tên chi nhánh ngân hàng quản lý hợp đồng |
| 13 | `NGAY_GIAO_DICH` | date, optional |  | Ngày thực hiện giao dịch tín dụng |
| 14 | `GHI_CHU` | char(15), optional |  | Thông tin ghi chú thêm về giao dịch |
| 15 | `SEGMENT` | varchar2(200), optional |  | Phân khúc khách hàng |
| 16 | `SECTOR` | varchar2(16), optional |  | Ngành nghề kinh doanh của khách hàng |
| 17 | `CATEGORY` | varchar2(12), optional |  | Loại hình khách hàng |
| 18 | `NHOM_NH` | varchar2(140), optional |  | Nhóm ngân hàng được phân loại theo quy định nội bộ |
| 19 | `TEN_NHOM_NH` | varchar2(50), optional |  | Tên nhóm ngân hàng |
| 20 | `MA_NH` | varchar2(140), optional |  | Mã ngân hàng tương ứng trong hệ thống |
| 21 | `TEN_MA_NH` | varchar2(200), optional |  | Tên ngân hàng tương ứng |
| 22 | `MA_SPSB` | varchar2(140), optional |  | Mã phân loại sản phẩm/dịch vụ tín dụng |
| 23 | `TEN_MA_SPSB` | varchar2(200), optional |  | Tên sản phẩm/dịch vụ tín dụng |
| 24 | `NHOM_NO` | varchar2(12), optional |  | Nhóm nợ theo phân loại tín dụng |
| 25 | `GOC_QUA_HAN` | number(25,5), optional |  | Số tiền gốc quá hạn cần thu hồi |
| 26 | `LAI_QUA_HAN` | number(25,5), optional |  | Số tiền lãi quá hạn cần thu hồi |
| 27 | `LAI_PHAT_PE_PS` | number, optional |  | Số tiền phạt liên quan đến giao dịch tín dụng |
| 28 | `SO_NGAY_QUA_HAN` | number, optional |  | Số ngày khách hàng đã quá hạn thanh toán |
| 29 | `ACC_OFFICER` | varchar2(16), optional |  | Mã nhân viên quản lý tài khoản khách hàng |
| 30 | `ACC_OFFICER_NAME` | varchar2(50), optional |  | Tên nhân viên quản lý tài khoản khách hàng |
| 31 | `PORTFOLIO` | varchar2(200), optional |  | Danh mục tín dụng của khách hàng |
| 32 | `SEGMENT_CODE` | varchar2(200), optional |  | Mã phân khúc khách hàng |
| 33 | `SEGMENT_NAME` | varchar2(50), optional |  | Tên phân khúc khách hàng |
| 34 | `CAMPAIGN_ID` | varchar2(35), optional |  | Mã chiến dịch tín dụng hoặc tiếp thị liên quan |
| 35 | `CAMPAIGN_NAME` | varchar2(200), optional |  | Tên chiến dịch tín dụng hoặc tiếp thị |
| 36 | `SEAB_PARTNER` | varchar2(35), optional |  | Đối tác tài chính liên quan đến khoản vay |
| 37 | `MIS_DAO1` | varchar2(35), optional |  | Chỉ số quản lý rủi ro của hợp đồng tại thời điểm đáo hạn |
| 38 | `CURR_MIS_DAO` | varchar2(35), optional |  | Chỉ số quản lý rủi ro tại thời điểm hiện tại |
| 39 | `ADDITION_CODE` | varchar2(1000), optional |  | Mã bổ sung liên quan đến khoản vay |
| 40 | `ADDITION_VALUE` | varchar2(1000), optional |  | Giá trị bổ sung liên quan đến khoản vay |
| 41 | `SALE_TYPE` | varchar2(35), optional |  | Loại hình bán hàng |
| 42 | `SALE_ID` | varchar2(35), optional |  | Mã nhân viên kinh doanh hoặc đối tác bán hàng |
| 43 | `SALE_NAME` | varchar2(200), optional |  | Tên nhân viên kinh doanh hoặc đối tác bán hàng |
| 44 | `BROKER_TYPE` | varchar2(35), optional |  | Loại hình môi giới trong giao dịch tín dụng |
| 45 | `BROKER_ID` | varchar2(35), optional |  | Mã nhân viên hoặc đối tác môi giới |
| 46 | `BRKER_NAME` | varchar2(200), optional |  | Tên nhân viên hoặc đối tác môi giới |
| 47 | `CONTRACT_REF` | varchar2(80), optional |  | Mã hợp đồng tham chiếu liên quan đến khoản vay |
| 48 | `REF_VALUE_DATE` | date, optional |  | Ngày hiệu lực của hợp đồng tham chiếu |
| 49 | `REF_MAT_DATE` | date, optional |  | Ngày đáo hạn của hợp đồng tham chiếu |
| 50 | `REF_AMOUNT` | number, optional |  | Số tiền trong hợp đồng tham chiếu |
| 51 | `REF_CURRENCY` | varchar2(3), optional |  | Loại tiền tệ của hợp đồng tham chiếu |
| 52 | `SUB_PRODUCT` | varchar2(140), optional |  | Mã sản phẩm tín dụng phụ |
| 53 | `SUB_NAME` | varchar2(50), optional |  | Tên sản phẩm tín dụng phụ |
| 54 | `MIS_DAO1_NAME` | varchar2(4000), optional |  | Tên chỉ số quản lý rủi ro tại thời điểm đáo hạn |
| 55 | `CUR_MIS_DAO_NAME` | varchar2(4000), optional |  | Tên chỉ số quản lý rủi ro tại thời điểm hiện tại |
| 56 | `SO_TIEN_PE` | number(25,5), optional |  | Số tiền được ghi nhận trong kế hoạch thu hồi |
| 57 | `SO_TIEN_PS` | number(25,5), optional |  | Số tiền đã thu hồi thực tế |
---

---

## Bảng: FCT_XLN_BAD_DEBT

- **Schema:** XLN_DTM
- **Type:** FCT

### Dimension Dependencies (Đã xác nhận — từ DDD)
| FK Column | Dim Table | Dim PK |
|:----------|:----------|:-------|
| `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` |
| `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` |
| `PRODUCT_SK` | `DIM_XLN_PRODUCT` | `DIMENSION_KEY` |

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:---:|:---|:---|:---|:---|
| 1 | `DAYID` | DATE | PK | Ngày dữ liệu |
| 2 | `CONTRACT_MD` | VARCHAR2(100) | PK | Mã hợp đồng MD của khoản nợ ngoại bảng |
| 3 | `CUSTOMER_ID` | VARCHAR2(50) |  | Mã khách hàng |
| 4 | `CATEGORY` | VARCHAR2(100) |  | Mã category của khoản MD |
| 5 | `CCY` | VARCHAR2(100) |  | Loại tiền |
| 6 | `PRINCIPAL_AMT` | NUMBER |  | Giá trị của khoản nợ ngoại bảng |
| 7 | `CO_CODE` | VARCHAR2(50) |  | Chi nhánh quản lý khoản nợ ngoại bảng |
| 8 | `REC_STATUS` | VARCHAR2(5) |  | Trạng thái khoản nợ ngoại bảng |
| 9 | `VALUE_DATE` | DATE |  | Ngày ghi nhận ngoại bảng |
| 10 | `CUSTOMER_SK` | VARCHAR2(30) | FK | Surrogate Key khách hàng, mapping sang `DIM_XLN_CUST` |
| 11 | `COMPANY_SK` | NUMBER | FK | Surrogate Key công ty, mapping sang `DIM_XLN_COMPANY` |
| 12 | `PRODUCT_SK` | NUMBER | FK | Surrogate Key sản phẩm, mapping sang `DIM_XLN_PRODUCT` |
| 13 | `FIRST_PRINCIPAL_AMT` | NUMBER |  | Giá trị ban đầu của khoản nợ ngoại bảng |
---

---

## Bảng: FCT_XLN_CREDIT_FEE

- **Schema:** XLN_DTM
- **Type:** FCT

### Dimension Dependencies (Đã xác nhận — từ DDD)
| FK Column | Dim Table | Dim PK |
|:----------|:----------|:-------|
| `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` |
| `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` |

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:---:|:---|:---|:---|:---|
| 1 | `DAYID` | DATE | PK | Ngày dữ liệu |
| 2 | `ENTRY_ID` | VARCHAR2(100) | PK | Mã bút toán giao dịch |
| 3 | `CUSTOMER` | VARCHAR2(50) |  | Mã khách hàng |
| 4 | `PL_CATEGORY` | VARCHAR2(100) |  | Mã PL |
| 5 | `TRANS_CODE` | VARCHAR2(100) |  | Mã hợp đồng khoản vay |
| 6 | `CCY` | VARCHAR2(5) |  | Loại tiền |
| 7 | `COMPANY` | VARCHAR2(30) |  | Mã chi nhánh thực hiện giao dịch |
| 8 | `FEE_AMT` | NUMBER |  | Số tiền phí nguyên tệ |
| 9 | `FEE_AMT_LCY` | NUMBER |  | Số tiền phí quy đổi |
| 10 | `FEE_NAME` | VARCHAR2(100) |  | Diễn giải thu phí |
| 11 | `FEE_ID` | VARCHAR2(50) |  | Mã phí |
| 12 | `CUSTOMER_NAME` |  |  | Tên khách hàng |
| 13 | `COMPANY_NAME` |  |  | Tên chi nhánh |
| 14 | `CUSTOMER_SK` | NUMBER | FK | Surrogate Key khách hàng, mapping sang `DIM_XLN_CUST` |
| 15 | `COMPANY_SK` | NUMBER | FK | Surrogate Key công ty, mapping sang `DIM_XLN_COMPANY` |

---

---

## Bảng: FCT_XLN_INT_WRITE_OFF

- **Schema:** XLN_DTM
- **Type:** FCT

### Dimension Dependencies (Đã xác nhận — từ DDD)
| FK Column | Dim Table | Dim PK |
|:----------|:----------|:-------|
| `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` |
| `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` |

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:---:|:---|:---|:---|:---|
| 1 | `DAYID` | DATE | PK | Ngày dữ liệu |
| 2 | `ENTRY_ID` | VARCHAR2(100) | PK | Mã bút toán giao dịch |
| 3 | `CUSTOMER_ID` | VARCHAR2(50) |  | Mã khách hàng |
| 4 | `PL_CATEGORY` | VARCHAR2(100) |  | Mã PL |
| 5 | `AMOUNT` | VARCHAR2(100) |  | Số tiền thoái lãi nguyên tệ |
| 6 | `AMOUNT_LCY` | NUMBER |  | Số tiền thoái lãi quy đổi |
| 7 | `CURRENCY` | NUMBER |  | Loại tiền |
| 8 | `NARRATIVE` | VARCHAR2(5) |  | Diễn giải chi tiết bút toán thoái lãi |
| 9 | `NARRATIVE_ALL` | VARCHAR2(50) |  | Diễn giải chi tiết bút toán thoái lãi |
| 10 | `COMPANY_CODE` | VARCHAR2(30) |  | Mã chi nhánh thực hiện giao dịch |
| 11 | `CUSTOMER_NAME` |  |  |  |
| 12 | `COMPANY_NAME` |  |  |  |
| 13 | `CUSTOMER_SK` | NUMBER | FK | Surrogate Key khách hàng, mapping sang `DIM_XLN_CUST` |
| 14 | `COMPANY_SK` | NUMBER | FK | Surrogate Key công ty, mapping sang `DIM_XLN_COMPANY` |
---

---

## Bảng: FCT_XLN_LOAN_TXN

- **Schema:** XLN_DTM
- **Type:** FCT

### Dimension Dependencies (Đã xác nhận — từ DDD)
| FK Column | Dim Table | Dim PK |
|:----------|:----------|:-------|
| `XLN_CONTRACT_SK` | `DIM_XLN_CONTRACT` | `DIMENSION_ID` |
| `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` |
| `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` |
| `PRODUCT_SK` | `DIM_XLN_PRODUCT` | `DIMENSION_KEY` |

### Dimension Dependencies (AI Inferred — chưa xác nhận)

> 🤖 **[AI PHÂN TÍCH — cần review trước khi dùng làm nguồn chân lý]**
> Dựa trên: phân tích `_SK` columns từ DDD và suy luận ngữ nghĩa.
>
> | FK Column | → DIM Table | DIM PK | Nguồn |
> |:----------|:-----------|:-------|:------|
> | `SEAB_PRODUCTS_SK` | `DIM_XLN_SEAB_PRODUCT` | `DIMENSION_KEY` | SK pattern |

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:---:|:---|:---|:---|:---|
| 1 | `DAYID` | DATE | PK | Ngày dữ liệu |
| 2 | `CUSTOMER` | VARCHAR2(50) |  | Mã khách hàng gắn với khoản vay |
| 3 | `CONTRACT_MAIN` | VARCHAR2(50) |  | Mã hợp đồng chính |
| 4 | `CONTRACT` | VARCHAR2(50) | PK | Mã hợp đồng |
| 5 | `CURRENCY` | VARCHAR2(50) |  | Loại tiền |
| 6 | `TRANS_DATE` | DATE |  | Ngày phát sinh giao dịch |
| 7 | `TRANS_CODE` | NUMBER(25,0) | PK | Mã giao dịch |
| 8 | `TRANS_AMOUNT_LCY` |  |  | Số tiền giao dịch quy đổi |
| 9 | `PRIN_BALANCE` | NUMBER(25,0) |  | Tổng dư nợ gốc của hợp đồng |
| 10 | `PRIN_OVERDUE` | NUMBER(25,0) |  | Tổng dư nợ gốc quá hạn của hợp đồng |
| 11 | `IN_OVERDUE` | NUMBER(25,0) |  | Tổng dư nợ lãi quá hạn của hợp đồng |
| 12 | `PE` | NUMBER(25,0) |  | Dư nợ lãi phạt PE |
| 13 | `PS` | NUMBER(25,0) |  | Dư nợ lãi phạt PS |
| 14 | `PE_PS` | NUMBER(25,0) |  | Tổng dư nợ lãi phạt PE, PS |
| 15 | `NO_DAY_OVERDUE` | NUMBER(25,0) |  | Số ngày quá hạn của hợp đồng vay |
| 16 | `CO_CODE` | VARCHAR2(50) |  | Chi nhánh quản lý khoản vay KH |
| 17 | `CATEGORY` | VARCHAR2(50) |  | Mã category của khoản vay |
| 18 | `SEAB_PRODUCTS` | VARCHAR2(50) |  | Mã sản phẩm của khoản vay theo nhóm sản phẩm của SeABank |
| 19 | `PRODUCT` | VARCHAR2(50) |  | Mã sản phẩm của khoản vay |
| 20 | `CLASSIFICATION` | VARCHAR2(12) |  | Nhóm nợ khoản vay |
| 21 | `SEAB_PARTNER` | VARCHAR2(35) |  | Đánh dấu đối tác SeABank |
| 22 | `MIS_DAO` | VARCHAR2(35) |  | Mã định danh khách hàng |
| 23 | `CURR_MIS_DAO` | VARCHAR2(35) |  | Mã định danh khách hàng hiện tại |
| 24 | `MIS_DAO1_NAME` | VARCHAR2(50) |  | Mô tả mã định danh KH |
| 25 | `CUR_MIS_DAO_NAME` | VARCHAR2(50) |  | Mô tả mã định danh KH hiện tại |
| 26 | `ADDITION_CODE` | NUMBER(19,0) |  | Thông tin tùy biến thêm của hợp đồng |
| 27 | `ADDITION_VALUE` | NUMBER(19,0) |  | Thông tin tùy biến thêm của hợp đồng |
| 28 | `SALE_TYPE` | VARCHAR2(35) |  | Phân loại nhân viên phụ trách khoản vay |
| 29 | `SALE_ID` | VARCHAR2(35) |  | Mã nhân viên phụ trách khoản vay |
| 30 | `BROKER_TYPE` | VARCHAR2(35) |  | Phân loại nhân viên môi giới |
| 31 | `BROKER_ID` | VARCHAR2(35) |  | Mã nhân viên môi giới |
| 32 | `CAMPAIGN_ID` | VARCHAR2(35) |  | Mã chiến dịch gắn với khoản vay |
| 33 | `CAMPAIGN_NAME` | VARCHAR2(100) |  | Tên chiến dịch gắn với khoản vay |
| 34 | `SUB_PRODUCT` | VARCHAR2(50) |  | Mã sản phẩm cấp 2 của khoản vay |
| 35 | `SUB_PRODUCT_NAME` | VARCHAR2(50) |  | Tên sản phẩm cấp 2 của khoản vay |
| 36 | `SUB_CATEGORY` | VARCHAR2(50) |  | Mã ngành hàng |
| 37 | `SUB_CATEGORY_NAME` | VARCHAR2(50) |  | Tên ngành hàng |
| 38 | `XLN_CONTRACT_SK` | NUMBER | FK | Surrogate Key hợp đồng, mapping sang `DIM_XLN_CONTRACT` |
| 39 | `CONTRACT_SK` |  | FK | Surrogate Key hợp đồng |
| 40 | `CUSTOMER_SK` | NUMBER | FK | Surrogate Key khách hàng, mapping sang `DIM_XLN_CUST` |
| 41 | `COMPANY_SK` | NUMBER | FK | Surrogate Key công ty, mapping sang `DIM_XLN_COMPANY` |
| 42 | `SEAB_PRODUCTS_SK` | NUMBER | FK | Surrogate Key sản phẩm SeABank, mapping sang `DIM_XLN_SEAB_PRODUCT` |
| 43 | `PRODUCT_SK` | NUMBER | FK | Surrogate Key sản phẩm |
| 44 | `CATEGORY_SK` |  | FK | Surrogate Key category |
| 45 | `SALE_NAME` | VARCHAR2(100) |  | Tên nhân viên phụ trách khoản vay |
| 46 | `BROKER_NAME` | VARCHAR2(100) |  | Tên nhân viên môi giới |
| 47 | `SOURCE` | VARCHAR2(10) |  | Phân hệ khoản vay: LD, MG, VS, PD |
| 48 | `TRANS_AMOUNT` |  |  | Số tiền giao dịch |
---

---

## Bảng: DIM_XLN_BUCKET

- **Schema:** XLN_DTM
- **Type:** DIM

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:----|:--------|:-------------|:-----|:----------------|
| 1 | `DIMENSION_ID` | NUMBER |  | Surrogate Key |
| 2 | `OVD_NO` | NUMBER(10,0) |  | Số ngày quá hạn |
| 3 | `BUCKET_CODE` | VARCHAR2(50) |  | Mã bucket theo từng mốc 30 ngày (B0, B1, B2…) |
| 4 | `SBV_GROUP` | VARCHAR2(50) |  | Nhóm nợ theo ngân hàng nhà nước |
| 5 | `DESCRIPTION` | VARCHAR2(100) |  | Diễn giải |
| 6 | `EFF_DATE` | DATE |  | Ngày hiệu lực bản ghi |
| 7 | `EXP_DATE` | DATE |  | Ngày hết hiệu lực bản ghi |

---

---

## Bảng: DIM_XLN_CALENDAR

- **Schema:** XLN_DTM
- **Type:** DIM

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:----|:--------|:-------------|:-----|:----------------|
| 1 | `DIMENSION_ID` | NUMBER(25,0) |  | Surrogate Key |
| 2 | `DAYID` | DATE |  | Ngày tháng năm |
| 3 | `DAY` | NUMBER(19,0) |  | Ngày |
| 4 | `MONTH` | NUMBER(19,0) |  | Tháng |
| 5 | `YEAR` | NUMBER(19,0) |  | Năm |
| 6 | `HOLIDAY` | NUMBER(19,0) |  | Check ngày nghỉ |
| 7 | `NO_DAY_MTD` | NUMBER(19,0) |  | Số ngày trong tháng tính tới ngày dayid |
| 8 | `NO_DAY_YTD` | NUMBER(19,0) |  | Số ngày trong năm tính tới ngày dayid |
| 9 | `DAY_NAME` | VARCHAR2(50) |  | Thứ trong tuần |
| 10 | `LAST_DAY_OF_MONTH` | DATE |  | Ngày cuối tháng |
| 11 | `NO_DAY_OF_MONTH` | NUMBER(19,0) |  | Tổng số ngày trong tháng |
| 12 | `NO_DAY_OF_QUARTER` | NUMBER(19,0) |  | Tổng số ngày trong quý |
| 13 | `NO_DAY_OF_YEAR` | NUMBER(19,0) |  | Tổng số ngày trong năm |

---

---

## Bảng: DIM_XLN_CARD

- **Schema:** XLN_DTM
- **Type:** DIM

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:---:|:---|:---|:---|:---|
| 1 | `DIMENSION_KEY` | NUMBER |  | Surrogate Key |
| 2 | `CARD_ID` | VARCHAR2(100) |  | Mã thẻ |
| 3 | `MAIN_ID` | VARCHAR2(50) |  | ID bản ghi mở thẻ chính trên T24 |
| 4 | `VALUE_DATE` |  |  | Ngày mở thẻ |
| 5 | `CARD_STATUS` | VARCHAR2(50) |  | Trạng thái thẻ (lấy thông tin thẻ chính) |
| 6 | `CARD_TYPE` | VARCHAR2(50) |  | Loại thẻ |
| 7 | `LIMIT_DES` | VARCHAR2(55) |  | Mã chính sách |
| 8 | `EFF_DATE` | DATE |  | Ngày hiệu lực bản ghi |
| 9 | `EXP_DATE` | DATE |  | Ngày hết hiệu lực bản ghi |
| 10 | `CUSTOMER_ID` |  |  | Mã khách hàng |
| 11 | `CARD_EXPIRE` |  |  | Ngày hết hạn thẻ |
| 12 | `ACCOUNT_ID` |  |  | Mã tài khoản liên kết với thẻ |
---

---

## Bảng: DIM_XLN_SALECODE

- **Schema:** XLN_DTM
- **Type:** DIM

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:----|:--------|:-------------|:-----|:----------------|
| 1 | `DIMENSION_KEY` | NUMBER(25,0) |  | Surrogate Key |
| 2 | `SALES_ID` | VARCHAR2(200) |  | ID Sale quản lý khoản vay |
| 3 | `SALES_NAME` | VARCHAR2(255) |  | Tên CBNV |
| 4 | `SALES_CONTACT` | VARCHAR2(40) |  | Số điện thoại Sale |
| 5 | `T24_USER_NAME` | VARCHAR2(50) |  | User Id trên hệ thống T24 |
| 6 | `SB_ID` | VARCHAR2(50) |  | Mã SB ID của CBNV |
| 7 | `STATUS_DATE` | DATE |  | Ngày nhân viên onboard |
| 8 | `EMPLOYMENT` | VARCHAR2(50) |  | Nhân viên đã nghỉ việc hay vẫn làm việc? |
| 9 | `EXP_DATE` | DATE |  | Ngày hết hiệu lực bản ghi |
| 10 | `EFF_DATE` | DATE |  | Ngày hiệu lực bản ghi |
---

---

## Bảng: FCT_XLN_ACTIVE_LOAN

- **Schema:** XLN_DTM
- **Type:** FCT

### Dimension Dependencies (Đã xác nhận — từ DDD)
| FK Column | Dim Table | Dim PK |
|:----------|:----------|:-------|
| `CONTRACT_SK` | `DIM_XLN_CONTRACT` | `DIMENSION_ID` |
| `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` |
| `PRODUCT_SK` | `DIM_XLN_PRODUCT` | `DIMENSION_KEY` |
| `BUCKET_SK` | `DIM_XLN_BUCKET` | `DIMENSION_ID` |
| `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` |
| `CARD_SK` | `DIM_XLN_CARD` | `DIMENSION_KEY` |
| `SALES_SK` | `DIM_XLN_SALECODE` | `DIMENSION_KEY` |

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:----|:--------|:-------------|:-----|:----------------|
| 1 | `DAYID` | DATE | PK | Ngày dữ liệu |
| 2 | `CONTRACT` | VARCHAR2(50) | PK | Mã hợp đồng gốc (main Contract) và hợp đồng quá hạn (trong trường hợp hợp đồng quá hạn không gắn với hợp đồng trong hạn) |
| 3 | `PD_CONTRACT` | VARCHAR2(50) |  | Mã hợp đồng chuyển quá hạn |
| 4 | `DISBURSEMENT_AMT` | NUMBER(25,0) |  | Tổng số tiền giải ngân đến ngày dữ liệu |
| 5 | `NO_DAYS_OVERDUE` | NUMBER(10,0) |  | Số ngày quá hạn đến ngày dữ liệu |
| 6 | `PD_NO` | NUMBER(10,0) |  | Số lần KH phát sinh quá hạn kể từ thời điếm giải ngân |
| 7 | `BALANCE` | NUMBER(25,0) |  | Dư gốc trong hạn còn lại |
| 8 | `BALANCE_PD` | NUMBER(25,0) |  | Dư gốc quá hạn còn lại |
| 9 | `BALANCE_IN` | NUMBER(25,0) |  | Số tiền lãi trong hạn bị chuyển quá hạn |
| 10 | `BALANCE_PE` | NUMBER(25,0) |  | Số tiền lãi quá hạn PE |
| 11 | `BALANCE_PS` | NUMBER(25,0) |  | Số tiền lãi phạt quá hạn PS |
| 12 | `TOTAL_BALANCE` | NUMBER(25,0) |  | Tổng nợ gốc trong hạn và quá hạn |
| 13 | `TOTAL_EXPOSURE` | NUMBER(25,0) |  | Tổng nợ gốc lãi trong hạn và quá hạn |
| 14 | `TOTAL_OVD` | NUMBER(25,0) |  | Tổng nợ quá hạn |
| 15 | `DEBT_SETTLEMENT` | VARCHAR2(1) |  | Kiểm tra trạng thái KH đã được chuyển sang XLN khu vực theo dõi (có giá trị 1: thuộc phân luồng chuyển XLN, 0: không thuộc luồng chuyển) Mapping theo file excel thủ công do XLN cập nhật |
| 16 | `BOM_DPD` | NUMBER(10,0) |  | Số ngày quá hạn tại ngày đầu tháng |
| 17 | `YESTERDAY_DPD` | NUMBER(10,0) |  | Số ngày quá hạn tại ngày liền trước ngày chạy dữ liệu |
| 18 | `MAX_OVD` | NUMBER(10,0) |  | Số ngày quá hạn lớn nhất theo hợp đồng từ thời điểm giải ngân |
| 19 | `INTEREST` | NUMBER(25,5) |  | Lãi suất trong hạn |
| 20 | `OVD_RATE` | NUMBER(25,5) |  | Lãi suất quá hạn |
| 21 | `FIRST_ACTIVED_DATE` | DATE |  | Ngày thẻ Active lần đầu (nếu tồn tại nhiều thẻ cùng gắn với 1 TK trung gian thẻ à ưu tiên lấy thẻ chính, có trạng thái là CARD OK) |
| 22 | `LAST_ACTIVED_DATE` | DATE |  | Ngày thẻ Active lần gần nhất (nếu tồn tại nhiều thẻ cùng gắn với 1 TK trung gian thẻ à ưu tiên lấy thẻ chính, có trạng thái là CARD OK) |
| 23 | `CAMPAIGN_ID` | VARCHAR2(100) |  | Mã chương trình |
| 24 | `XLN_CONTRACT_SK` |  |  |  |
| 25 | `CUSTOMER_SK` | NUMBER(19,0) | FK | Surrogate Key Customer (mã khách hàng) Dùng mapping sang DIM_XLN_CUSTOMER + DIM_XLN_CUSTOMER_PII |
| 26 | `PRODUCT_SK` | NUMBER(19,0) | FK | Surrogate Key Product (Mã sản phẩm) Dùng mapping sang DIM_XLN_PRODUCT |
| 27 | `BUCKET_SK` | NUMBER(19,0) | FK | Surrogate Key Contract (hợp đồng tín dụng) Dùng mapping sang DIM_XLN_LOAN |
| 28 | `COMPANY_SK` | NUMBER(19,0) | FK | Surrogate Key Bucket (nhóm nợ quản trị thu hồi nợ) Dùng mapping sang DIM_XLN_BUCKET |
| 29 | `CARD_SK` | NUMBER(19,0) | FK | Surrogate Key Card ID (số thẻ) Dùng mapping sang DIM_XLN_CARD |
| 30 | `SALES_SK` | NUMBER(19,0) | FK | Surrogate Key Salecode (nhân viên kinh doanh) Dùng mapping sang DIM_XLN_SALECODE |
| 31 | `CUSTOMER` |  |  |  |
| 32 | `COMPANY_CODE` |  |  |  |
| 33 | `MAX_OVD_IN_MONTH` |  |  |  |
---

---

## Bảng: FCT_XLN_REPAYSCHEDULE

- **Schema:** XLN_DTM
- **Type:** FCT

### Dimension Dependencies (Đã xác nhận — từ DDD)
| FK Column | Dim Table | Dim PK |
|:----------|:----------|:-------|
| `CUSTOMER_SK` | `DIM_XLN_CUST` | `DIMENSION_KEY` |
| `CONTRACT_SK` | `DIM_XLN_CONTRACT` | `DIMENSION_ID` |
| `COMPANY_SK` | `DIM_XLN_COMPANY` | `DIMENSION_KEY` |
| `SALES_SK` | `DIM_XLN_SALECODE` | `DIMENSION_KEY` |

### Column Definitions (từ DDD)
| STT | Tên cột | Kiểu dữ liệu | Khóa | Mô tả nghiệp vụ |
|:----|:--------|:-------------|:-----|:----------------|
| 1 | `DAYID` | DATE | PK | Ngày dữ liệu |
| 2 | `CONTRACT` | VARCHAR2(50) | PK | Số hợp đồng đến hạn trả nợ. |
| 3 | `REPAYMENT_TYPE` | VARCHAR2(50) | PK | Loại trả nợ |
| 4 | `REPAYMENT_DATE` | DATE |  | Ngày trả nợ |
| 5 | `REPAYMENT_AMT` | NUMBER(25,0) |  | Số tiền trả |
| 6 | `REPAYMENT_ACCT` | VARCHAR2(50) |  | Tài khoản trả nợ gốc/lãi/phí tương ứng với từng kiểu trả nợ |
| 7 | `PAY_ACCT_BAL` | NUMBER(25,0) |  | Số dư của TK trả nợ tại ngày chạy dữ liệu |
| 8 | `SCH_FREQ` | VARCHAR2(50) |  | Tần suất trả nợ |
| 9 | `SCH_FREQ_CODE` | VARCHAR2(50) |  | Mã tần suất trả nợ |
| 10 | `BALANCE` | NUMBER(25,0) |  | Dư gốc trong hạn còn lại |
| 11 | `BALANCE_PD` | NUMBER(25,0) |  | Dư gốc quá hạn còn lại |
| 12 | `BALANCE_IN` | NUMBER(25,0) |  | Số tiền lãi trong hạn bị chuyển quá hạn |
| 13 | `BALANCE_PE` | NUMBER(25,0) |  | Số tiền lãi quá hạn PE |
| 14 | `BALANCE_PS` | NUMBER(25,0) |  | Số tiền lãi phạt quá hạn PS |
| 15 | `BAL_PD_TOTAL` | NUMBER(25,0) |  | Tổng số tiền quá hạn |
| 16 | `CUSTOMER_SK` | NUMBER(19,0) | FK | Surrogate Key Customer (mã khách hàng) Dùng mapping sang DIM_XLN_CUSTOMER |
| 17 | `XLN_CONTRACT_SK` |  |  |  |
| 18 | `COMPANY_SK` | NUMBER(19,0) | FK | Surrogate Key Customer (mã khách hàng) Dùng mapping sang DIM_XLN_COMPANY |
| 19 | `SALES_SK` | NUMBER(19,0) | FK | Surrogate Key Customer (mã khách hàng) Dùng mapping sang DIM_XLN_SALECODE |
---