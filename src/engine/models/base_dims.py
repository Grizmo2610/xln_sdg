from __future__ import annotations

from datetime import date

import holidays
import polars as pl

from engine.schema.columns import (
    # DIM_XLN_CALENDAR
    CAL_ID, DAYID, DAY, MONTH, YEAR, DAY_NAME, HOLIDAY,
    NO_DAY_MTD, NO_DAY_YTD,
    LAST_DAY_OF_MONTH, NO_DAY_OF_MONTH, NO_DAY_OF_QUARTER, NO_DAY_OF_YEAR,
    # DIM_XLN_BUCKET
    BUCKET_ID, OVD_NO, BUCKET_CODE, SBV_GROUP, DESCRIPTION,
    EFF_DATE, EXP_DATE,
    # DIM_XLN_LOAN_TXN_CODE
    TXN_CODE_ID, TRANS_CODE, TRANS_NAME, TRANS_TYPE, LOAN_TYPE, TRANS_NAME_XLN,
)

class CalendarDimLoader:
    """
    Generate all rows for DIM_XLN_CALENDAR between start_date and end_date.
    Marks Vietnamese public holidays using the `holidays` library.
    """

    def generate(self, start_date: date, end_date: date) -> pl.DataFrame:
        vn_holidays = holidays.Vietnam(years=range(start_date.year, end_date.year + 1))
        holiday_set = {d for d in vn_holidays}

        return (
            pl.DataFrame({DAYID: pl.date_range(start_date, end_date, interval="1d", eager=True)})
            .with_columns(
                pl.int_range(1, pl.len() + 1, dtype=pl.Int64).alias(CAL_ID),
                pl.col(DAYID).dt.day().alias(DAY),
                pl.col(DAYID).dt.month().alias(MONTH),
                pl.col(DAYID).dt.year().alias(YEAR),
                pl.col(DAYID).is_in(list(holiday_set)).cast(pl.Int8).alias(HOLIDAY),
                pl.col(DAYID).dt.day().alias(NO_DAY_MTD),
                pl.col(DAYID).dt.ordinal_day().alias(NO_DAY_YTD),
                pl.col(DAYID).dt.strftime("%A").alias(DAY_NAME),
                pl.col(DAYID).dt.month_end().alias(LAST_DAY_OF_MONTH),
                pl.col(DAYID).dt.month_end().dt.day().alias(NO_DAY_OF_MONTH),
                # Quarter day number: map quarter (1-4) to its first ordinal day
                # Q1→1, Q2→91/92, Q3→182/183, Q4→274/275 — approximate with fixed offsets
                # Exact: ordinal_day - (first day of quarter's ordinal - 1)
                (
                    pl.col(DAYID).dt.ordinal_day()
                    - (
                        pl.when(pl.col(DAYID).dt.quarter() == 1).then(pl.lit(0))
                        .when(pl.col(DAYID).dt.quarter() == 2).then(pl.lit(90))
                        .when(pl.col(DAYID).dt.quarter() == 3).then(pl.lit(181))
                        .otherwise(pl.lit(273))
                    )
                ).alias(NO_DAY_OF_QUARTER),
                pl.when(pl.col(DAYID).dt.is_leap_year())
                .then(pl.lit(366))
                .otherwise(pl.lit(365))
                .alias(NO_DAY_OF_YEAR),
            )
            .select([
                CAL_ID, DAYID, DAY, MONTH, YEAR, HOLIDAY,
                NO_DAY_MTD, NO_DAY_YTD, DAY_NAME,
                LAST_DAY_OF_MONTH, NO_DAY_OF_MONTH, NO_DAY_OF_QUARTER, NO_DAY_OF_YEAR,
            ])
        )

class BucketDimLoader:
    """
    Generate all rows for DIM_XLN_BUCKET.
    Each row maps an OVD day count to a bucket code (B00–B11+) and SBV group (G01–G05).
    Covers OVD 0 → 8000 days.
    """

    # (threshold_exclusive, bucket_code) — sorted ascending
    _BUCKET_BREAKS: list[tuple[int, str]] = [
        (30,   "B00"),
        (60,   "B01"),
        (90,   "B02"),
        (120,  "B03"),
        (150,  "B04"),
        (180,  "B05"),
        (210,  "B06"),
        (240,  "B07"),
        (270,  "B08"),
        (300,  "B09"),
        (330,  "B10"),
        (8001, "B11+"),
    ]

    # SBV group mapping — handled via pl.when chain (cut() requires unique labels)
    # OVD=0 → G01, 1-9 → G02, 10-29 → G03, 30-89 → G04, 90+ → G05
    _SBV_EXPR = (
        pl.when(pl.col("OVD_NO") == 0).then(pl.lit("G01"))
        .when(pl.col("OVD_NO") < 10).then(pl.lit("G02"))
        .when(pl.col("OVD_NO") < 30).then(pl.lit("G03"))
        .when(pl.col("OVD_NO") < 90).then(pl.lit("G04"))
        .otherwise(pl.lit("G05"))
    )

    _MAX_OVD = 8000
    _SEED_EFF_DATE = date(2023, 1, 1)

    def generate(self) -> pl.DataFrame:
        df = pl.DataFrame({OVD_NO: pl.arange(0, self._MAX_OVD + 1, eager=True)})

        bucket_thresholds, bucket_labels = zip(*self._BUCKET_BREAKS)

        return (
            df.with_columns(
                # BUCKET_CODE
                pl.col(OVD_NO)
                .cut(
                    breaks=list(bucket_thresholds[:-1]),
                    labels=list(bucket_labels),
                    left_closed=True,
                )
                .alias(BUCKET_CODE),

                # SBV_GROUP — when chain (cut() disallows duplicate labels)
                self._SBV_EXPR.alias(SBV_GROUP),

                # DESCRIPTION
                pl.when(pl.col(OVD_NO) == 0)
                .then(pl.lit("Current (0 days overdue)"))
                .otherwise(
                    pl.concat_str([
                        pl.lit("Overdue "),
                        pl.col(OVD_NO).cast(pl.Utf8),
                        pl.lit(" days"),
                    ])
                )
                .alias(DESCRIPTION),

                pl.lit(self._SEED_EFF_DATE).alias(EFF_DATE),
                pl.lit(None, dtype=pl.Date).alias(EXP_DATE),

                pl.int_range(1, pl.len() + 1, dtype=pl.Int64).alias(BUCKET_ID),
            )
            .select([BUCKET_ID, OVD_NO, BUCKET_CODE, SBV_GROUP, DESCRIPTION, EFF_DATE, EXP_DATE])
        )

class LoanTxnCodeDimLoader:
    """
    Generate static lookup rows for DIM_XLN_LOAN_TXN_CODE.
    These are fixed transaction type definitions — no FK deps, no daily changes.
    """

    # (ID, TRANS_CODE, TRANS_NAME, TRANS_TYPE, LOAN_TYPE, TRANS_NAME_XLN)
    _ROWS: list[tuple] = [
        (1,  130, "Thu goc trong han (VS)",             "PR",         "VS", "Thu goc trong han (VS)"),
        (2,  131, "Thu no truoc han the visa",          "PR",         "VS", "Thu no truoc han the visa"),
        (3,  133, "Giai ngan (VS)",                     "DIS",        "VS", "Giai ngan (VS)"),
        (4,  135, "Giai ngan (VS)",                     "DIS",        "VS", "Giai ngan (VS)"),
        (5,  136, "Thu goc trong han (VS)",             "PR",         "VS", "Thu goc trong han (VS)"),
        (6,  137, "Thu lai trong han (VS)",             "IN",         "VS", "Thu lai the visa"),
        (7,  138, "Thu lai trong han (VS)",             "IN",         "VS", "Thu lai the visa"),
        (8,  139, "Lai gd sale the visa",               "IN",         "VS", "Lai gd sale the visa"),
        (9,  392, "Giai ngan (VS)",                     "DIS",        "VS", "Giai ngan (VS)"),
        (10, 78,  "TT giao dich Sale the visa",         "PR",         "VS", "TT giao dich Sale the visa"),
        (11, 402, "Giai ngan (LD)",                     "DIS",        "",   "Giai ngan"),
        (12, 408, "Giai ngan",                          "DIS",        "",   "Giai ngan"),
        (13, 420, "Thu goc trong han (LD)",             "PR",         "",   "Thu goc trong han"),
        (14, 423, "Thu goc som 1 phan (LD)",            "PR",         "",   "Giam goc vay"),
        (15, 434, "Thu lai trong han (LD)",             "IN",         "",   "Thu lai trong han"),
        (16, 750, "Thu goc qua han",                    "OVERDUE_PR", "",   "Thu goc qua han (PR)"),
        (17, 751, "Thu lai cham tra (IN)",              "OVERDUE_IN", "",   "Thu lai qua han (IN)"),
        (18, 752, "Thu lai qua han (PE)",               "OVERDUE_PE", "",   "Thu lai phat PE"),
        (19, 753, "Thu lai phat qua han (PS)",          "OVERDUE_PS", "",   "Thu lai phat PS"),
        (20, 800, "Giai ngan, giai ngan bo sung (MG)",  "DIS",        "",   "Giai ngan"),
        (21, 802, "Thu goc trong han (MG) (theo lich)", "PR",         "",   "Thu goc trong han"),
        (22, 804, "Thu lai trong han (MG)",             "IN",         "",   "Thu lai trong han"),
        (23, 810, "Thu goc som 1 phan/tat toan (MG)",   "PR",         "",   "Giam goc vay"),
    ]

    def generate(self) -> pl.DataFrame:
        return pl.DataFrame(
            self._ROWS,
            schema=[TXN_CODE_ID, TRANS_CODE, TRANS_NAME, TRANS_TYPE, LOAN_TYPE, TRANS_NAME_XLN],
            orient="row",
        ).with_columns(
            pl.col(TXN_CODE_ID).cast(pl.Int64),
            pl.col(TRANS_CODE).cast(pl.Int64),
            pl.col(TRANS_NAME).cast(pl.Utf8),
            pl.col(TRANS_TYPE).cast(pl.Utf8),
            pl.col(LOAN_TYPE).cast(pl.Utf8),
            pl.col(TRANS_NAME_XLN).cast(pl.Utf8),
        )