# =============================================================================
# core/pool.py
# PoolRegistry — session-scoped cache of DIM table data.
# Fetches only the FK columns needed; never loads full tables.
# =============================================================================

from __future__ import annotations

import logging
from typing import Sequence

import polars as pl

from engine.db.client import OracleClient
from engine.schema import tables as T
from engine.schema.tables import TableDef
from engine.schema import join_map

logger = logging.getLogger(__name__)


class PoolRegistry:
    """
    In-memory cache of DIM table pools for one pipeline session.

    A "pool" is the minimal set of columns from a DIM table that generators
    need to resolve FK values — no full-table loads.

    Lifecycle:
        - get()      → fetch from Oracle on first call, return cache on subsequent.
        - refresh()  → force re-fetch from Oracle (call after INSERT into that DIM).
        - invalidate()→ drop cache without re-fetching.

    Args:
        db: OracleClient (must already be connected).
    """

    def __init__(self, db: OracleClient) -> None:
        self._db    = db
        self._cache: dict[str, pl.DataFrame] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(
        self,
        logical_key: str,
        columns: Sequence[str] | None = None,
        where: str | None = None,
        params: dict | None = None,
    ) -> pl.DataFrame:
        """
        Return the pool DataFrame for a DIM table.

        If already cached (and no where filter is requested), returns the
        cached copy.  Otherwise fetches from Oracle.

        Args:
            logical_key: Registry key, e.g. 'CUST', 'CONTRACT'.
            columns:     Columns to fetch. Defaults to the minimal set
                         derived from join_map.pool_columns_for().
            where:       Optional WHERE clause (bypasses cache — use for
                         targeted queries like prev_state).
            params:      Bind params for the WHERE clause.
        """
        # Targeted WHERE queries always go to Oracle (not cached)
        if where:
            table  = T.get(logical_key)
            cols   = columns or _default_columns(logical_key, table)
            return self._db.fetch_pool(table, cols, where=where, params=params)

        # Regular pool — use cache
        if logical_key not in self._cache:
            self._fetch_and_cache(logical_key, columns)

        return self._cache[logical_key]

    def refresh(self, *logical_keys: str) -> None:
        """
        Force re-fetch from Oracle for one or more tables.
        Call this immediately after inserting into a DIM table.
        """
        for key in logical_keys:
            logger.debug("PoolRegistry.refresh: %s", key)
            self._fetch_and_cache(key, columns=None)

    def invalidate(self, *logical_keys: str) -> None:
        """
        Drop cached pool(s) without re-fetching.
        Next get() call will hit Oracle.
        """
        for key in logical_keys:
            if key in self._cache:
                del self._cache[key]
                logger.debug("PoolRegistry.invalidate: %s evicted.", key)

    def invalidate_all(self) -> None:
        """Drop the entire cache."""
        self._cache.clear()
        logger.debug("PoolRegistry: full cache cleared.")

    def is_cached(self, logical_key: str) -> bool:
        return logical_key in self._cache

    def cached_keys(self) -> list[str]:
        return list(self._cache.keys())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_and_cache(
        self,
        logical_key: str,
        columns: Sequence[str] | None,
    ) -> None:
        table = T.get(logical_key)
        cols  = columns or _default_columns(logical_key, table)
        logger.info(
            "PoolRegistry: fetching %s [%s] from Oracle …",
            logical_key, ", ".join(cols),
        )
        df = self._db.fetch_pool(table, cols)
        self._cache[logical_key] = df
        logger.info(
            "PoolRegistry: %s cached — %d rows.", logical_key, len(df),
        )


def _default_columns(logical_key: str, table: TableDef) -> list[str]:
    """
    Determine the minimal column set to fetch for a pool.

    Priority:
      1. Columns derived from join_map (FK + PK pairs for this table).
      2. Fallback: just the surrogate key if no FK relationships are defined.
    """
    cols = join_map.pool_columns_for(logical_key)
    if cols:
        return cols
    # Fallback for DIM tables not referenced by any FCT (e.g. standalone dims)
    if table.surrogate_key:
        return [table.surrogate_key]
    raise ValueError(
        f"Cannot determine default pool columns for '{logical_key}'. "
        "Add FK entries to join_map.py or pass columns= explicitly."
    )