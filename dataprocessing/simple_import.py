"""
Simple import functionality for DataProcessing package.
Provides intuitive import syntax for live data.
"""

import pandas as pd
from typing import Union, Optional
from .core import CSVData
from .simple_live import SimpleLiveData, LiveCSVData


def import_data(url: str) -> SimpleLiveData:
    """
    Import data from URL with simple syntax.
    
    Args:
        url: URL to import from (can include @ prefix)
        
    Returns:
        SimpleLiveData object
    """
    # Remove @ prefix if present
    if url.startswith('@'):
        url = url[1:]
    
    return SimpleLiveData(url)


def create_live_stream(data_source: Union[str, SimpleLiveData], interval: int = 3600) -> SimpleLiveData:
    """
    Create a live stream from data source.
    
    Args:
        data_source: URL string or SimpleLiveData object
        interval: Refresh interval in seconds
        
    Returns:
        SimpleLiveData object with streaming enabled
    """
    if isinstance(data_source, str):
        # Remove @ prefix if present
        if data_source.startswith('@'):
            data_source = data_source[1:]
        live_data = SimpleLiveData(data_source, interval)
    else:
        # Already a SimpleLiveData object
        live_data = data_source
        live_data.interval = interval
    
    live_data.start()
    return live_data


# Global registry for named data sources
_data_registry = {}


def register_data(name: str, url: str):
    """
    Register a data source with a name.
    
    Args:
        name: Name for the data source
        url: URL of the data source
    """
    _data_registry[name] = url


def get_data(name: str) -> SimpleLiveData:
    """
    Get data by registered name.
    
    Args:
        name: Registered data source name
        
    Returns:
        SimpleLiveData object
    """
    if name not in _data_registry:
        raise ValueError(f"Data source '{name}' not registered. Use register_data() first.")
    
    return SimpleLiveData(_data_registry[name])


# Convenience function for direct SQL queries
def sql_query(data_source: Union[str, SimpleLiveData], query: str) -> CSVData:
    """
    Execute SQL query on data source.
    
    Args:
        data_source: URL string or SimpleLiveData object
        query: SQL query string
        
    Returns:
        CSVData with query results
    """
    if isinstance(data_source, str):
        # Remove @ prefix if present
        if data_source.startswith('@'):
            data_source = data_source[1:]
        live_data = SimpleLiveData(data_source)
    else:
        live_data = data_source
    
    return live_data.sql(query)


# Simple data loading without streaming
def load_data(url: str) -> CSVData:
    """
    Load data from URL without streaming.
    
    Args:
        url: URL to load from (can include @ prefix)
        
    Returns:
        CSVData object
    """
    # Remove @ prefix if present
    if url.startswith('@'):
        url = url[1:]
    
    try:
        df = pd.read_csv(url)
        return CSVData(df)
    except Exception as e:
        raise Exception(f"Failed to load data from URL: {e}")


# Enhanced SimpleLiveData with better SQL support
class EnhancedLiveData(SimpleLiveData):
    """Enhanced live data with better SQL and data access."""
    
    def __init__(self, source: str, interval: int = 3600):
        super().__init__(source, interval)
        self._table_name = "data"  # Default table name for SQL queries
    
    def sql(self, query: str) -> CSVData:
        """
        Execute SQL query with automatic table name replacement.
        
        Args:
            query: SQL query string (can use 'data' as table name)
            
        Returns:
            CSVData with query results
        """
        # Replace common table names with 'data'
        query = query.replace('teacher_data', 'data')
        query = query.replace('live_data', 'data')
        
        return super().sql(query)
    
    @property
    def columns(self):
        """Get column names."""
        return self.header
    
    def filter(self, condition: str) -> CSVData:
        """
        Filter data using SQL WHERE clause.
        
        Args:
            condition: SQL WHERE condition
            
        Returns:
            Filtered CSVData
        """
        return self.sql(f"SELECT * FROM data WHERE {condition}")
    
    def select(self, columns: list) -> CSVData:
        """
        Select specific columns.
        
        Args:
            columns: List of column names
            
        Returns:
            CSVData with selected columns
        """
        cols_str = ', '.join(columns)
        return self.sql(f"SELECT {cols_str} FROM data")
    
    def group_by(self, group_column: str, agg_column: str, agg_func: str = 'COUNT') -> CSVData:
        """
        Group data by column with aggregation.
        
        Args:
            group_column: Column to group by
            agg_column: Column to aggregate
            agg_func: Aggregation function (COUNT, AVG, SUM, etc.)
            
        Returns:
            Grouped CSVData
        """
        return self.sql(f"""
            SELECT {group_column}, {agg_func}({agg_column}) as {agg_func.lower()}_{agg_column}
            FROM data 
            GROUP BY {group_column}
        """)


# Updated import function that returns EnhancedLiveData
def import_enhanced(url: str) -> EnhancedLiveData:
    """
    Import data with enhanced functionality.
    
    Args:
        url: URL to import from (can include @ prefix)
        
    Returns:
        EnhancedLiveData object
    """
    # Remove @ prefix if present
    if url.startswith('@'):
        url = url[1:]
    
    return EnhancedLiveData(url)


# Global import function (main entry point)
def import_live(url: str) -> EnhancedLiveData:
    """
    Main import function for live data.
    
    Args:
        url: URL to import from (can include @ prefix)
        
    Returns:
        EnhancedLiveData object
    """
    return import_enhanced(url) 