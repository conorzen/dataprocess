"""
SQL functionality for DataProcessing package.
Allows users to write SQL queries on CSV data.
"""

import pandas as pd
import sqlite3
import tempfile
import os
from typing import Union, List, Dict, Any, Optional
from pathlib import Path
from .exceptions import DataProcessingError


class SQLProcessor:
    """
    SQL processor for CSV data using SQLite backend.
    """
    
    def __init__(self, data: Union[pd.DataFrame, 'CSVData']):
        """
        Initialize SQL processor with data.
        
        Args:
            data: DataFrame or CSVData object
        """
        if hasattr(data, 'df'):
            # CSVData object
            self.df = data.df.copy()
        else:
            # DataFrame
            self.df = data.copy()
        
        self._temp_db = None
        self._connection = None
        self._setup_database()
    
    def _setup_database(self):
        """Set up temporary SQLite database with the data."""
        # Create temporary database file
        self._temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self._temp_db.close()
        
        # Create connection
        self._connection = sqlite3.connect(self._temp_db.name)
        
        # Write DataFrame to SQLite
        self.df.to_sql('data', self._connection, if_exists='replace', index=False)
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute SQL query on the data.
        
        Args:
            sql: SQL query string
            
        Returns:
            DataFrame with query results
        """
        try:
            result = pd.read_sql_query(sql, self._connection)
            return result
        except Exception as e:
            raise DataProcessingError(f"SQL query failed: {str(e)}")
    
    def execute(self, sql: str) -> None:
        """
        Execute SQL statement (INSERT, UPDATE, DELETE, etc.).
        
        Args:
            sql: SQL statement
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(sql)
            self._connection.commit()
        except Exception as e:
            raise DataProcessingError(f"SQL execution failed: {str(e)}")
    
    def get_table_info(self) -> pd.DataFrame:
        """
        Get information about the table structure.
        
        Returns:
            DataFrame with column information
        """
        return pd.read_sql_query("PRAGMA table_info(data)", self._connection)
    
    def get_sample_data(self, limit: int = 5) -> pd.DataFrame:
        """
        Get sample data from the table.
        
        Args:
            limit: Number of rows to return
            
        Returns:
            DataFrame with sample data
        """
        return self.query(f"SELECT * FROM data LIMIT {limit}")
    
    def close(self):
        """Close the database connection and clean up."""
        if self._connection:
            self._connection.close()
        
        if self._temp_db and os.path.exists(self._temp_db.name):
            os.unlink(self._temp_db.name)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def sql_query(data: Union[pd.DataFrame, 'CSVData'], query: str) -> pd.DataFrame:
    """
    Execute SQL query on data.
    
    Args:
        data: DataFrame or CSVData object
        query: SQL query string
        
    Returns:
        DataFrame with query results
    """
    with SQLProcessor(data) as processor:
        return processor.query(query)


def sql_execute(data: Union[pd.DataFrame, 'CSVData'], sql: str) -> None:
    """
    Execute SQL statement on data.
    
    Args:
        data: DataFrame or CSVData object
        sql: SQL statement
    """
    with SQLProcessor(data) as processor:
        processor.execute(sql)


# Common SQL query templates
SQL_TEMPLATES = {
    'select_all': "SELECT * FROM data",
    'select_columns': "SELECT {columns} FROM data",
    'filter': "SELECT * FROM data WHERE {condition}",
    'sort': "SELECT * FROM data ORDER BY {column} {direction}",
    'group_by': "SELECT {group_columns}, {aggregate_functions} FROM data GROUP BY {group_columns}",
    'join': "SELECT * FROM data a JOIN {other_table} b ON a.{key1} = b.{key2}",
    'limit': "SELECT * FROM data LIMIT {limit}",
    'distinct': "SELECT DISTINCT {columns} FROM data",
    'count': "SELECT COUNT(*) as count FROM data",
    'summary': """
        SELECT 
            COUNT(*) as total_rows,
            COUNT(DISTINCT {column}) as unique_values,
            AVG({column}) as average,
            MIN({column}) as minimum,
            MAX({column}) as maximum
        FROM data
        WHERE {column} IS NOT NULL
    """
}


def build_query(template_name: str, **kwargs) -> str:
    """
    Build SQL query from template.
    
    Args:
        template_name: Name of the template to use
        **kwargs: Parameters to substitute in the template
        
    Returns:
        Formatted SQL query string
    """
    if template_name not in SQL_TEMPLATES:
        raise DataProcessingError(f"Unknown SQL template: {template_name}")
    
    template = SQL_TEMPLATES[template_name]
    return template.format(**kwargs)


# Helper functions for common operations
def select_columns(data: Union[pd.DataFrame, 'CSVData'], columns: List[str]) -> pd.DataFrame:
    """
    Select specific columns using SQL.
    
    Args:
        data: DataFrame or CSVData object
        columns: List of column names to select
        
    Returns:
        DataFrame with selected columns
    """
    columns_str = ', '.join(columns)
    query = build_query('select_columns', columns=columns_str)
    return sql_query(data, query)


def filter_data(data: Union[pd.DataFrame, 'CSVData'], condition: str) -> pd.DataFrame:
    """
    Filter data using SQL WHERE clause.
    
    Args:
        data: DataFrame or CSVData object
        condition: SQL WHERE condition
        
    Returns:
        Filtered DataFrame
    """
    query = build_query('filter', condition=condition)
    return sql_query(data, query)


def sort_data(data: Union[pd.DataFrame, 'CSVData'], column: str, ascending: bool = True) -> pd.DataFrame:
    """
    Sort data using SQL ORDER BY.
    
    Args:
        data: DataFrame or CSVData object
        column: Column to sort by
        ascending: Sort order
        
    Returns:
        Sorted DataFrame
    """
    direction = 'ASC' if ascending else 'DESC'
    query = build_query('sort', column=column, direction=direction)
    return sql_query(data, query)


def group_by(data: Union[pd.DataFrame, 'CSVData'], group_columns: List[str], 
             aggregate_functions: Dict[str, str]) -> pd.DataFrame:
    """
    Group data using SQL GROUP BY.
    
    Args:
        data: DataFrame or CSVData object
        group_columns: Columns to group by
        aggregate_functions: Dictionary mapping column names to aggregate functions
        
    Returns:
        Grouped DataFrame
    """
    group_cols_str = ', '.join(group_columns)
    agg_funcs_str = ', '.join([f"{func}({col}) as {col}_{func.lower()}" 
                              for col, func in aggregate_functions.items()])
    
    # Build query manually since template has issues
    query = f"SELECT {group_cols_str}, {agg_funcs_str} FROM data GROUP BY {group_cols_str}"
    return sql_query(data, query)


def get_summary(data: Union[pd.DataFrame, 'CSVData'], column: str) -> pd.DataFrame:
    """
    Get summary statistics for a column using SQL.
    
    Args:
        data: DataFrame or CSVData object
        column: Column to summarize
        
    Returns:
        DataFrame with summary statistics
    """
    query = build_query('summary', column=column)
    return sql_query(data, query)


def get_distinct_values(data: Union[pd.DataFrame, 'CSVData'], columns: List[str]) -> pd.DataFrame:
    """
    Get distinct values using SQL DISTINCT.
    
    Args:
        data: DataFrame or CSVData object
        columns: Columns to get distinct values for
        
    Returns:
        DataFrame with distinct values
    """
    columns_str = ', '.join(columns)
    query = build_query('distinct', columns=columns_str)
    return sql_query(data, query) 