from __future__ import annotations

import random
import string
from datetime import date, timedelta

import polars as pl

from engine.core.base import BaseGenerator
from engine.core.vn_faker import VietnameseFaker
from engine.core.sampling import SamplingEngine
from engine.config.random import rng as _rng

_ref_faker = VietnameseFaker(seed=99)
from engine.core.pool import PoolRegistry
from engine.schema.columns import (
    # DIM_XLN_COMPANY
    COMPANY_KEY, COMPANY_CODE, COMPANY_NAME, COMPANY_NAME_VN,
    BRANCH_CODE, BRANCH_NAME, BRANCH_CITY, BRANCH_PROVINCE,
    REGION_CODE, REGION_NAME,
    EFF_DATE, EXP_DATE,
    # DIM_XLN_PRODUCT
    PRODUCT_KEY, PRODUCT_CODE, PRODUCT_NAME, PRODUCT_GROUP,
    # DIM_XLN_SALECODE
    SALES_KEY, SALES_ID, SALES_NAME, SALES_CONTACT,
    T24_USER_NAME, SB_ID, STATUS_DATE, EMPLOYMENT,
)

# Chi nhánh thực tế của SeABank (representative sample)
# (city_code, city_name_vn, branch_code, branch_name_en, branch_name_vn, province, region_code, region_name)
_BRANCHES: list[tuple] = [
    ("HN",  "Hà Nội",      "HN01", "Hanoi Head Office",      "Hội sở Hà Nội",      "Hà Nội",   "R1", "Miền Bắc"),
    ("HN",  "Hà Nội",      "HN02", "Hanoi Dong Da Branch",   "Chi nhánh Đống Đa",   "Hà Nội",   "R1", "Miền Bắc"),
    ("HN",  "Hà Nội",      "HN03", "Hanoi Cau Giay Branch",  "Chi nhánh Cầu Giấy",  "Hà Nội",   "R1", "Miền Bắc"),
    ("HN",  "Hà Nội",      "HN04", "Hanoi Ha Dong Branch",   "Chi nhánh Hà Đông",   "Hà Nội",   "R1", "Miền Bắc"),
    ("HN",  "Hà Nội",      "HN05", "Hanoi Long Bien Branch", "Chi nhánh Long Biên",  "Hà Nội",   "R1", "Miền Bắc"),
    ("HP",  "Hải Phòng",   "HP01", "Hai Phong Branch",       "Chi nhánh Hải Phòng", "Hải Phòng","R1", "Miền Bắc"),
    ("TN",  "Thái Nguyên", "TN01", "Thai Nguyen Branch",     "Chi nhánh Thái Nguyên","Thái Nguyên","R1","Miền Bắc"),
    ("HCM", "TP.HCM",      "HCM01","HCM Head Office",        "Hội sở TP.HCM",       "TP.HCM",   "R2", "Miền Nam"),
    ("HCM", "TP.HCM",      "HCM02","HCM Quan 1 Branch",      "Chi nhánh Quận 1",    "TP.HCM",   "R2", "Miền Nam"),
    ("HCM", "TP.HCM",      "HCM03","HCM Binh Thanh Branch",  "Chi nhánh Bình Thạnh","TP.HCM",   "R2", "Miền Nam"),
    ("HCM", "TP.HCM",      "HCM04","HCM Thu Duc Branch",     "Chi nhánh Thủ Đức",   "TP.HCM",   "R2", "Miền Nam"),
    ("HCM", "TP.HCM",      "HCM05","HCM Go Vap Branch",      "Chi nhánh Gò Vấp",    "TP.HCM",   "R2", "Miền Nam"),
    ("DN",  "Đà Nẵng",     "DN01", "Da Nang Branch",         "Chi nhánh Đà Nẵng",   "Đà Nẵng",  "R3", "Miền Trung"),
    ("HUE", "Huế",         "HUE01","Hue Branch",             "Chi nhánh Huế",       "Thừa Thiên Huế","R3","Miền Trung"),
    ("CT",  "Cần Thơ",     "CT01", "Can Tho Branch",         "Chi nhánh Cần Thơ",   "Cần Thơ",  "R2", "Miền Nam"),
    ("BD",  "Bình Dương",  "BD01", "Binh Duong Branch",      "Chi nhánh Bình Dương","Bình Dương","R2", "Miền Nam"),
    ("BH",  "Biên Hòa",    "BH01", "Bien Hoa Branch",        "Chi nhánh Biên Hòa",  "Đồng Nai", "R2", "Miền Nam"),
    ("VT",  "Vũng Tàu",   "VT01", "Vung Tau Branch",        "Chi nhánh Vũng Tàu", "Bà Rịa-VT","R2", "Miền Nam"),
]

# Sản phẩm tín dụng — (product_code, product_name, product_group)
_PRODUCTS: list[tuple[str, str, str]] = [
    # Vay tiêu dùng
    ("TDCH",  "Vay tiêu dùng có tài sản bảo đảm",     "Vay tiêu dùng"),
    ("TDKCH", "Vay tiêu dùng không có tài sản bảo đảm","Vay tiêu dùng"),
    ("TDOTO", "Vay mua ô tô",                          "Vay tiêu dùng"),
    ("TDBD",  "Vay bất động sản",                      "Vay tiêu dùng"),
    # Vay kinh doanh
    ("KDNH",  "Vay ngắn hạn kinh doanh",               "Vay kinh doanh"),
    ("KDTH",  "Vay trung hạn kinh doanh",               "Vay kinh doanh"),
    ("KDDH",  "Vay dài hạn kinh doanh",                "Vay kinh doanh"),
    # Thẻ tín dụng
    ("VISA",  "Thẻ tín dụng Visa",                     "Thẻ tín dụng"),
    ("MC",    "Thẻ tín dụng Mastercard",               "Thẻ tín dụng"),
    ("NAPAS", "Thẻ tín dụng Napas",                    "Thẻ tín dụng"),
    # Mortgage
    ("MG",    "Vay thế chấp nhà",                      "Mortgage"),
    ("MGOTO", "Vay thế chấp ô tô",                     "Mortgage"),
    # Cán bộ nhân viên
    ("CBNV",  "Vay ưu đãi CBNV",                       "Vay CBNV"),
]

def _rand_id(prefix: str = "", n: int = 6) -> str:
    return prefix + "".join(random.choices(string.digits, k=n))

def _rand_phone() -> str:
    return "0" + "".join(random.choices(string.digits, k=9))

def _rand_name() -> str:
    return random.choice(_LAST_NAMES) + " " + random.choice(_FIRST_NAMES)

def _rand_date(start: date, end: date) -> date:
    delta = max((end - start).days, 0)
    return start + timedelta(days=random.randint(0, delta))

class ReferenceGenerator(BaseGenerator):
    """
    Sinh DIM_XLN_COMPANY, DIM_XLN_PRODUCT, DIM_XLN_SALECODE.

    - Không phụ thuộc pool nào.
    - generate() trả về dict[str, pl.DataFrame] với key "COMPANY", "PRODUCT", "SALECODE".
    - scd2_churn() dùng cho daily run: thêm nhân viên mới, trả về DataFrame
      chỉ chứa SALECODE rows mới (COMPANY và PRODUCT không thay đổi hàng ngày).

    Surrogate key offset:
        Caller truyền sk_offset_* để tránh trùng DIMENSION_KEY khi daily run
        thêm nhân viên mới vào bảng đã có data.
    """

    def required_pools(self) -> list[str]:
        return []   # hoàn toàn độc lập

    def generate(
        self,
        run_date: date,
        pool: PoolRegistry,
        n: int = 0,                     # unused — driven by _BRANCHES / _PRODUCTS
        n_sales: int = 50,              # số nhân viên kinh doanh cần sinh
        sk_offset_company: int = 0,
        sk_offset_product: int = 0,
        sk_offset_sales: int = 0,
    ) -> dict[str, pl.DataFrame]:
        """
        Sinh toàn bộ reference data một lần (seed time).

        Returns:
            {
                "COMPANY":  DataFrame cho DIM_XLN_COMPANY,
                "PRODUCT":  DataFrame cho DIM_XLN_PRODUCT,
                "SALECODE": DataFrame cho DIM_XLN_SALECODE,
            }
        """
        company_df  = self._gen_company(run_date, sk_offset_company)
        product_df  = self._gen_product(run_date, sk_offset_product)
        salecode_df = self._gen_salecode(run_date, n_sales, sk_offset_sales)

        return {
            "COMPANY":  company_df,
            "PRODUCT":  product_df,
            "SALECODE": salecode_df,
        }

    def scd2_churn(
        self,
        run_date: date,
        n_new: int = 2,
        sk_offset_sales: int = 0,
    ) -> pl.DataFrame:
        """
        Daily SCD2 churn — chỉ sinh thêm nhân viên mới cho SALECODE.
        COMPANY và PRODUCT không thay đổi hàng ngày.

        Returns:
            DataFrame mới cho DIM_XLN_SALECODE (chỉ rows mới, không phải toàn bộ).
        """
        return self._gen_salecode(run_date, n=n_new, sk_offset=sk_offset_sales)

    # Private generators

    @staticmethod
    def _gen_company(run_date: date, sk_offset: int) -> pl.DataFrame:
        """
        Mỗi branch trong _BRANCHES → 1 row DIM_XLN_COMPANY.
        COMPANY_CODE = BRANCH_CODE (đơn vị kinh doanh ≈ chi nhánh trong scope này).
        """
        rows = []
        for i, (city_code, city_name, branch_code, branch_name_en,
                branch_name_vn, province, region_code, region_name) in enumerate(_BRANCHES, start=1):
            rows.append({
                COMPANY_KEY:     sk_offset + i,
                COMPANY_CODE:    branch_code,
                COMPANY_NAME:    branch_name_en,
                COMPANY_NAME_VN: branch_name_vn,
                BRANCH_CODE:     branch_code,
                BRANCH_NAME:     branch_name_en,
                BRANCH_CITY:     city_code,
                BRANCH_PROVINCE: province,
                REGION_CODE:     region_code,
                REGION_NAME:     region_name,
                EFF_DATE:        date(2015, 1, 1),   # tất cả chi nhánh active từ 2015
                EXP_DATE:        None,
            })
        return pl.DataFrame(rows).with_columns(
            pl.col(COMPANY_KEY).cast(pl.Int64)
        )

    @staticmethod
    def _gen_product(run_date: date, sk_offset: int) -> pl.DataFrame:
        """
        Mỗi entry trong _PRODUCTS → 1 row DIM_XLN_PRODUCT.
        """
        rows = []
        for i, (code, name, group) in enumerate(_PRODUCTS, start=1):
            rows.append({
                PRODUCT_KEY:   sk_offset + i,
                PRODUCT_CODE:  code,
                PRODUCT_NAME:  name,
                PRODUCT_GROUP: group,
                EFF_DATE:      date(2015, 1, 1),
                EXP_DATE:      None,
            })
        return pl.DataFrame(rows).with_columns(
            pl.col(PRODUCT_KEY).cast(pl.Int64)
        )

    @staticmethod
    def _gen_salecode(run_date: date, n: int, sk_offset: int) -> pl.DataFrame:
        """
        Sinh n nhân viên kinh doanh mới → n rows DIM_XLN_SALECODE.
        onboard_date phân tán trong 3 năm trước run_date.
        """
        rows = []
        start_date = run_date - timedelta(days=3 * 365)
        for i in range(1, n + 1):
            onboard = _rand_date(start_date, run_date)
            is_active = float(_rng.random()) < 0.90      # 90% đang làm việc
            rows.append({
                SALES_KEY:     sk_offset + i,
                SALES_ID:      _rand_id("RM", 6),
                SALES_NAME:    str(_ref_faker.gen_full_name(_rng.choice(["M","F"], size=1))[0]),
                SALES_CONTACT: _rand_phone(),
                T24_USER_NAME: _rand_id("U", 6),
                SB_ID:         _rand_id("SB", 8),
                STATUS_DATE:   onboard,
                EMPLOYMENT:    "ACTIVE" if is_active else "RESIGNED",
                EFF_DATE:      onboard,
                EXP_DATE:      None if is_active else (onboard + timedelta(days=int(_rng.integers(90, 731)))),
            })
        return pl.DataFrame(rows).with_columns(
            pl.col(SALES_KEY).cast(pl.Int64)
        )
