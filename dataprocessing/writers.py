"""
CSV file writing functionality for DataProcessing package.
"""

import pandas as pd
import gzip
from pathlib import Path
from typing import Optional, Union, Dict, Any
from .exceptions import SaveError
from .utils import is_compressed_file


def save_csv_file(
    df: pd.DataFrame,
    file_path: Union[str, Path],
    index: bool = False,
    encoding: str = 'utf-8',
    delimiter: str = ',',
    **kwargs
) -> None:
    """
    Save a DataFrame to a CSV file with smart formatting.
    
    Args:
        df: Pandas DataFrame to save
        file_path: Path where to save the file
        index: Whether to include the index
        encoding: File encoding
        delimiter: CSV delimiter
        **kwargs: Additional pandas to_csv parameters
        
    Raises:
        SaveError: If there's an error saving the file
    """
    file_path = Path(file_path)
    
    try:
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle compressed files
        if is_compressed_file(file_path):
            _save_compressed_csv(df, file_path, index, encoding, delimiter, **kwargs)
        else:
            # Save regular CSV
            df.to_csv(
                file_path,
                index=index,
                encoding=encoding,
                sep=delimiter,
                **kwargs
            )
            
    except Exception as e:
        raise SaveError(file_path, e)


def _save_compressed_csv(
    df: pd.DataFrame,
    file_path: Path,
    index: bool,
    encoding: str,
    delimiter: str,
    **kwargs
) -> None:
    """
    Save a DataFrame to a compressed CSV file.
    
    Args:
        df: Pandas DataFrame to save
        file_path: Path where to save the file
        index: Whether to include the index
        encoding: File encoding
        delimiter: CSV delimiter
        **kwargs: Additional pandas to_csv parameters
    """
    file_extension = file_path.suffix.lower()
    
    if file_extension == '.gz':
        with gzip.open(file_path, 'wt', encoding=encoding) as f:
            df.to_csv(f, index=index, sep=delimiter, **kwargs)
    else:
        raise SaveError(file_path, ValueError(f"Unsupported compression format: {file_extension}"))


def save_csv_with_info(
    df: pd.DataFrame,
    file_path: Union[str, Path],
    **kwargs
) -> Dict[str, Any]:
    """
    Save a DataFrame to CSV and return information about the saved file.
    
    Args:
        df: Pandas DataFrame to save
        file_path: Path where to save the file
        **kwargs: Additional parameters for save_csv_file
        
    Returns:
        Dictionary with save information
    """
    file_path = Path(file_path)
    
    # Save the file
    save_csv_file(df, file_path, **kwargs)
    
    # Gather information about the saved file
    info = {
        'file_path': str(file_path),
        'rows': len(df),
        'columns': len(df.columns),
        'file_size': _get_file_size(file_path),
        'compressed': is_compressed_file(file_path)
    }
    
    return info


def _get_file_size(file_path: Path) -> str:
    """
    Get file size in human-readable format.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Formatted file size string
    """
    try:
        size = file_path.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except OSError:
        return "Unknown size"


def export_to_formats(
    df: pd.DataFrame,
    base_path: Union[str, Path],
    formats: list = None,
    **kwargs
) -> Dict[str, str]:
    """
    Export DataFrame to multiple formats.
    
    Args:
        df: Pandas DataFrame to export
        base_path: Base path for the files (without extension)
        formats: List of formats to export to (default: ['csv', 'json', 'excel'])
        **kwargs: Additional parameters for saving
        
    Returns:
        Dictionary mapping format to file path
    """
    if formats is None:
        formats = ['csv', 'json', 'excel']
    
    base_path = Path(base_path)
    exported_files = {}
    
    for format_type in formats:
        try:
            if format_type == 'csv':
                file_path = base_path.with_suffix('.csv')
                save_csv_file(df, file_path, **kwargs)
                exported_files['csv'] = str(file_path)
                
            elif format_type == 'json':
                file_path = base_path.with_suffix('.json')
                df.to_json(file_path, orient='records', indent=2)
                exported_files['json'] = str(file_path)
                
            elif format_type == 'excel':
                file_path = base_path.with_suffix('.xlsx')
                df.to_excel(file_path, index=False)
                exported_files['excel'] = str(file_path)
                
            elif format_type == 'parquet':
                file_path = base_path.with_suffix('.parquet')
                df.to_parquet(file_path, index=False)
                exported_files['parquet'] = str(file_path)
                
        except Exception as e:
            # Log the error but continue with other formats
            print(f"Failed to export to {format_type}: {e}")
    
    return exported_files


def save_with_backup(
    df: pd.DataFrame,
    file_path: Union[str, Path],
    backup_suffix: str = '.backup',
    **kwargs
) -> None:
    """
    Save a DataFrame with automatic backup of existing file.
    
    Args:
        df: Pandas DataFrame to save
        file_path: Path where to save the file
        backup_suffix: Suffix for backup files
        **kwargs: Additional parameters for save_csv_file
    """
    file_path = Path(file_path)
    
    # Create backup if file exists
    if file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + backup_suffix)
        file_path.rename(backup_path)
    
    # Save the new file
    save_csv_file(df, file_path, **kwargs)


def save_partitioned(
    df: pd.DataFrame,
    base_path: Union[str, Path],
    partition_column: str,
    max_rows_per_file: int = 10000,
    **kwargs
) -> list:
    """
    Save a DataFrame partitioned by a column into multiple files.
    
    Args:
        df: Pandas DataFrame to save
        base_path: Base path for the files
        partition_column: Column to partition by
        max_rows_per_file: Maximum rows per file
        **kwargs: Additional parameters for save_csv_file
        
    Returns:
        List of saved file paths
    """
    base_path = Path(base_path)
    saved_files = []
    
    # Get unique values in partition column
    partition_values = df[partition_column].unique()
    
    for value in partition_values:
        # Filter data for this partition
        partition_data = df[df[partition_column] == value]
        
        # Create safe filename
        safe_value = str(value).replace('/', '_').replace('\\', '_')
        file_path = base_path.parent / f"{base_path.stem}_{safe_value}{base_path.suffix}"
        
        # Split into chunks if too large
        if len(partition_data) > max_rows_per_file:
            chunks = [partition_data[i:i + max_rows_per_file] 
                     for i in range(0, len(partition_data), max_rows_per_file)]
            
            for i, chunk in enumerate(chunks):
                chunk_file_path = file_path.parent / f"{file_path.stem}_part{i+1}{file_path.suffix}"
                save_csv_file(chunk, chunk_file_path, **kwargs)
                saved_files.append(str(chunk_file_path))
        else:
            save_csv_file(partition_data, file_path, **kwargs)
            saved_files.append(str(file_path))
    
    return saved_files 