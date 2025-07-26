"""
Custom exceptions for DataProcessing package.
"""

class DataProcessingError(Exception):
    """Base exception for DataProcessing package."""
    pass


class FileReadError(DataProcessingError):
    """Raised when there's an error reading a CSV file."""
    
    def __init__(self, file_path, original_error=None):
        self.file_path = file_path
        self.original_error = original_error
        
        if isinstance(original_error, UnicodeDecodeError):
            message = f"Unable to read file encoding for '{file_path}'. Try specifying encoding='utf-8' or encoding='latin-1'"
        elif isinstance(original_error, FileNotFoundError):
            message = f"File not found: '{file_path}'"
        elif isinstance(original_error, PermissionError):
            message = f"Permission denied: '{file_path}'"
        else:
            message = f"Error reading file '{file_path}': {str(original_error)}"
        
        super().__init__(message)


class ColumnNotFoundError(DataProcessingError):
    """Raised when a column is not found in the CSV data."""
    
    def __init__(self, column_name, available_columns=None):
        self.column_name = column_name
        self.available_columns = list(available_columns) if available_columns is not None else []
        
        # Try to suggest similar column names
        if self.available_columns:
            import difflib
            suggestions = difflib.get_close_matches(column_name, self.available_columns, n=3, cutoff=0.6)
            
            if suggestions:
                suggestion_text = f" Did you mean: {', '.join(suggestions)}?"
            else:
                suggestion_text = f" Available columns: {', '.join(self.available_columns)}"
        else:
            suggestion_text = ""
        
        message = f"Column '{column_name}' not found.{suggestion_text}"
        super().__init__(message)


class ValidationError(DataProcessingError):
    """Raised when data validation fails."""
    
    def __init__(self, message, column=None, row=None):
        self.column = column
        self.row = row
        
        if column and row is not None:
            message = f"Validation error in column '{column}' at row {row}: {message}"
        elif column:
            message = f"Validation error in column '{column}': {message}"
        
        super().__init__(message)


class DataTypeError(DataProcessingError):
    """Raised when there's a data type conversion error."""
    
    def __init__(self, column, value, expected_type):
        self.column = column
        self.value = value
        self.expected_type = expected_type
        
        message = f"Cannot convert value '{value}' in column '{column}' to {expected_type}"
        super().__init__(message)


class SaveError(DataProcessingError):
    """Raised when there's an error saving a CSV file."""
    
    def __init__(self, file_path, original_error=None):
        self.file_path = file_path
        self.original_error = original_error
        
        if isinstance(original_error, PermissionError):
            message = f"Permission denied when saving to '{file_path}'"
        elif isinstance(original_error, FileNotFoundError):
            message = f"Directory not found for saving '{file_path}'"
        else:
            message = f"Error saving file '{file_path}': {str(original_error)}"
        
        super().__init__(message) 