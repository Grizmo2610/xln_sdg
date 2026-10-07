# =============================================================================
# schema/columns.py
# All column names as Python constants.
# Source of truth: DDD-Thiết kế chi tiết datamart XLN V1.0 phase 2
# =============================================================================

# ---------------------------------------------------------------------------
# Surrogate / dimension keys
# ---------------------------------------------------------------------------
DIM_KEY             = "DIMENSION_KEY"       # Generic surrogate key (most DIM tables)
DIM_ID              = "DIMENSION_ID"        # Surrogate key variant (BUCKET, CONTRACT, CALENDAR)

# ---------------------------------------------------------------------------
# Common temporal columns
# ---------------------------------------------------------------------------
DAYID               = "DAYID"
EFF_DATE            = "EFF_DATE"
EXP_DATE            = "EXP_DATE"
LOAD_DATE           = "LOAD_DATE"

# ---------------------------------------------------------------------------
# DIM_XLN_CUST
# ---------------------------------------------------------------------------
CUST_KEY            = "DIMENSION_KEY"
CUSTOMER            = "CUSTOMER"
SHORT_NAME          = "SHORT_NAME"
CUSTOMER_CLASS      = "CUSTOMER_CLASS"
CONTACT_DATE        = "CONTACT_DATE"
PORTFOLIO           = "PORTFOLIO"
DISTRICT_CODE       = "DISTRICT_CODE"
DISTRICT_NAME       = "DISTRICT_NAME"
CITY_CODE           = "CITY_CODE"
CITY_NAME           = "CITY_NAME"
STATUS_DATE         = "STATUS_DATE"
EMPLOYMENT          = "EMPLOYMENT"
CUSTOMER_GROUP      = "CUSTOMER_GROUP"
SEAB_CU_SEGMENT     = "SEAB_CU_SEGMENT"
SECTOR              = "SECTOR"
ACCOUNT_OFFICER     = "ACCOUNT_OFFICER"
ACCOUNT_OFFICER_NAME = "ACCOUNT_OFFICER_NAME"

# ---------------------------------------------------------------------------
# DIM_XLN_CUST_PII
# ---------------------------------------------------------------------------
DATE_OF_BIRTH       = "DATE_OF_BIRTH"
GENDER              = "GENDER"
LEGAL_ID            = "LEGAL_ID"
LEGAL_DOC_NAME      = "LEGAL_DOC_NAME"
LEGAL_ISS_DATE      = "LEGAL_ISS_DATE"
PHONE_T24           = "PHONE_T24"
EMAIL_T24           = "EMAIL_T24"
ADDRESS_T24         = "ADDRESS_T24"
SB_ID               = "SB_ID"

# ---------------------------------------------------------------------------
# DIM_XLN_CONTRACT
# ---------------------------------------------------------------------------
CONTRACT_ID         = "DIMENSION_ID"        # Surrogate key for contract
CONTRACT            = "CONTRACT"
DATASOURCE          = "DATASOURCE"
CONTRACT_REF        = "CONTRACT_REF"
CATEGORY            = "CATEGORY"
CURRENCY            = "CURRENCY"
COLLATERAL_DESC     = "COLLATERAL_DESC"
VALUE_DATE          = "VALUE_DATE"
MATURITY_DATE       = "MATURITY_DATE"
INT_LIQ_ACCT        = "INT_LIQ_ACCT"
MORTGAGE_ACCOUNT    = "MORTGAGE_ACCOUNT"
CHRG_LIQ_ACCT       = "CHRG_LIQ_ACCT"
SECURED             = "SECURED"
CO_CODE             = "CO_CODE"
REMARKS             = "REMARKS"
FREQUENCY           = "FREQUENCY"
FREQUENCY_DAY       = "FREQUENCY_DAY"
FREQUENCY_PR        = "FREQUENCY_PR"
TERM                = "TERM"
LIMIT_REF           = "LIMIT_REF"
SEAB_LOS_ID         = "SEAB_LOS_ID"
REF_CONTRACT_REF    = "REF_CONTRACT_REF"
SOURCE_TYPE         = "SOURCE_TYPE"
CAMPAIGN_ID         = "CAMPAIGN_ID"
REF_VALUE_DATE      = "REF_VALUE_DATE"
REF_MAT_DATE        = "REF_MAT_DATE"
REF_CONTRACT_AMT    = "REF_CONTRACT_AMT"
REF_CONTRACT_CCY    = "REF_CONTRACT_CCY"

# ---------------------------------------------------------------------------
# DIM_XLN_COMPANY
# ---------------------------------------------------------------------------
COMPANY_KEY         = "DIMENSION_KEY"
COMPANY_CODE        = "COMPANY_CODE"
COMPANY_NAME        = "COMPANY_NAME"
BRANCH_CODE         = "BRANCH_CODE"
BRANCH_NAME         = "BRANCH_NAME"
COMPANY_NAME_VN     = "COMPANY_NAME_VN"
BRANCH_CITY         = "BRANCH_CITY"
BRANCH_PROVINCE     = "BRANCH_PROVINCE"
REGION_CODE         = "REGION_CODE"
REGION_NAME         = "REGION_NAME"

# ---------------------------------------------------------------------------
# DIM_XLN_PRODUCT
# ---------------------------------------------------------------------------
PRODUCT_KEY         = "DIMENSION_KEY"
PRODUCT_CODE        = "PRODUCT_CODE"
PRODUCT_NAME        = "PRODUCT_NAME"
PRODUCT_GROUP       = "PRODUCT_GROUP"

# ---------------------------------------------------------------------------
# DIM_XLN_BUCKET
# ---------------------------------------------------------------------------
BUCKET_ID           = "DIMENSION_ID"
OVD_NO              = "OVD_NO"
BUCKET_CODE         = "BUCKET_CODE"
SBV_GROUP           = "SBV_GROUP"
DESCRIPTION         = "DESCRIPTION"

# ---------------------------------------------------------------------------
# DIM_XLN_CARD
# ---------------------------------------------------------------------------
CARD_KEY            = "DIMENSION_KEY"
CARD_ID             = "CARD_ID"
MAIN_ID             = "MAIN_ID"
CARD_STATUS         = "CARD_STATUS"
CARD_TYPE           = "CARD_TYPE"
LIMIT_DES           = "LIMIT_DES"
CUSTOMER_ID         = "CUSTOMER_ID"
CARD_EXPIRE         = "CARD_EXPIRE"
ACCOUNT_ID          = "ACCOUNT_ID"

# ---------------------------------------------------------------------------
# DIM_XLN_SALECODE
# ---------------------------------------------------------------------------
SALES_KEY           = "DIMENSION_KEY"
SALES_ID            = "SALES_ID"
SALES_NAME          = "SALES_NAME"
SALES_CONTACT       = "SALES_CONTACT"
T24_USER_NAME       = "T24_USER_NAME"
# SB_ID already defined above
# STATUS_DATE already defined above
# EMPLOYMENT already defined above

# ---------------------------------------------------------------------------
# DIM_XLN_LOAN_TXN_CODE
# ---------------------------------------------------------------------------
TXN_CODE_ID         = "ID"
TRANS_CODE          = "TRANS_CODE"
TRANS_NAME          = "TRANS_NAME"
TRANS_TYPE          = "TRANS_TYPE"
LOAN_TYPE           = "LOAN_TYPE"
TRANS_NAME_XLN      = "TRANS_NAME_XLN"

# ---------------------------------------------------------------------------
# DIM_XLN_CALENDAR
# ---------------------------------------------------------------------------
CAL_ID              = "DIMENSION_ID"
YEAR                = "YEAR"
MONTH               = "MONTH"
DAY                 = "DAY"
DAY_NAME            = "DAY_NAME"
HOLIDAY             = "HOLIDAY"
NO_DAY_MTD          = "NO_DAY_MTD"
NO_DAY_YTD          = "NO_DAY_YTD"
LAST_DAY_OF_MONTH   = "LAST_DAY_OF_MONTH"
NO_DAY_OF_MONTH     = "NO_DAY_OF_MONTH"
NO_DAY_OF_QUARTER   = "NO_DAY_OF_QUARTER"
NO_DAY_OF_YEAR      = "NO_DAY_OF_YEAR"

# ---------------------------------------------------------------------------
# FK columns used in FCT tables
# ---------------------------------------------------------------------------
CUSTOMER_SK         = "CUSTOMER_SK"
CONTRACT_SK         = "CONTRACT_SK"
XLN_CONTRACT_SK     = "XLN_CONTRACT_SK"    # FCT_XLN_LOAN_TXN uses this name
COMPANY_SK          = "COMPANY_SK"
PRODUCT_SK          = "PRODUCT_SK"
BUCKET_SK           = "BUCKET_SK"
CARD_SK             = "CARD_SK"
SALES_SK            = "SALES_SK"

# ---------------------------------------------------------------------------
# FCT_XLN_ACTIVE_LOAN — fact columns
# ---------------------------------------------------------------------------
PD_CONTRACT         = "PD_CONTRACT"
DISBURSEMENT_AMT    = "DISBURSEMENT_AMT"
NO_DAYS_OVERDUE     = "NO_DAYS_OVERDUE"
PD_NO               = "PD_NO"
BALANCE             = "BALANCE"
BALANCE_PD          = "BALANCE_PD"
BALANCE_IN          = "BALANCE_IN"
BALANCE_PE          = "BALANCE_PE"
BALANCE_PS          = "BALANCE_PS"
TOTAL_BALANCE       = "TOTAL_BALANCE"
TOTAL_EXPOSURE      = "TOTAL_EXPOSURE"
TOTAL_OVD           = "TOTAL_OVD"
DEBT_SETTLEMENT     = "DEBT_SETTLEMENT"
BOM_DPD             = "BOM_DPD"
YESTERDAY_DPD       = "YESTERDAY_DPD"
MAX_OVD             = "MAX_OVD"
INTEREST            = "INTEREST"
OVD_RATE            = "OVD_RATE"
FIRST_ACTIVED_DATE  = "FIRST_ACTIVED_DATE"
LAST_ACTIVED_DATE   = "LAST_ACTIVED_DATE"
MAX_OVD_IN_MONTH    = "MAX_OVD_IN_MONTH"

# ---------------------------------------------------------------------------
# FCT_XLN_REPAYSCHEDULE — fact columns
# ---------------------------------------------------------------------------
REPAYMENT_TYPE      = "REPAYMENT_TYPE"
REPAYMENT_DATE      = "REPAYMENT_DATE"
REPAYMENT_AMT       = "REPAYMENT_AMT"
REPAYMENT_ACCT      = "REPAYMENT_ACCT"
PAY_ACCT_BAL        = "PAY_ACCT_BAL"
SCH_FREQ            = "SCH_FREQ"
SCH_FREQ_CODE       = "SCH_FREQ_CODE"
BAL_PD_TOTAL        = "BAL_PD_TOTAL"

# ---------------------------------------------------------------------------
# FCT_XLN_LOAN_TXN — fact columns
# ---------------------------------------------------------------------------
CONTRACT_MAIN       = "CONTRACT_MAIN"
TRANS_DATE          = "TRANS_DATE"
TRANS_AMOUNT_LCY    = "TRANS_AMOUNT_LCY"
PRIN_BALANCE        = "PRIN_BALANCE"
PRIN_OVERDUE        = "PRIN_OVERDUE"
IN_OVERDUE          = "IN_OVERDUE"
PE                  = "PE"
PS                  = "PS"
PE_PS               = "PE_PS"
NO_DAY_OVERDUE      = "NO_DAY_OVERDUE"
CLASSIFICATION      = "CLASSIFICATION"
SEAB_PARTNER        = "SEAB_PARTNER"
MIS_DAO             = "MIS_DAO"
CURR_MIS_DAO        = "CURR_MIS_DAO"
MIS_DAO1_NAME       = "MIS_DAO1_NAME"
CUR_MIS_DAO_NAME    = "CUR_MIS_DAO_NAME"
ADDITION_CODE       = "ADDITION_CODE"
ADDITION_VALUE      = "ADDITION_VALUE"
SALE_TYPE           = "SALE_TYPE"
SALE_ID             = "SALE_ID"
SALE_NAME           = "SALE_NAME"
BROKER_TYPE         = "BROKER_TYPE"
BROKER_ID           = "BROKER_ID"
BROKER_NAME         = "BROKER_NAME"
SUB_PRODUCT         = "SUB_PRODUCT"
SUB_PRODUCT_NAME    = "SUB_PRODUCT_NAME"
SUB_CATEGORY        = "SUB_CATEGORY"
SUB_CATEGORY_NAME   = "SUB_CATEGORY_NAME"
SEAB_PRODUCTS       = "SEAB_PRODUCTS"
SEAB_PRODUCTS_SK    = "SEAB_PRODUCTS_SK"
CATEGORY_SK         = "CATEGORY_SK"
TRANS_AMOUNT        = "TRANS_AMOUNT"
SOURCE              = "SOURCE"

# ---------------------------------------------------------------------------
# FCT_XLN_CREDIT_FEE — fact columns
# ---------------------------------------------------------------------------
ENTRY_ID            = "ENTRY_ID"
PL_CATEGORY         = "PL_CATEGORY"
# TRANS_CODE already defined above
# COMPANY_CODE already defined above (CO_CODE is used in DIM; COMPANY_CODE in COMPANY)
COMPANY             = "COMPANY"
FEE_AMT             = "FEE_AMT"
FEE_AMT_LCY         = "FEE_AMT_LCY"
FEE_NAME            = "FEE_NAME"
FEE_ID              = "FEE_ID"
CUSTOMER_NAME       = "CUSTOMER_NAME"

# ---------------------------------------------------------------------------
# FCT_XLN_BAD_DEBT — fact columns
# ---------------------------------------------------------------------------
CONTRACT_MD         = "CONTRACT_MD"
CUSTOMER_ID_BD      = "CUSTOMER_ID"         # same col name, aliased to avoid clash
CCY                 = "CCY"
PRINCIPAL_AMT       = "PRINCIPAL_AMT"
REC_STATUS          = "REC_STATUS"
FIRST_PRINCIPAL_AMT = "FIRST_PRINCIPAL_AMT"

# ---------------------------------------------------------------------------
# FCT_XLN_INT_WRITE_OFF — fact columns
# ---------------------------------------------------------------------------
CUSTOMER_ID_IWO     = "CUSTOMER_ID"
AMOUNT              = "AMOUNT"
AMOUNT_LCY          = "AMOUNT_LCY"
NARRATIVE           = "NARRATIVE"
NARRATIVE_ALL       = "NARRATIVE_ALL"
COMPANY_CODE_IWO    = "COMPANY_CODE"        # raw company code (not FK)

# Raw product code column in FCT_XLN_LOAN_TXN (not same as PRODUCT_CODE in DIM)
PRODUCT             = "PRODUCT"
