from __future__ import annotations

from typing import Any

import polars as pl
import pandas as pd


class DataFrameWrapper:

    def __init__(self, df: pl.DataFrame | pd.DataFrame) -> None:
        self._df = df

    @property
    def is_polars(self) -> bool:
        return isinstance(self._df, pl.DataFrame)

    def collect(self) -> pl.DataFrame | pd.DataFrame:
        return self._df

    def to_polars(self) -> pl.DataFrame:
        if self.is_polars:
            return self._df
        return pl.from_pandas(self._df)

    def to_pandas(self) -> pd.DataFrame:
        if not self.is_polars:
            return self._df
        return self._df.to_pandas()

    def select(self, columns: list[str]) -> DataFrameWrapper:
        if self.is_polars:
            return DataFrameWrapper(self._df.select(columns))
        return DataFrameWrapper(self._df[columns])

    def drop(self, columns: list[str]) -> DataFrameWrapper:
        if self.is_polars:
            return DataFrameWrapper(self._df.drop(columns))
        return DataFrameWrapper(self._df.drop(columns=columns))

    def rename(self, mapping: dict[str, str]) -> DataFrameWrapper:
        if self.is_polars:
            return DataFrameWrapper(self._df.rename(mapping))
        return DataFrameWrapper(self._df.rename(columns=mapping))

    def filter(self, condition: Any) -> DataFrameWrapper:
        if self.is_polars:
            return DataFrameWrapper(self._df.filter(condition))
        if isinstance(condition, str):
            return DataFrameWrapper(self._df.query(condition))
        return DataFrameWrapper(self._df[condition])

    def fill_null(self, value: Any) -> DataFrameWrapper:
        if self.is_polars:
            return DataFrameWrapper(self._df.fill_null(value))
        return DataFrameWrapper(self._df.fillna(value))

    def drop_nulls(self, columns: list[str] | None = None) -> DataFrameWrapper:
        if self.is_polars:
            return DataFrameWrapper(self._df.drop_nulls(subset=columns))
        return DataFrameWrapper(self._df.dropna(subset=columns))

    def sort(self, by: str | list[str], *, descending: bool = False) -> DataFrameWrapper:
        if self.is_polars:
            return DataFrameWrapper(self._df.sort(by, descending=descending))
        cols = [by] if isinstance(by, str) else by
        return DataFrameWrapper(self._df.sort_values(cols, ascending=not descending))

    def group_by(self, by: str | list[str]) -> _GroupByProxy:
        return _GroupByProxy(self._df, by, is_polars=self.is_polars)

    def join(
        self,
        other: DataFrameWrapper | pl.DataFrame | pd.DataFrame,
        on: str | list[str],
        how: str = "inner",
        *,
        suffix: str = "_right",
    ) -> DataFrameWrapper:
        other_df = other.collect() if isinstance(other, DataFrameWrapper) else other

        if self.is_polars:
            other_pl = other_df if isinstance(other_df, pl.DataFrame) else pl.from_pandas(other_df)
            pl_how = "full" if how == "outer" else how
            return DataFrameWrapper(self._df.join(other_pl, on=on, how=pl_how, suffix=suffix))

        other_pd = other_df if isinstance(other_df, pd.DataFrame) else other_df.to_pandas()
        return DataFrameWrapper(self._df.merge(other_pd, on=on, how=how, suffixes=("", suffix)))

    def concat(self, other: DataFrameWrapper | pl.DataFrame | pd.DataFrame) -> DataFrameWrapper:
        other_df = other.collect() if isinstance(other, DataFrameWrapper) else other

        if self.is_polars:
            other_pl = other_df if isinstance(other_df, pl.DataFrame) else pl.from_pandas(other_df)
            return DataFrameWrapper(pl.concat([self._df, other_pl], how="vertical"))

        other_pd = other_df if isinstance(other_df, pd.DataFrame) else other_df.to_pandas()
        return DataFrameWrapper(pd.concat([self._df, other_pd], ignore_index=True))

    def cast(self, mapping: dict[str, Any]) -> DataFrameWrapper:
        if self.is_polars:
            exprs = [pl.col(col).cast(dtype) for col, dtype in mapping.items()]
            return DataFrameWrapper(self._df.with_columns(exprs))
        df = self._df.copy()
        for col, dtype in mapping.items():
            df[col] = df[col].astype(dtype)
        return DataFrameWrapper(df)

    def with_column(self, name: str, values: Any) -> DataFrameWrapper:
        if self.is_polars:
            if isinstance(values, pl.Expr):
                return DataFrameWrapper(self._df.with_columns(values.alias(name)))
            return DataFrameWrapper(self._df.with_columns(pl.Series(name, values)))
        df = self._df.copy()
        df[name] = values
        return DataFrameWrapper(df)

    def with_expressions(self, *exprs: pl.Expr) -> DataFrameWrapper:
        if self.is_polars:
            return DataFrameWrapper(self._df.with_columns(list(exprs)))
        raise NotImplementedError("pandas branch not implemented for with_expressions")

    def unique(self, columns: list[str] | None = None) -> DataFrameWrapper:
        if self.is_polars:
            return DataFrameWrapper(self._df.unique(subset=columns))
        return DataFrameWrapper(self._df.drop_duplicates(subset=columns))

    def __len__(self) -> int:
        return len(self._df)

    def __repr__(self) -> str:
        engine = "polars" if self.is_polars else "pandas"
        return f"DataFrameWrapper(engine={engine}, shape={self._df.shape})"

    @property
    def columns(self) -> list[str]:
        return list(self._df.columns)

    @property
    def shape(self) -> tuple[int, int]:
        return self._df.shape


class _GroupByProxy:

    def __init__(
        self,
        df: pl.DataFrame | pd.DataFrame,
        by: str | list[str],
        *,
        is_polars: bool,
    ) -> None:
        self._df = df
        self._by = [by] if isinstance(by, str) else by
        self._is_polars = is_polars

    def agg(self, aggregations: dict[str, str]) -> DataFrameWrapper:
        if self._is_polars:
            exprs = [_pl_agg_expr(col, func) for col, func in aggregations.items()]
            return DataFrameWrapper(self._df.group_by(self._by).agg(exprs))

        return DataFrameWrapper(
            self._df.groupby(self._by).agg(aggregations).reset_index()
        )


def _pl_agg_expr(col: str, func: str) -> pl.Expr:
    mapping = {
        "sum":   pl.col(col).sum(),
        "mean":  pl.col(col).mean(),
        "min":   pl.col(col).min(),
        "max":   pl.col(col).max(),
        "count": pl.col(col).count(),
        "first": pl.col(col).first(),
    }
    if func not in mapping:
        raise ValueError(f"Unsupported aggregation: '{func}'. Choose from {list(mapping)}")
    return mapping[func].alias(col)
