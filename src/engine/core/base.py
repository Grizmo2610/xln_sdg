# =============================================================================
# core/base.py
# BaseGenerator — abstract contract for all data generators.
# Enforces pool validation before any generation happens.
# =============================================================================

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import date

import polars as pl

from engine.core.pool import PoolRegistry

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """
    Abstract base class for all generators.

    Subclasses must implement:
        - required_pools()  →  list of DIM logical keys this generator needs.
        - generate(...)     →  produce one or more DataFrames for a given date.

    The base class handles pool validation so subclasses can assume
    all required pools are present when generate() is called.
    """

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def required_pools(self) -> list[str]:
        """
        Declare which DIM pools must be loaded before this generator runs.
        Returns logical keys (e.g. ['CUST', 'CONTRACT', 'COMPANY']).
        Return [] for generators with no DIM dependencies (e.g. ReferenceGenerator).
        """
        ...

    @abstractmethod
    def generate(self, run_date: date, pool: PoolRegistry, n: int) -> pl.DataFrame | dict[str, pl.DataFrame]:
        """
        Generate synthetic data for `run_date`.

        Args:
            run_date: The simulation date being processed.
            pool:     PoolRegistry — use pool.get(key) to fetch DIM data.
            n:        Target row count (meaning varies per generator).

        Returns:
            A single DataFrame, or a dict of {logical_key: DataFrame}
            for generators that produce multiple tables (e.g. CustomerGenerator).
        """
        ...

    # ------------------------------------------------------------------
    # Pool validation — called by pipeline before generate()
    # ------------------------------------------------------------------

    def validate_pools(self, pool: PoolRegistry) -> None:
        """
        Verify all required pools are present and non-empty.
        Raises MissingPoolError with a clear message if any are absent.
        Called automatically by run_safe().
        """
        missing  = []
        empty    = []

        for key in self.required_pools():
            if not pool.is_cached(key):
                missing.append(key)
            elif pool.get(key).is_empty():
                empty.append(key)

        errors: list[str] = []
        if missing:
            errors.append(f"Pools not loaded: {missing}")
        if empty:
            errors.append(f"Pools are empty (no rows): {empty}")

        if errors:
            raise MissingPoolError(
                f"{self.__class__.__name__} cannot run — " + "; ".join(errors)
            )

        logger.debug(
            "%s: pool validation passed (%s).",
            self.__class__.__name__,
            ", ".join(self.required_pools()) or "no pools required",
        )

    def run_safe(
        self,
        run_date: date,
        pool: PoolRegistry,
        n: int,
    ) -> pl.DataFrame | dict[str, pl.DataFrame]:
        """
        Validate pools, then call generate().
        Use this instead of calling generate() directly.
        """
        self.validate_pools(pool)
        logger.info(
            "%s: generating for %s (n=%d) …",
            self.__class__.__name__, run_date, n,
        )
        result = self.generate(run_date, pool, n)
        _log_result(self.__class__.__name__, run_date, result)
        return result


# =============================================================================
# Exceptions
# =============================================================================

class MissingPoolError(RuntimeError):
    """Raised when a generator is called before its required pools are loaded."""


# =============================================================================
# Internal helpers
# =============================================================================

def _log_result(
    name: str,
    run_date: date,
    result: pl.DataFrame | dict[str, pl.DataFrame],
) -> None:
    if isinstance(result, pl.DataFrame):
        logger.info("%s [%s]: generated %d rows.", name, run_date, len(result))
    elif isinstance(result, dict):
        summary = ", ".join(f"{k}={len(v)}" for k, v in result.items())
        logger.info("%s [%s]: generated {%s}.", name, run_date, summary)