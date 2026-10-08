from __future__ import annotations

from datetime import datetime

import polars as pl


class SCD2StateMachine:

    @staticmethod
    def close_version(df: pl.DataFrame, run_date: datetime) -> pl.DataFrame:
        if df.is_empty():
            return df
        return df.with_columns(pl.lit(run_date.date()).alias("EXP_DATE"))

    @staticmethod
    def open_new_version(
        df: pl.DataFrame,
        run_date: datetime,
        exp_date_none: datetime | None = None,
        changes: list[pl.Expr] | dict | None = None,
    ) -> pl.DataFrame:
        if df.is_empty():
            return df

        from datetime import date as _date
        exp_val = (
            exp_date_none if isinstance(exp_date_none, _date)
            else (exp_date_none.date() if exp_date_none is not None else None)
        )
        df_new = df.with_columns([
            pl.lit(run_date.date()).cast(pl.Date).alias("EFF_DATE"),
            pl.lit(exp_val).cast(pl.Date).alias("EXP_DATE"),
        ])

        if changes:
            if isinstance(changes, dict):
                df_new = df_new.with_columns([pl.lit(v).alias(k) for k, v in changes.items()])
            else:
                df_new = df_new.with_columns(changes)

        return df_new

    @staticmethod
    def evolve_records(
        df_churn: pl.DataFrame,
        run_date: datetime,
        exp_date_none: datetime | None = None,
        changes: list[pl.Expr] | dict | None = None,
    ) -> tuple[pl.DataFrame, pl.DataFrame]:
        # atomic: close old versions and open new ones together (HC-2)
        df_closing = SCD2StateMachine.close_version(df_churn, run_date)
        df_opening = SCD2StateMachine.open_new_version(df_churn, run_date, exp_date_none, changes)
        return df_closing, df_opening

    @staticmethod
    def validate(df: pl.DataFrame, business_key: str, exp_date_none: datetime) -> None:
        active = df.filter(pl.col("EXP_DATE") == pl.lit(exp_date_none))
        counts = active.group_by(business_key).len()
        duplicates = counts.filter(pl.col("len") > 1)
        if not duplicates.is_empty():
            from src.core.exceptions import SCD2IntegrityError
            raise SCD2IntegrityError(
                message="SCD2 validation failed: duplicate active records detected.",
                table_name="Unknown (Validating Dataset)",
                duplicate_keys=duplicates[business_key].to_list()
            )