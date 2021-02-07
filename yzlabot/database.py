import os
from typing import Optional

from tinydb import TinyDB, Query


class YBDatabase:
    def __init__(self, guild_id: int):
        self.db_path: str = f"config/guild_{guild_id}.json"
        self.db: Optional[TinyDB] = None

    def __enter__(self) -> TinyDB:
        self.db = TinyDB(self.db_path)
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()


__all__ = [
    "YBDatabase",
    "Query"
]
