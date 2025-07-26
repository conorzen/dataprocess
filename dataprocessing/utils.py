"""
Utility functions for DataProcessing package.
"""

import os
import gzip
import zipfile
import chardet
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
import pandas as pd


def detect_encoding(file_path: Union[str, Path], sample_size: int = 10000) -> str:
    """
    Detect the encoding of a file.
    
    Args:
        file_path: Path to the file
        sample_size: Number of bytes to sample for detection
        
    Returns:
        Detected encoding string
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(sample_size)
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    except Exception:
        return 'utf-8'


def detect_delimiter(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """
    Detect the delimiter used in a CSV file.
    
    Args:
        file_path: Path to the CSV file
        encoding: File encoding
        
    Returns:
        Detected delimiter string
    """
    delimiters = [',', ';', '\t', '|', ' ']
    
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            first_line = f.readline().strip()
            
        if not first_line:
            return ','
        
        # Count occurrences of each delimiter
        delimiter_counts = {}
        for delim in delimiters:
            delimiter_counts[delim] = first_line.count(delim)
        
        # Return the most common delimiter
        return max(delimiter_counts, key=delimiter_counts.get)
    except Exception:
        return ','


def is_compressed_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is compressed (gzip or zip).
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is compressed
    """
    file_path = str(file_path).lower()
    return file_path.endswith(('.gz', '.zip'))


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get the file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (lowercase)
    """
    return Path(file_path).suffix.lower()


def validate_file_path(file_path: Union[str, Path]) -> Path:
    """
    Validate and normalize file path.
    
    Args:
        file_path: Path to validate
        
    Returns:
        Normalized Path object
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    return path


def infer_data_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Infer data types for DataFrame columns.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        Dictionary mapping column names to inferred types
    """
    type_mapping = {}
    
    for col in df.columns:
        # Skip if column is all null
        if df[col].isna().all():
            type_mapping[col] = 'object'
            continue
            
        # Get non-null values
        non_null_values = df[col].dropna()
        
        if len(non_null_values) == 0:
            type_mapping[col] = 'object'
            continue
            
        # Try to infer type
        sample_values = non_null_values.head(100)
        
        # Check if numeric
        try:
            pd.to_numeric(sample_values)
            if sample_values.dtype == 'int64' or all(float(x).is_integer() for x in sample_values if pd.notna(x)):
                type_mapping[col] = 'int'
            else:
                type_mapping[col] = 'float'
        except (ValueError, TypeError):
            # Check if boolean
            if set(sample_values.astype(str).str.lower()) <= {'true', 'false', '1', '0', 'yes', 'no'}:
                type_mapping[col] = 'bool'
            # Check if date
            elif _is_date_column(sample_values):
                type_mapping[col] = 'date'
            else:
                type_mapping[col] = 'object'
    
    return type_mapping


def _is_date_column(values) -> bool:
    """
    Check if a column contains date-like values.
    
    Args:
        values: Series of values to check
        
    Returns:
        True if column appears to contain dates
    """
    from dateutil import parser
    
    date_count = 0
    total_count = 0
    
    for value in values:
        if pd.isna(value):
            continue
            
        total_count += 1
        try:
            parser.parse(str(value))
            date_count += 1
        except (ValueError, TypeError):
            pass
    
    # If more than 70% of non-null values are dates, consider it a date column
    return total_count > 0 and (date_count / total_count) > 0.7


def format_file_size(file_path: Union[str, Path]) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Formatted file size string
    """
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except OSError:
        return "Unknown size"


def get_column_statistics(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Get detailed statistics for a column.
    
    Args:
        df: Pandas DataFrame
        column: Column name
        
    Returns:
        Dictionary with column statistics
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found")
    
    col_data = df[column]
    stats = {
        'name': column,
        'dtype': str(col_data.dtype),
        'total_count': len(col_data),
        'null_count': col_data.isna().sum(),
        'null_percentage': (col_data.isna().sum() / len(col_data)) * 100,
        'unique_count': col_data.nunique(),
        'unique_percentage': (col_data.nunique() / len(col_data)) * 100
    }
    
    # Add type-specific statistics
    if pd.api.types.is_numeric_dtype(col_data):
        non_null = col_data.dropna()
        if len(non_null) > 0:
            stats.update({
                'min': float(non_null.min()),
                'max': float(non_null.max()),
                'mean': float(non_null.mean()),
                'median': float(non_null.median()),
                'std': float(non_null.std())
            })
    elif pd.api.types.is_string_dtype(col_data):
        non_null = col_data.dropna()
        if len(non_null) > 0:
            stats.update({
                'min_length': int(non_null.astype(str).str.len().min()),
                'max_length': int(non_null.astype(str).str.len().max()),
                'avg_length': float(non_null.astype(str).str.len().mean())
            })
    
    return stats


def sanitize_column_name(name: str) -> str:
    """
    Sanitize a column name for safe use.
    
    Args:
        name: Original column name
        
    Returns:
        Sanitized column name
    """
    import re
    
    # Remove or replace problematic characters
    sanitized = re.sub(r'[^\w\s-]', '_', str(name))
    sanitized = re.sub(r'[\s-]+', '_', sanitized)
    sanitized = sanitized.strip('_')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'unnamed_column'
    
    # Ensure it doesn't start with a number
    if sanitized[0].isdigit():
        sanitized = 'col_' + sanitized
    
    return sanitized 