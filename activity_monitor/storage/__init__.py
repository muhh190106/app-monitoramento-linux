"""Local SQLite storage. Importing this package never opens or seeds a database."""

from .database import Database, default_database_path

__all__ = ["Database", "default_database_path"]
