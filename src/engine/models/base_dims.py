from __future__ import annotations

from datetime import date, datetime

import holidays
import polars as pl

from engine.io.storage.dataframe import DataFrameWrapper

class CalendarDimLoader:

    def __init__(self) -> None:
        super().__init__(
            table_name="DIM_XLN_CALENDAR",
            business_key="DAYID",
            surrogate_key="DIMENSION_ID",
        )

    def generate(self, run_date: datetime, **kwargs) -> pl.DataFrame:
        start_date = kwargs.get("start_date", run_date.date())
        end_date = kwargs.get("end_date", run_date.date())

        vn_holidays = holidays.Vietnam()

        return (
            pl.DataFrame({
                "DAYID": pl.date_range(
                    start_date,
                    end_date,
                    interval="1d",
                    eager=True,
                )
            })
            .with_columns(
                pl.int_range(1, pl.len() + 1, dtype=pl.Int64)
                .alias("DIMENSION_ID"),

                pl.col("DAYID").dt.day().alias("DAY"),
                pl.col("DAYID").dt.month().alias("MONTH"),
                pl.col("DAYID").dt.year().alias("YEAR"),

                pl.col("DAYID")
                .is_in(list(vn_holidays))
                .cast(pl.Int8)
                .alias("HOLIDAY"),

                pl.col("DAYID").dt.day().alias("NO_DAY_MTD"),
                pl.col("DAYID").dt.ordinal_day().alias("NO_DAY_YTD"),
                pl.col("DAYID").dt.strftime("%A").alias("DAY_NAME"),

                pl.col("DAYID")
                .dt.month_end()
                .alias("LAST_DAY_OF_MONTH"),

                pl.col("DAYID")
                .dt.month_end()
                .dt.day()
                .alias("NO_DAY_OF_MONTH"),

                (
                    pl.col("DAYID").dt.ordinal_day()
                    - pl.col("DAYID").dt.quarter_start().dt.ordinal_day()
                    + 1
                ).alias("NO_DAY_OF_QUARTER"),

                pl.when(pl.col("DAYID").dt.is_leap_year())
                .then(366)
                .otherwise(365)
                .alias("NO_DAY_OF_YEAR"),
            )
            .select([
                "DIMENSION_ID",
                "DAYID",
                "DAY",
                "MONTH",
                "YEAR",
                "HOLIDAY",
                "NO_DAY_MTD",
                "NO_DAY_YTD",
                "DAY_NAME",
                "LAST_DAY_OF_MONTH",
                "NO_DAY_OF_MONTH",
                "NO_DAY_OF_QUARTER",
                "NO_DAY_OF_YEAR",
            ])
        )

class BucketDimLoader:

    BUCKETS = [
        (0, "B00"), (30, "B01"), (60, "B02"), (90, "B03"), (120, "B04"), (150, "B05"), (180, "B06"),
        (210, "B07"), (240, "B08"), (270, "B09"), (300, "B10"), (8000, "B11+"),
    ]

    SBV_GROUPS = [
        (10, "G01"), (30, "G02"), (90, "G03"), (180, "G04"), (8000, "G05"),
    ]

    def generate(self) -> pl.DataFrame:
        max_ovd = 8000

        df = pl.DataFrame({
            "OVD_NO": pl.arange(0, max_ovd + 1, eager=True),
        })

        bucket_df = pl.DataFrame(
            self.BUCKETS,
            schema=["MAX_OVD", "BUCKET_CODE"],
        ).with_columns(
            pl.col("MAX_OVD").cast(pl.Int64)
        )

        group_df = pl.DataFrame(
            self.SBV_GROUPS,
            schema=["MAX_OVD", "SBV_GROUP"],
        ).with_columns(
            pl.col("MAX_OVD").cast(pl.Int64)
        )

        df = (
            df.sort("OVD_NO")
            .join_asof(
                bucket_df.sort("MAX_OVD"),
                left_on="OVD_NO",
                right_on="MAX_OVD",
                strategy="backward",
            )
            .join_asof(
                group_df.sort("MAX_OVD"),
                left_on="OVD_NO",
                right_on="MAX_OVD",
                strategy="backward",
            )
            .with_columns(
                pl.when(pl.col("OVD_NO") == 0)
                .then(pl.lit("Current (0 days overdue)"))
                .otherwise(
                    pl.concat_str([
                        pl.lit("Overdue "),
                        pl.col("OVD_NO"),
                        pl.lit(" days"),
                    ])
                )
                .alias("DESCRIPTION_SBV"),

                pl.lit(date(2023, 1, 1)).alias("EFF_DATE"),
                pl.lit(None, dtype=pl.Date).alias("EXP_DATE"),

                (pl.int_range(1, pl.len() + 1))
                .cast(pl.Int64)
                .alias("DIMENSION_ID"),
            )
            .select([
                "DIMENSION_ID",
                "OVD_NO",
                "BUCKET_CODE",
                "SBV_GROUP",
                "DESCRIPTION_SBV",
                "EFF_DATE",
                "EXP_DATE",
            ])
        )

        return df


class LoanTxnCodeDimLoader:

    def __init__(self) -> None:
        super().__init__(
            table_name="DIM_XLN_LOAN_TXN_CODE",
            business_key="TRANS_CODE",
            surrogate_key="DIMENSION_KEY",
        )

    ROWS = [
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
            self.ROWS,
            schema=[
                "ID",
                "TRANS_CODE",
                "TRANS_NAME",
                "TRANS_TYPE",
                "LOAN_TYPE",
                "TRANS_NAME_XLN",
            ],
            orient="row",
        ).with_columns(
            pl.col("ID").cast(pl.Int64),
            pl.col("TRANS_CODE").cast(pl.Int64),
            pl.col("TRANS_NAME").cast(pl.Utf8),
            pl.col("TRANS_TYPE").cast(pl.Utf8),
            pl.col("LOAN_TYPE").cast(pl.Utf8),
            pl.col("TRANS_NAME_XLN").cast(pl.Utf8),
        )
