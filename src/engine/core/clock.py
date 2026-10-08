# =============================================================================
# core/clock.py
# SimClock — determines which dates need to be generated.
# Queries Oracle for MAX(DAYID) and yields missing dates.
# =============================================================================

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Iterator

from engine.db.client import OracleClient
from engine.schema import tables as T

logger = logging.getLogger(__name__)

# The anchor FCT table used to determine the last loaded date
_ANCHOR_TABLE = T.FCT_XLN_ACTIVE_LOAN


class SimClock:
    """
    Tracks simulation time and determines which dates still need data.

    Args:
        to_date:   The target date to run up to (inclusive).
        from_date: Optional override for the start date.
                   If not supplied, the start date is derived from
                   MAX(DAYID) + 1 day in Oracle.
    """

    def __init__(self, to_date: date, from_date: date | None = None) -> None:
        self.to_date    = to_date
        self._from_date = from_date   # None = "ask Oracle"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def last_loaded_date(self, db: OracleClient) -> date | None:
        """
        Query Oracle for the most recent DAYID in the anchor FCT table.
        Returns a date object, or None if the table is empty.

        DAYID is a DATE column in Oracle; oracledb returns it as a
        Python datetime object (via the output type handler in client.py).
        """
        raw = db.max_dayid(_ANCHOR_TABLE)
        if raw is None:
            logger.info("SimClock: anchor table is empty — no data loaded yet.")
            return None
        # oracledb DATE → Python datetime; normalise to date
        if isinstance(raw, datetime):
            loaded = raw.date()
        elif isinstance(raw, date):
            loaded = raw
        else:
            raise ValueError(
                f"SimClock: unexpected MAX(DAYID) type {type(raw)!r}: {raw!r}. "
                "Expected datetime or date (DAYID column is DATE in Oracle)."
            )
        logger.info("SimClock: last loaded date = %s", loaded)
        return loaded

    def dates_to_run(self, db: OracleClient) -> Iterator[date]:
        """
        Yield each calendar date that is missing from Oracle,
        from (last_loaded_date + 1) through self.to_date, inclusive.

        If from_date was supplied at construction time, it overrides
        the Oracle query entirely.
        """
        if self._from_date is not None:
            start = self._from_date
            logger.info(
                "SimClock: using explicit from_date=%s, to_date=%s",
                start, self.to_date,
            )
        else:
            last = self.last_loaded_date(db)
            if last is None:
                raise RuntimeError(
                    "Oracle has no data and no from_date was supplied. "
                    "Run 'seed' first, or pass --start-date."
                )
            start = last + timedelta(days=1)
            logger.info(
                "SimClock: resuming from %s → %s", start, self.to_date,
            )

        if start > self.to_date:
            logger.info("SimClock: nothing to run (already up to date).")
            return

        current = start
        while current <= self.to_date:
            yield current
            current += timedelta(days=1)
