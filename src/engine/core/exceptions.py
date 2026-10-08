from __future__ import annotations

from pathlib import Path


class BaseEngineError(Exception):
    pass


class StorageWriteError(BaseEngineError):
    def __init__(self, message: str, file_path: str | Path | None = None):
        self.file_path = str(file_path) if file_path else "Unknown Path"
        super().__init__(f"[StorageWriteError] {message} (Path: {self.file_path})")


class SCD2IntegrityError(BaseEngineError):
    def __init__(self, message: str, table_name: str, duplicate_keys: list):
        self.table_name = table_name
        self.duplicate_keys = duplicate_keys
        super().__init__(
            f"[SCD2IntegrityError] {message}\n"
            f"Table: {self.table_name}\n"
            f"Violating Keys: {self.duplicate_keys[:10]}"
            + ("..." if len(self.duplicate_keys) > 10 else "")
        )


class DataGenerationError(BaseEngineError):
    pass


class ConfigurationMissingError(BaseEngineError):
    pass