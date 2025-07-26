"""
Core CSVData class and main functions for DataProcessing package.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, Callable
from .readers import read_csv_file, read_csv_with_info, preview_csv, get_csv_info
from .writers import save_csv_file, save_csv_with_info, export_to_formats
from .exceptions import ColumnNotFoundError, ValidationError, DataTypeError
from .utils import get_column_statistics, infer_data_types, sanitize_column_name
from .sql import SQLProcessor, sql_query, sql_execute
from .live_data import LiveDataManager, connect_database, connect_api, create_stream, load_from_database, load_from_api


class CSVData:
    """
    A user-friendly wrapper around pandas DataFrame for CSV operations.
    """
    
    def __init__(self, data: Union[pd.DataFrame, str, Path], **kwargs):
        """
        Initialize CSVData with a DataFrame or file path.
        
        Args:
            data: DataFrame or path to CSV file
            **kwargs: Additional parameters for reading CSV files
        """
        if isinstance(data, pd.DataFrame):
            self._df = data.copy()
        elif isinstance(data, (str, Path)):
            self._df = read_csv_file(data, **kwargs)
        else:
            raise ValueError("Data must be a DataFrame or file path")
    
    @property
    def df(self) -> pd.DataFrame:
        """Get the underlying pandas DataFrame."""
        return self._df
    
    @property
    def shape(self) -> tuple:
        """Get the shape of the data (rows, columns)."""
        return self._df.shape
    
    @property
    def columns(self) -> List[str]:
        """Get the column names."""
        return list(self._df.columns)
    
    @property
    def dtypes(self) -> Dict[str, str]:
        """Get the data types of columns."""
        return self._df.dtypes.to_dict()
    
    def __len__(self) -> int:
        """Get the number of rows."""
        return len(self._df)
    
    def __getitem__(self, key):
        """Get a column or slice of data."""
        if isinstance(key, str):
            if key not in self._df.columns:
                raise ColumnNotFoundError(key, self._df.columns)
            return self._df[key]
        else:
            return CSVData(self._df[key])
    
    def __repr__(self) -> str:
        """String representation of the CSVData object."""
        return f"CSVData(shape={self.shape}, columns={len(self.columns)})"
    
    def head(self, n: int = 5) -> pd.DataFrame:
        """Get the first n rows."""
        return self._df.head(n)
    
    def tail(self, n: int = 5) -> pd.DataFrame:
        """Get the last n rows."""
        return self._df.tail(n)
    
    def sample(self, n: int = 5, random_state: Optional[int] = None) -> pd.DataFrame:
        """Get a random sample of n rows."""
        return self._df.sample(n=n, random_state=random_state)
    
    def where(self, condition) -> 'CSVData':
        """
        Filter data based on a condition.
        
        Args:
            condition: Boolean condition (e.g., age > 25)
            
        Returns:
            Filtered CSVData object
        """
        # Handle column-based conditions
        if hasattr(condition, '__name__') and condition.__name__ == '<lambda>':
            # Lambda function - apply to DataFrame
            filtered_df = self._df[condition(self._df)]
        else:
            # Try to evaluate the condition
            try:
                # Create a copy of the DataFrame for evaluation
                df_copy = self._df.copy()
                filtered_df = df_copy[eval(str(condition), {'df': df_copy, 'self': df_copy})]
            except Exception:
                # If evaluation fails, assume it's a pandas boolean series
                filtered_df = self._df[condition]
        
        return CSVData(filtered_df)
    
    def sort_by(self, column: str, ascending: bool = True) -> 'CSVData':
        """
        Sort data by a column.
        
        Args:
            column: Column name to sort by
            ascending: Sort order
            
        Returns:
            Sorted CSVData object
        """
        if column not in self._df.columns:
            raise ColumnNotFoundError(column, self._df.columns)
        
        sorted_df = self._df.sort_values(column, ascending=ascending)
        return CSVData(sorted_df)
    
    def select_columns(self, columns: List[str]) -> 'CSVData':
        """
        Select specific columns.
        
        Args:
            columns: List of column names to select
            
        Returns:
            CSVData object with selected columns
        """
        missing_columns = [col for col in columns if col not in self._df.columns]
        if missing_columns:
            raise ColumnNotFoundError(missing_columns[0], self._df.columns)
        
        selected_df = self._df[columns]
        return CSVData(selected_df)
    
    def drop_columns(self, columns: List[str]) -> 'CSVData':
        """
        Drop specific columns.
        
        Args:
            columns: List of column names to drop
            
        Returns:
            CSVData object without dropped columns
        """
        missing_columns = [col for col in columns if col not in self._df.columns]
        if missing_columns:
            raise ColumnNotFoundError(missing_columns[0], self._df.columns)
        
        dropped_df = self._df.drop(columns=columns)
        return CSVData(dropped_df)
    
    def rename_column(self, old_name: str, new_name: str) -> 'CSVData':
        """
        Rename a column.
        
        Args:
            old_name: Current column name
            new_name: New column name
            
        Returns:
            CSVData object with renamed column
        """
        if old_name not in self._df.columns:
            raise ColumnNotFoundError(old_name, self._df.columns)
        
        renamed_df = self._df.rename(columns={old_name: new_name})
        return CSVData(renamed_df)
    
    def add_column(self, name: str, values) -> 'CSVData':
        """
        Add a new column.
        
        Args:
            name: New column name
            values: Column values (can be Series, list, or scalar)
            
        Returns:
            CSVData object with new column
        """
        df_copy = self._df.copy()
        df_copy[name] = values
        return CSVData(df_copy)
    
    def fill_missing(self, column: str, value) -> 'CSVData':
        """
        Fill missing values in a column.
        
        Args:
            column: Column name
            value: Value to fill missing values with
            
        Returns:
            CSVData object with filled missing values
        """
        if column not in self._df.columns:
            raise ColumnNotFoundError(column, self._df.columns)
        
        df_copy = self._df.copy()
        df_copy[column] = df_copy[column].fillna(value)
        return CSVData(df_copy)
    
    def drop_missing(self, columns: Optional[List[str]] = None) -> 'CSVData':
        """
        Drop rows with missing values.
        
        Args:
            columns: Columns to check for missing values (all if None)
            
        Returns:
            CSVData object without missing values
        """
        if columns:
            missing_columns = [col for col in columns if col not in self._df.columns]
            if missing_columns:
                raise ColumnNotFoundError(missing_columns[0], self._df.columns)
            dropped_df = self._df.dropna(subset=columns)
        else:
            dropped_df = self._df.dropna()
        
        return CSVData(dropped_df)
    
    def drop_duplicates(self, subset: Optional[List[str]] = None) -> 'CSVData':
        """
        Remove duplicate rows.
        
        Args:
            subset: Columns to consider for duplicates (all if None)
            
        Returns:
            CSVData object without duplicates
        """
        if subset:
            missing_columns = [col for col in subset if col not in self._df.columns]
            if missing_columns:
                raise ColumnNotFoundError(missing_columns[0], self._df.columns)
            deduplicated_df = self._df.drop_duplicates(subset=subset)
        else:
            deduplicated_df = self._df.drop_duplicates()
        
        return CSVData(deduplicated_df)
    
    def summary(self) -> Dict[str, Any]:
        """
        Get a summary of the data.
        
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'shape': self.shape,
            'columns': len(self.columns),
            'memory_usage': self._df.memory_usage(deep=True).sum(),
            'dtypes': self.dtypes,
            'null_counts': self._df.isnull().sum().to_dict(),
            'numeric_columns': list(self._df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(self._df.select_dtypes(include=['object']).columns)
        }
        
        # Add basic statistics for numeric columns
        numeric_cols = self._df.select_dtypes(include=[np.number])
        if not numeric_cols.empty:
            summary['numeric_summary'] = numeric_cols.describe().to_dict()
        
        return summary
    
    def profile(self) -> Dict[str, Dict[str, Any]]:
        """
        Get detailed profile of each column.
        
        Returns:
            Dictionary with column profiles
        """
        profiles = {}
        for column in self.columns:
            profiles[column] = get_column_statistics(self._df, column)
        return profiles
    
    def check_missing(self) -> Dict[str, Any]:
        """
        Check for missing values in the data.
        
        Returns:
            Dictionary with missing value information
        """
        null_counts = self._df.isnull().sum()
        null_percentages = (null_counts / len(self._df)) * 100
        
        return {
            'total_rows': len(self._df),
            'columns_with_missing': list(null_counts[null_counts > 0].index),
            'null_counts': null_counts.to_dict(),
            'null_percentages': null_percentages.to_dict(),
            'total_missing': null_counts.sum()
        }
    
    def validate_types(self, type_mapping: Dict[str, str]) -> 'CSVData':
        """
        Validate and convert data types.
        
        Args:
            type_mapping: Dictionary mapping column names to expected types
            
        Returns:
            CSVData object with validated types
        """
        df_copy = self._df.copy()
        
        for column, expected_type in type_mapping.items():
            if column not in self._df.columns:
                raise ColumnNotFoundError(column, self._df.columns)
            
            try:
                if expected_type == 'int':
                    df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce').astype('Int64')
                elif expected_type == 'float':
                    df_copy[column] = pd.to_numeric(df_copy[column], errors='coerce')
                elif expected_type == 'bool':
                    df_copy[column] = df_copy[column].astype(bool)
                elif expected_type == 'date':
                    df_copy[column] = pd.to_datetime(df_copy[column], errors='coerce')
                elif expected_type == 'email':
                    # Basic email validation
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    df_copy[column] = df_copy[column].astype(str).str.match(email_pattern)
                else:
                    df_copy[column] = df_copy[column].astype(str)
                    
            except Exception as e:
                raise DataTypeError(column, str(df_copy[column].iloc[0]), expected_type)
        
        return CSVData(df_copy)
    
    def save(self, file_path: Union[str, Path], **kwargs) -> None:
        """
        Save the data to a CSV file.
        
        Args:
            file_path: Path where to save the file
            **kwargs: Additional parameters for saving
        """
        save_csv_file(self._df, file_path, **kwargs)
    
    def save_with_info(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Save the data and return information about the saved file.
        
        Args:
            file_path: Path where to save the file
            **kwargs: Additional parameters for saving
            
        Returns:
            Dictionary with save information
        """
        return save_csv_with_info(self._df, file_path, **kwargs)
    
    def export(self, base_path: Union[str, Path], formats: List[str] = None, **kwargs) -> Dict[str, str]:
        """
        Export data to multiple formats.
        
        Args:
            base_path: Base path for the files (without extension)
            formats: List of formats to export to
            **kwargs: Additional parameters for saving
            
        Returns:
            Dictionary mapping format to file path
        """
        return export_to_formats(self._df, base_path, formats, **kwargs)
    
    def to_pandas(self) -> pd.DataFrame:
        """Convert to pandas DataFrame."""
        return self._df.copy()
    
    def to_dict(self, orient: str = 'records') -> List[Dict[str, Any]]:
        """Convert to dictionary format."""
        return self._df.to_dict(orient=orient)
    
    def to_list(self) -> List[List[Any]]:
        """Convert to list of lists format."""
        return self._df.values.tolist()
    
    def sql(self, query: str) -> 'CSVData':
        """
        Execute SQL query on the data.
        
        Args:
            query: SQL query string
            
        Returns:
            CSVData object with query results
        """
        result_df = sql_query(self, query)
        return CSVData(result_df)
    
    def sql_processor(self) -> SQLProcessor:
        """
        Get SQL processor for advanced SQL operations.
        
        Returns:
            SQLProcessor object
        """
        return SQLProcessor(self)
    
    def live_data_manager(self) -> LiveDataManager:
        """
        Get live data manager for database and API connections.
        
        Returns:
            LiveDataManager object
        """
        return LiveDataManager()


def load(file_path: Union[str, Path], **kwargs) -> CSVData:
    """
    Load a CSV file into a CSVData object.
    
    Args:
        file_path: Path to the CSV file
        **kwargs: Additional parameters for reading
        
    Returns:
        CSVData object
    """
    return CSVData(file_path, **kwargs)


def save(data: CSVData, file_path: Union[str, Path], **kwargs) -> None:
    """
    Save a CSVData object to a file.
    
    Args:
        data: CSVData object to save
        file_path: Path where to save the file
        **kwargs: Additional parameters for saving
    """
    data.save(file_path, **kwargs)


def load_from_db(db_type: str, connection_string: str, query: str, **kwargs) -> CSVData:
    """
    Load data from database.
    
    Args:
        db_type: Database type ('sqlite', 'postgresql', 'mysql')
        connection_string: Database connection string
        query: SQL query to execute
        **kwargs: Additional connection parameters
        
    Returns:
        CSVData object with database results
    """
    df = load_from_database(db_type, connection_string, query, **kwargs)
    return CSVData(df)


def load_from_api(base_url: str, endpoint: str, **kwargs) -> CSVData:
    """
    Load data from API.
    
    Args:
        base_url: API base URL
        endpoint: API endpoint
        **kwargs: Additional API parameters
        
    Returns:
        CSVData object with API response
    """
    df = load_from_api(base_url, endpoint, **kwargs)
    return CSVData(df)


def create_live_stream(data_source: Callable, **kwargs) -> 'RealTimeDataStream':
    """
    Create a real-time data stream.
    
    Args:
        data_source: Function that returns data
        **kwargs: Additional stream parameters
        
    Returns:
        RealTimeDataStream object
    """
    return create_stream(data_source, **kwargs) 