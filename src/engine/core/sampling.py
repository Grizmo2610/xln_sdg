from __future__ import annotations

import numpy as np
import polars as pl

from engine.config.random import rng


class SamplingEngine:
    """
    Collection of vectorized sampling methods.
    No state - used as a namespace (all @staticmethod).
    """

    # Categorical sampling

    @staticmethod
    def weighted_choice(
        values: list,
        probs: list[float],
        n: int,
        *,
        replace: bool = True,
    ) -> np.ndarray:
        """
        Sample n elements from `values` according to weights `probs`.

        Args:
            values: list of values to choose from.
            probs:  corresponding probabilities, must sum to 1.0 (small drift is normalized).
            n:      number of elements needed.
            replace: allow replacement (default True).

        Returns:
            np.ndarray shape (n,).

        Raises:
            ValueError: if len(values) != len(probs) or probs contain negative values.
        """
        if len(values) != len(probs):
            raise ValueError(
                f"weighted_choice: len(values)={len(values)} != len(probs)={len(probs)}"
            )
        p = np.array(probs, dtype=np.float64)
        if np.any(p < 0):
            raise ValueError("weighted_choice: probs contain negative values.")
        total = p.sum()
        if total <= 0:
            raise ValueError("weighted_choice: sum of probs = 0.")
        p = p / total

        return rng.choice(values, size=n, replace=replace, p=p)

    @staticmethod
    def uniform_choice(values: list, n: int, *, replace: bool = True) -> np.ndarray:
        """Sample n elements uniformly from `values`."""
        return rng.choice(values, size=n, replace=replace)

    @staticmethod
    def sample_gender(n: int, female_ratio: float) -> np.ndarray:
        """
        Sample n gender values as "F" or "M" strings.

        Args:
            n:            number of records.
            female_ratio: probability of "F" (0.0 -> 1.0).

        Returns:
            np.ndarray[str] shape (n,) with values "F" or "M".
        """
        return np.where(rng.random(n) < female_ratio, "FEMALE", "MALE")

    # Null injection

    @staticmethod
    def apply_null_rate(
        series: pl.Series,
        null_pct: float,
    ) -> pl.Series:
        """
        Randomly set `null_pct` proportion of elements to None.

        Args:
            series:   Polars Series of any dtype.
            null_pct: null rate (0.0 -> 1.0). 0.0 returns original series.

        Returns:
            Polars Series of same dtype with some null values.
        """
        if null_pct <= 0.0:
            return series
        if null_pct >= 1.0:
            return pl.Series(series.name, [None] * len(series), dtype=series.dtype)

        n = len(series)
        mask = rng.random(n) < null_pct
        null_mask = pl.Series("_mask", mask)

        return series.zip_with(null_mask, pl.Series(series.name, [None] * n, dtype=series.dtype))

    # Boolean / flag sampling

    @staticmethod
    def bernoulli(p: float, n: int) -> np.ndarray:
        """
        Return bool array shape (n,): True with probability p.
        Used for binary flags (churn, default, prepay...).
        """
        return rng.random(n) < p

    # Numeric distributions

    @staticmethod
    def normal_positive(
        mean: float,
        std: float,
        n: int,
        *,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> np.ndarray:
        """
        Sample from Normal distribution, clip to [min_val, max_val] if needed.
        Ensure result > 0 (e.g., loan amount).
        """
        samples = rng.normal(loc=mean, scale=std, size=n)
        samples = np.abs(samples)
        if min_val is not None:
            samples = np.clip(samples, min_val, None)
        if max_val is not None:
            samples = np.clip(samples, None, max_val)
        return samples

    @staticmethod
    def uniform_float(low: float, high: float, n: int) -> np.ndarray:
        """Uniform float in [low, high)."""
        return rng.uniform(low, high, size=n)

    @staticmethod
    def uniform_int(low: int, high: int, n: int) -> np.ndarray:
        """Uniform int in [low, high] (inclusive)."""
        return rng.integers(low, high + 1, size=n)

    # Date sampling

    @staticmethod
    def random_dates(
        start: np.datetime64,
        end: np.datetime64,
        n: int,
    ) -> np.ndarray:
        """
        Sample n random dates in [start, end] (inclusive).
        Returns np.ndarray dtype='datetime64[D]'.
        """
        start_day = start.astype("datetime64[D]").astype(np.int64)
        end_day = end.astype("datetime64[D]").astype(np.int64)
        if end_day < start_day:
            raise ValueError("random_dates: end < start.")
        day_offsets = rng.integers(0, end_day - start_day + 1, size=n)
        return (start_day + day_offsets).astype("datetime64[D]")

    # Pool sampling (helper - does not replace ActivePoolManager)

    @staticmethod
    def sample_rows(df: pl.DataFrame, n: int, *, replace: bool = True) -> pl.DataFrame:
        """
        Sample n rows from DataFrame (Polars).
        Use for small DataFrame / testing - use ActivePoolManager for main pools.
        """
        idx = rng.integers(0, len(df), size=n) if replace else rng.choice(len(df), size=n, replace=False)
        return df[idx.tolist()]