"""
Data validation and cleaning functions for DataProcessing package.
"""

import re
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Callable
from .exceptions import ValidationError, DataTypeError


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid email format
    """
    if pd.isna(email) or email == '':
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, str(email)))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone string to validate
        
    Returns:
        True if valid phone format
    """
    if pd.isna(phone) or phone == '':
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', str(phone))
    
    # Check if it's a reasonable length (7-15 digits)
    return 7 <= len(digits_only) <= 15


def validate_date(date_str: str, format: Optional[str] = None) -> bool:
    """
    Validate date format.
    
    Args:
        date_str: Date string to validate
        format: Expected date format (auto-detect if None)
        
    Returns:
        True if valid date format
    """
    if pd.isna(date_str) or date_str == '':
        return False
    
    try:
        if format:
            pd.to_datetime(date_str, format=format)
        else:
            pd.to_datetime(date_str)
        return True
    except (ValueError, TypeError):
        return False


def validate_numeric(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    """
    Validate numeric value with optional range.
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        True if valid numeric value
    """
    if pd.isna(value):
        return False
    
    try:
        num_val = float(value)
        
        if min_val is not None and num_val < min_val:
            return False
        
        if max_val is not None and num_val > max_val:
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def validate_string_length(value: str, min_length: Optional[int] = None, max_length: Optional[int] = None) -> bool:
    """
    Validate string length.
    
    Args:
        value: String to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        
    Returns:
        True if valid string length
    """
    if pd.isna(value):
        return False
    
    str_val = str(value)
    length = len(str_val)
    
    if min_length is not None and length < min_length:
        return False
    
    if max_length is not None and length > max_length:
        return False
    
    return True


def validate_unique(series: pd.Series) -> bool:
    """
    Check if all values in a series are unique.
    
    Args:
        series: Pandas Series to check
        
    Returns:
        True if all values are unique
    """
    return series.nunique() == len(series)


def validate_categorical(series: pd.Series, allowed_values: List[Any]) -> bool:
    """
    Check if all values in a series are from allowed categories.
    
    Args:
        series: Pandas Series to check
        allowed_values: List of allowed values
        
    Returns:
        True if all values are from allowed categories
    """
    unique_values = set(series.dropna().unique())
    allowed_set = set(allowed_values)
    return unique_values.issubset(allowed_set)


def validate_dataframe(
    df: pd.DataFrame,
    rules: Dict[str, Dict[str, Any]]
) -> Dict[str, List[ValidationError]]:
    """
    Validate DataFrame against a set of rules.
    
    Args:
        df: DataFrame to validate
        rules: Dictionary mapping column names to validation rules
        
    Returns:
        Dictionary mapping column names to list of validation errors
    """
    errors = {}
    
    for column, rule_set in rules.items():
        if column not in df.columns:
            errors[column] = [ValidationError(f"Column '{column}' not found", column=column)]
            continue
        
        column_errors = []
        series = df[column]
        
        for rule_type, rule_params in rule_set.items():
            try:
                if rule_type == 'required':
                    if rule_params and series.isna().any():
                        null_indices = series[series.isna()].index.tolist()
                        column_errors.append(
                            ValidationError(f"Column '{column}' has {len(null_indices)} missing values", 
                                          column=column, row=null_indices)
                        )
                
                elif rule_type == 'email':
                    if rule_params:
                        invalid_emails = series[~series.apply(validate_email)]
                        if not invalid_emails.empty:
                            invalid_indices = invalid_emails.index.tolist()
                            column_errors.append(
                                ValidationError(f"Column '{column}' has {len(invalid_indices)} invalid emails", 
                                              column=column, row=invalid_indices)
                            )
                
                elif rule_type == 'phone':
                    if rule_params:
                        invalid_phones = series[~series.apply(validate_phone)]
                        if not invalid_phones.empty:
                            invalid_indices = invalid_phones.index.tolist()
                            column_errors.append(
                                ValidationError(f"Column '{column}' has {len(invalid_indices)} invalid phone numbers", 
                                              column=column, row=invalid_indices)
                            )
                
                elif rule_type == 'date':
                    format_param = rule_params.get('format') if isinstance(rule_params, dict) else None
                    invalid_dates = series[~series.apply(lambda x: validate_date(x, format_param))]
                    if not invalid_dates.empty:
                        invalid_indices = invalid_dates.index.tolist()
                        column_errors.append(
                            ValidationError(f"Column '{column}' has {len(invalid_indices)} invalid dates", 
                                          column=column, row=invalid_indices)
                        )
                
                elif rule_type == 'numeric':
                    min_val = rule_params.get('min') if isinstance(rule_params, dict) else None
                    max_val = rule_params.get('max') if isinstance(rule_params, dict) else None
                    invalid_nums = series[~series.apply(lambda x: validate_numeric(x, min_val, max_val))]
                    if not invalid_nums.empty:
                        invalid_indices = invalid_nums.index.tolist()
                        column_errors.append(
                            ValidationError(f"Column '{column}' has {len(invalid_indices)} invalid numeric values", 
                                          column=column, row=invalid_indices)
                        )
                
                elif rule_type == 'length':
                    min_len = rule_params.get('min') if isinstance(rule_params, dict) else None
                    max_len = rule_params.get('max') if isinstance(rule_params, dict) else None
                    invalid_lengths = series[~series.apply(lambda x: validate_string_length(x, min_len, max_len))]
                    if not invalid_lengths.empty:
                        invalid_indices = invalid_lengths.index.tolist()
                        column_errors.append(
                            ValidationError(f"Column '{column}' has {len(invalid_indices)} values with invalid length", 
                                          column=column, row=invalid_indices)
                        )
                
                elif rule_type == 'unique':
                    if rule_params and not validate_unique(series):
                        column_errors.append(
                            ValidationError(f"Column '{column}' has duplicate values", column=column)
                        )
                
                elif rule_type == 'categorical':
                    if isinstance(rule_params, list) and not validate_categorical(series, rule_params):
                        invalid_values = set(series.dropna().unique()) - set(rule_params)
                        column_errors.append(
                            ValidationError(f"Column '{column}' has invalid values: {invalid_values}", column=column)
                        )
                
                elif rule_type == 'custom':
                    if callable(rule_params):
                        invalid_custom = series[~series.apply(rule_params)]
                        if not invalid_custom.empty:
                            invalid_indices = invalid_custom.index.tolist()
                            column_errors.append(
                                ValidationError(f"Column '{column}' has {len(invalid_indices)} values failing custom validation", 
                                              column=column, row=invalid_indices)
                            )
            
            except Exception as e:
                column_errors.append(
                    ValidationError(f"Error applying rule '{rule_type}' to column '{column}': {str(e)}", column=column)
                )
        
        if column_errors:
            errors[column] = column_errors
    
    return errors


def clean_dataframe(
    df: pd.DataFrame,
    cleaning_rules: Dict[str, Dict[str, Any]]
) -> pd.DataFrame:
    """
    Clean DataFrame based on cleaning rules.
    
    Args:
        df: DataFrame to clean
        cleaning_rules: Dictionary mapping column names to cleaning rules
        
    Returns:
        Cleaned DataFrame
    """
    df_clean = df.copy()
    
    for column, rules in cleaning_rules.items():
        if column not in df_clean.columns:
            continue
        
        for rule_type, rule_params in rules.items():
            if rule_type == 'fill_missing':
                df_clean[column] = df_clean[column].fillna(rule_params)
            
            elif rule_type == 'strip_whitespace':
                if rule_params:
                    df_clean[column] = df_clean[column].astype(str).str.strip()
            
            elif rule_type == 'lowercase':
                if rule_params:
                    df_clean[column] = df_clean[column].astype(str).str.lower()
            
            elif rule_type == 'uppercase':
                if rule_params:
                    df_clean[column] = df_clean[column].astype(str).str.upper()
            
            elif rule_type == 'replace':
                if isinstance(rule_params, dict):
                    for old_val, new_val in rule_params.items():
                        df_clean[column] = df_clean[column].replace(old_val, new_val)
            
            elif rule_type == 'regex_replace':
                if isinstance(rule_params, dict):
                    for pattern, replacement in rule_params.items():
                        df_clean[column] = df_clean[column].astype(str).str.replace(pattern, replacement, regex=True)
            
            elif rule_type == 'round':
                if isinstance(rule_params, int):
                    df_clean[column] = pd.to_numeric(df_clean[column], errors='coerce').round(rule_params)
            
            elif rule_type == 'custom':
                if callable(rule_params):
                    df_clean[column] = df_clean[column].apply(rule_params)
    
    return df_clean


def get_validation_summary(validation_errors: Dict[str, List[ValidationError]]) -> Dict[str, Any]:
    """
    Get a summary of validation errors.
    
    Args:
        validation_errors: Dictionary of validation errors from validate_dataframe
        
    Returns:
        Summary dictionary
    """
    total_errors = sum(len(errors) for errors in validation_errors.values())
    columns_with_errors = len(validation_errors)
    
    error_types = {}
    for column, errors in validation_errors.items():
        for error in errors:
            error_type = type(error).__name__
            error_types[error_type] = error_types.get(error_type, 0) + 1
    
    return {
        'total_errors': total_errors,
        'columns_with_errors': columns_with_errors,
        'error_types': error_types,
        'validation_passed': total_errors == 0
    } 