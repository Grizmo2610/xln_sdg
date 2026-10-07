# =============================================================================
# db/client.py
# OracleClient — the only layer that speaks to Oracle.
# All SQL is built here; no SQL strings anywhere else in the codebase.
# =============================================================================

from __future__ import annotations

import os
import logging
from typing import Any, Sequence

import oracledb
import polars as pl
from dotenv import load_dotenv

from engine.schema.tables import TableDef

load_dotenv()
logger = logging.getLogger(__name__)

# Default chunk size for bulk inserts (rows per round-trip)
_DEFAULT_CHUNK = 2_000


class OracleClient:
    """
    Thin wrapper around oracledb.

    Usage (context manager — preferred):
        with OracleClient() as db:
            df = db.select("SELECT * FROM ...")

    Usage (manual):
        db = OracleClient()
        db.connect()
        ...
        db.close()
    """

    def __init__(self) -> None:
        self._dsn = oracledb.makedsn(
            host        = os.environ["ORACLE_HOST"],
            port        = int(os.environ.get("ORACLE_PORT", 1521)),
            service_name= os.environ["ORACLE_SERVICE"],
        )
        self._user      = os.environ["ORACLE_USER"]
        self._password  = os.environ["ORACLE_PASSWORD"]
        self._conn: oracledb.Connection | None = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        if self._conn is not None:
            return
        logger.debug("Connecting to Oracle %s …", self._dsn)
        self._conn = oracledb.connect(
            user        = self._user,
            password    = self._password,
            dsn         = self._dsn,
        )
        # Return dates/timestamps as Python objects, not strings
        self._conn.outputtypehandler = _output_type_handler
        logger.info("Oracle connection established.")

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            logger.debug("Oracle connection closed.")

    def __enter__(self) -> "OracleClient":
        self.connect()
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @property
    def _connection(self) -> oracledb.Connection:
        if self._conn is None:
            raise RuntimeError("OracleClient is not connected. Call connect() first.")
        return self._conn

    def _cursor(self) -> oracledb.Cursor:
        return self._connection.cursor()

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def execute(self, sql: str, params: dict | list | None = None) -> None:
        """Execute a single DML/DDL statement (no result set)."""
        with self._cursor() as cur:
            cur.execute(sql, params or {})
        self._connection.commit()

    def select(self, sql: str, params: dict | list | None = None) -> pl.DataFrame:
        """
        Execute a SELECT and return the result as a Polars DataFrame.
        Column names are taken from cursor.description and uppercased.
        """
        with self._cursor() as cur:
            cur.execute(sql, params or {})
            cols = [d[0].upper() for d in cur.description]
            rows = cur.fetchall()

        if not rows:
            return pl.DataFrame({c: [] for c in cols})

        # Transpose list-of-rows → dict-of-columns for Polars
        transposed: dict[str, list] = {c: [] for c in cols}
        for row in rows:
            for c, v in zip(cols, row):
                transposed[c].append(v)

        return pl.DataFrame(transposed)

    def insert(
        self,
        table: TableDef,
        df: pl.DataFrame,
        chunk_size: int = _DEFAULT_CHUNK,
    ) -> int:
        """
        Bulk-insert a Polars DataFrame into an Oracle table.

        - Uses only table.insert_columns (excludes identity-generated cols).
        - Sends rows in chunks to avoid large round-trips.
        - Returns total rows inserted.
        """
        if df.is_empty():
            logger.debug("insert(%s): DataFrame is empty, skipping.", table.oracle_name)
            return 0

        cols = table.insert_columns
        # Verify all columns exist in the DataFrame
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise ValueError(
                f"insert({table.oracle_name}): DataFrame missing columns: {missing}"
            )

        placeholders = ", ".join(f":{i+1}" for i in range(len(cols)))
        sql = (
            f"INSERT INTO {table.oracle_name} "
            f"({', '.join(cols)}) "
            f"VALUES ({placeholders})"
        )

        # Convert only the needed columns to Python-native list-of-tuples
        data = df.select(list(cols)).rows()

        total = 0
        with self._cursor() as cur:
            for start in range(0, len(data), chunk_size):
                chunk = data[start : start + chunk_size]
                cur.executemany(sql, chunk)
                total += len(chunk)
                logger.debug(
                    "insert(%s): %d / %d rows committed.",
                    table.oracle_name, total, len(data),
                )
            self._connection.commit()

        logger.info("insert(%s): %d rows total.", table.oracle_name, total)
        return total

    def fetch_pool(
        self,
        table: TableDef,
        columns: Sequence[str],
        where: str | None = None,
        params: dict | None = None,
    ) -> pl.DataFrame:
        """
        Lightweight SELECT of specific columns from a table.
        Never does SELECT * — only fetches exactly what the pool needs.

        Args:
            table:   TableDef of the DIM/FCT to query.
            columns: Column names to SELECT.
            where:   Optional WHERE clause string (no leading 'WHERE' keyword).
            params:  Bind parameters for the WHERE clause.

        Returns:
            Polars DataFrame with the requested columns.
        """
        col_list = ", ".join(columns)
        sql = f"SELECT {col_list} FROM {table.oracle_name}"
        if where:
            sql += f" WHERE {where}"
        logger.debug("fetch_pool: %s", sql)
        return self.select(sql, params)

    # ------------------------------------------------------------------
    # Utility queries
    # ------------------------------------------------------------------

    def max_dayid(self, table: TableDef) -> str | None:
        """
        Return MAX(DAYID) from a table as a string, or None if the table is empty.
        DAYID is stored as VARCHAR2 in format YYYYMMDD.
        """
        sql = f"SELECT MAX(DAYID) FROM {table.oracle_name}"
        with self._cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()
        return row[0] if row and row[0] is not None else None

    def row_count(self, table: TableDef) -> int:
        """Return total row count for a table."""
        sql = f"SELECT COUNT(*) FROM {table.oracle_name}"
        with self._cursor() as cur:
            cur.execute(sql)
            row = cur.fetchone()
        return row[0] if row else 0

    def table_exists(self, oracle_name: str) -> bool:
        """Check whether a table exists in the current schema."""
        sql = (
            "SELECT COUNT(*) FROM user_tables "
            "WHERE table_name = :1"
        )
        with self._cursor() as cur:
            cur.execute(sql, [oracle_name.upper()])
            row = cur.fetchone()
        return (row[0] if row else 0) > 0


# =============================================================================
# Output type handler — return Python datetime objects instead of cx_Oracle LOB
# =============================================================================

def _output_type_handler(
    cursor: oracledb.Cursor,
    metadata: oracledb.FetchInfo,
) -> oracledb.DbType | None:
    """
    Ensure DATE and TIMESTAMP columns are returned as Python datetime objects.
    oracledb returns them natively by default in thin mode; this handler
    makes behaviour explicit and consistent in both thin and thick modes.
    """
    if metadata.type_code in (oracledb.DB_TYPE_DATE, oracledb.DB_TYPE_TIMESTAMP):
        return cursor.var(oracledb.DB_TYPE_TIMESTAMP, arraysize=cursor.arraysize)
    return None