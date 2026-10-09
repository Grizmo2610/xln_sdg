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

    # Connection lifecycle

    def connect(self) -> None:
        if self._conn is not None:
            return
        logger.debug("Connecting to Oracle %s …", self._dsn)
        try:
            self._conn = oracledb.connect(
                user        = self._user,
                password    = self._password,
                dsn         = self._dsn,
            )
            self._conn.outputtypehandler = _output_type_handler
            logger.info("Oracle connection established.")
        except oracledb.DatabaseError as exc:
            logger.error("Failed to connect to Oracle (%s): %s", self._dsn, exc)
            logger.debug("Connection error details:", exc_info=True)
            raise ConnectionError(f"Oracle connection failed: {exc}") from exc

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

    # Internal helpers

    @property
    def _connection(self) -> oracledb.Connection:
        if self._conn is None:
            raise RuntimeError("OracleClient is not connected. Call connect() first.")
        return self._conn

    def _cursor(self) -> oracledb.Cursor:
        return self._connection.cursor()

    # Core operations

    def execute(self, sql: str, params: dict | list | None = None) -> None:
        """Execute a single DML/DDL statement (no result set)."""
        try:
            with self._cursor() as cur:
                cur.execute(sql, params or {})
            self._connection.commit()
        except oracledb.DatabaseError as exc:
            logger.error("execute() failed: %s", exc)
            logger.debug("SQL: %s | params: %s", sql, params, exc_info=True)
            raise

    def select(self, sql: str, params: dict | list | None = None) -> pl.DataFrame:
        """
        Execute a SELECT and return the result as a Polars DataFrame.
        Column names are taken from cursor.description and uppercased.
        """
        try:
            with self._cursor() as cur:
                cur.execute(sql, params or {})
                cols = [d[0].upper() for d in cur.description]
                rows = cur.fetchall()
        except oracledb.DatabaseError as exc:
            logger.error("SELECT failed: %s", exc)
            logger.debug("SQL: %s | params: %s", sql, params, exc_info=True)
            raise

        if not rows:
            return pl.DataFrame({c: [] for c in cols})

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

        data = df.select(list(cols)).rows()
        total = 0

        try:
            with self._cursor() as cur:
                for start in range(0, len(data), chunk_size):
                    chunk = data[start : start + chunk_size]
                    end   = start + len(chunk)
                    try:
                        cur.executemany(sql, chunk)
                        total += len(chunk)
                        logger.debug(
                            "insert(%s): rows %d–%d committed (%d total).",
                            table.oracle_name, start + 1, end, total,
                        )
                    except oracledb.DatabaseError as exc:
                        logger.error(
                            "insert(%s): chunk %d–%d failed: %s",
                            table.oracle_name, start + 1, end, exc,
                        )
                        logger.debug("Chunk insert error details:", exc_info=True)
                        raise
                self._connection.commit()
        except oracledb.DatabaseError:
            raise

        logger.info("insert(%s): %d rows inserted.", table.oracle_name, total)
        return total

    def fetch_pool(
        self,
        table: TableDef,
        columns: Sequence[str],
        where: str | None = None,
        params: dict | list | None = None,
    ) -> pl.DataFrame:
        """
        Lightweight SELECT of specific columns from a table.
        Never does SELECT * — only fetches exactly what the pool needs.
        """
        col_list = ", ".join(columns)
        sql = f"SELECT {col_list} FROM {table.oracle_name}"
        if where:
            sql += f" WHERE {where}"
        logger.debug("fetch_pool(%s): %s", table.oracle_name, sql)
        try:
            return self.select(sql, params)
        except oracledb.DatabaseError as exc:
            logger.error(
                "fetch_pool(%s) failed: %s", table.oracle_name, exc
            )
            logger.debug("fetch_pool error details:", exc_info=True)
            raise

    # Utility queries

    def max_dayid(self, table: TableDef) -> object | None:
        """
        Return MAX(DAYID) from a table, or None if the table is empty.
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

    def identity_columns(self, oracle_name: str) -> list[tuple[str, str]]:
        """
        Return [(column_name, generation_type)] for every identity column of a
        table in the current schema. generation_type is 'ALWAYS' or 'BY DEFAULT'.
        """
        sql = (
            "SELECT column_name, generation_type FROM user_tab_identity_cols "
            "WHERE table_name = :1"
        )
        with self._cursor() as cur:
            cur.execute(sql, [oracle_name.upper()])
            rows = cur.fetchall()
        return [(r[0], r[1].strip()) for r in rows]

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



def _output_type_handler(
    cursor: oracledb.Cursor,
    metadata: oracledb.FetchInfo,
) -> oracledb.DbType | None:
    if metadata.type_code in (oracledb.DB_TYPE_DATE, oracledb.DB_TYPE_TIMESTAMP):
        return cursor.var(oracledb.DB_TYPE_TIMESTAMP, arraysize=cursor.arraysize)
    return None