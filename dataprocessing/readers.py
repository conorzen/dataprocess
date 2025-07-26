"""
CSV file reading functionality for DataProcessing package.
"""

import pandas as pd
import gzip
import zipfile
from pathlib import Path
from typing import Optional, Union, Dict, Any
from .exceptions import FileReadError
from .utils import (
    detect_encoding, 
    detect_delimiter, 
    is_compressed_file,
    validate_file_path,
    format_file_size
)


def read_csv_file(
    file_path: Union[str, Path],
    encoding: Optional[str] = None,
    delimiter: Optional[str] = None,
    header: Optional[int] = 0,
    **kwargs
) -> pd.DataFrame:
    """
    Read a CSV file with smart parameter detection.
    
    Args:
        file_path: Path to the CSV file
        encoding: File encoding (auto-detected if None)
        delimiter: CSV delimiter (auto-detected if None)
        header: Row number to use as header (0 for first row, None for no header)
        **kwargs: Additional pandas read_csv parameters
        
    Returns:
        Pandas DataFrame
        
    Raises:
        FileReadError: If there's an error reading the file
    """
    file_path = Path(file_path)
    
    try:
        # Validate file exists
        validate_file_path(file_path)
        
        # Auto-detect encoding if not provided
        if encoding is None:
            encoding = detect_encoding(file_path)
        
        # Auto-detect delimiter if not provided
        if delimiter is None:
            delimiter = detect_delimiter(file_path, encoding)
        
        # Handle compressed files
        if is_compressed_file(file_path):
            return _read_compressed_csv(file_path, encoding, delimiter, header, **kwargs)
        
        # Read the CSV file
        df = pd.read_csv(
            file_path,
            encoding=encoding,
            sep=delimiter,
            header=header,
            **kwargs
        )
        
        return df
        
    except Exception as e:
        raise FileReadError(file_path, e)


def _read_compressed_csv(
    file_path: Path,
    encoding: str,
    delimiter: str,
    header: Optional[int],
    **kwargs
) -> pd.DataFrame:
    """
    Read a compressed CSV file.
    
    Args:
        file_path: Path to the compressed file
        encoding: File encoding
        delimiter: CSV delimiter
        header: Row number to use as header
        **kwargs: Additional pandas read_csv parameters
        
    Returns:
        Pandas DataFrame
    """
    file_extension = file_path.suffix.lower()
    
    if file_extension == '.gz':
        with gzip.open(file_path, 'rt', encoding=encoding) as f:
            return pd.read_csv(f, sep=delimiter, header=header, **kwargs)
    
    elif file_extension == '.zip':
        # For zip files, we need to extract and read the first CSV file
        with zipfile.ZipFile(file_path, 'r') as zip_file:
            csv_files = [f for f in zip_file.namelist() if f.lower().endswith('.csv')]
            if not csv_files:
                raise FileReadError(file_path, ValueError("No CSV files found in zip archive"))
            
            # Use the first CSV file
            csv_file = csv_files[0]
            with zip_file.open(csv_file) as f:
                return pd.read_csv(f, encoding=encoding, sep=delimiter, header=header, **kwargs)
    
    else:
        raise FileReadError(file_path, ValueError(f"Unsupported compression format: {file_extension}"))


def read_csv_with_info(
    file_path: Union[str, Path],
    **kwargs
) -> Dict[str, Any]:
    """
    Read a CSV file and return both the data and metadata.
    
    Args:
        file_path: Path to the CSV file
        **kwargs: Additional parameters for read_csv_file
        
    Returns:
        Dictionary containing 'data' (DataFrame) and 'info' (metadata)
    """
    file_path = Path(file_path)
    
    # Read the data
    df = read_csv_file(file_path, **kwargs)
    
    # Gather metadata
    info = {
        'file_path': str(file_path),
        'file_size': format_file_size(file_path),
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': list(df.columns),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'dtypes': df.dtypes.to_dict(),
        'null_counts': df.isnull().sum().to_dict(),
        'compressed': is_compressed_file(file_path)
    }
    
    return {
        'data': df,
        'info': info
    }


def preview_csv(
    file_path: Union[str, Path],
    n_rows: int = 5,
    **kwargs
) -> pd.DataFrame:
    """
    Preview the first few rows of a CSV file.
    
    Args:
        file_path: Path to the CSV file
        n_rows: Number of rows to preview
        **kwargs: Additional parameters for read_csv_file
        
    Returns:
        DataFrame with preview data
    """
    kwargs['nrows'] = n_rows
    return read_csv_file(file_path, **kwargs)


def get_csv_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get information about a CSV file without loading all data.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dictionary with file information
    """
    file_path = Path(file_path)
    
    try:
        validate_file_path(file_path)
        
        # Get basic file info
        info = {
            'file_path': str(file_path),
            'file_size': format_file_size(file_path),
            'compressed': is_compressed_file(file_path)
        }
        
        # Try to get column names and row count
        try:
            encoding = detect_encoding(file_path)
            delimiter = detect_delimiter(file_path, encoding)
            
            # Read just the header
            if is_compressed_file(file_path):
                if file_path.suffix.lower() == '.gz':
                    with gzip.open(file_path, 'rt', encoding=encoding) as f:
                        header = f.readline().strip()
                else:
                    # For zip files, this is more complex, so we'll skip for now
                    header = ""
            else:
                with open(file_path, 'r', encoding=encoding) as f:
                    header = f.readline().strip()
            
            if header:
                columns = header.split(delimiter)
                info['columns'] = len(columns)
                info['column_names'] = columns
                
                # Try to estimate row count (rough estimate)
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        line_count = sum(1 for _ in f)
                    info['estimated_rows'] = line_count - 1  # Subtract header
                except:
                    info['estimated_rows'] = 'Unknown'
            
        except Exception:
            info['columns'] = 'Unknown'
            info['column_names'] = []
            info['estimated_rows'] = 'Unknown'
        
        return info
        
    except Exception as e:
        raise FileReadError(file_path, e) 