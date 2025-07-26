"""
DataProcessing - A user-friendly Python package for working with CSV data.
"""

from .core import CSVData, load, save, load_from_db, load_from_api, create_live_stream
from .exceptions import DataProcessingError, ColumnNotFoundError, FileReadError
from .sql import SQLProcessor, sql_query, sql_execute, build_query
from .live_data import LiveDataManager, DatabaseConnector, APIConnector, RealTimeDataStream
from .simple_import import import_live, create_live_stream, EnhancedLiveData

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "CSVData",
    "load", 
    "save",
    "load_from_db",
    "load_from_api", 
    "create_live_stream",
    "DataProcessingError",
    "ColumnNotFoundError", 
    "FileReadError",
    "SQLProcessor",
    "sql_query",
    "sql_execute",
    "build_query",
    "LiveDataManager",
    "DatabaseConnector",
    "APIConnector",
    "RealTimeDataStream",
    "import_live",
    "EnhancedLiveData"
]

# Convenience function for quick loading
def read_csv(file_path, **kwargs):
    """Alias for load() function for pandas-like API."""
    return load(file_path, **kwargs)

# Add to __all__ for convenience
__all__.append("read_csv") 