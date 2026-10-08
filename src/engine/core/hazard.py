from __future__ import annotations

from datetime import date

import polars as pl


class HazardModel:

    @staticmethod
    def transition(df: pl.DataFrame, run_date: date) -> pl.DataFrame:
        # run_date is a plain date; compare directly against MATURITY_DATE (Date column)
        return df.with_columns(
            pl.when(pl.col("STATE") == "NORMAL")
            .then(
                pl.when(pl.col("MATURITY_DATE") <= pl.lit(run_date)).then(pl.lit("SETTLED"))
                .when(pl.col("random_val") < pl.col("p_prepay")).then(pl.lit("SETTLED"))
                .when(pl.col("random_val") < (pl.col("p_prepay") + pl.col("p_default"))).then(pl.lit("OVERDUE"))
                .otherwise(pl.col("STATE"))
            )
            .when(pl.col("STATE") == "OVERDUE")
            .then(
                pl.when(pl.col("random_val") < pl.col("p_cure")).then(pl.lit("NORMAL"))
                .when(pl.col("random_val") < (pl.col("p_cure") + pl.col("p_worsen"))).then(pl.lit("BAD_DEBT"))
                .otherwise(pl.col("STATE"))
            )
            .otherwise(pl.col("STATE"))
            .alias("STATE")
        )

    @staticmethod
    def update_dpd(df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            pl.when(pl.col("STATE").is_in(["OVERDUE", "BAD_DEBT"]))
            .then(pl.col("DPD") + 1)
            .otherwise(pl.lit(0))
            .alias("DPD")
        )