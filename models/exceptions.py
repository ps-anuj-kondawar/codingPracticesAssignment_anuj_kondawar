class DatabaseError(Exception):
    """Base exception for database and persistence errors."""
    pass


class CorruptDataError(DatabaseError):
    """Raised when the database file exists but contains invalid or corrupt data."""
    pass


class StorageError(DatabaseError):
    """Raised when reading from or writing to the database file fails due to I/O issues."""
    pass
