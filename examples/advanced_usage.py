"""
Advanced usage examples for CSV Buddy package.
"""

import pandas as pd
import numpy as np
from dataprocessing import load, CSVData
from dataprocessing.validators import validate_dataframe, clean_dataframe, get_validation_summary

# Create more complex sample data with various data quality issues
sample_data = {
    'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'name': ['Alice Smith', 'Bob Johnson', 'Charlie Brown', 'Diana Prince', 'Eve Wilson', 
             'Frank Miller', 'Grace Lee', 'Henry Davis', 'Ivy Chen', 'Jack Wilson'],
    'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'diana@example.com', 'eve@example.com',
              'frank@example.com', 'grace@example.com', 'henry@example.com', 'ivy@example.com', 'jack@example.com'],
    'age': [25, 30, 35, 28, 32, 45, 29, 38, 26, 41],
    'phone': ['555-1234', '555-5678', '555-9012', '555-3456', '555-7890',
              '555-2345', '555-6789', '555-0123', '555-4567', '555-8901'],
    'salary': [50000, 60000, 70000, 55000, 65000, 80000, 52000, 75000, 48000, 85000],
    'department': ['Engineering', 'Marketing', 'Engineering', 'Sales', 'HR',
                   'Engineering', 'Marketing', 'Sales', 'HR', 'Engineering'],
    'hire_date': ['2020-01-15', '2019-03-20', '2018-07-10', '2021-02-28', '2020-11-05',
                  '2017-12-01', '2021-06-15', '2019-09-12', '2022-01-20', '2018-04-30'],
    'status': ['Active', 'Active', 'Active', 'Active', 'Active',
               'Active', 'Active', 'Active', 'Active', 'Active']
}

# Create DataFrame and introduce some data quality issues
df = pd.DataFrame(sample_data)

# Introduce some data quality issues
df.loc[2, 'email'] = 'invalid-email'  # Invalid email
df.loc[4, 'age'] = 150  # Invalid age
df.loc[6, 'phone'] = '123'  # Invalid phone
df.loc[8, 'salary'] = -5000  # Negative salary
df.loc[1, 'name'] = '   Bob Johnson   '  # Extra whitespace
df.loc[3, 'department'] = 'InvalidDept'  # Invalid department
df.loc[5, 'hire_date'] = '2023-13-45'  # Invalid date

# Save the problematic data
df.to_csv('problematic_data.csv', index=False)

print("=== DataProcessing Advanced Usage Examples ===\n")

# Example 1: Loading and initial inspection
print("1. Loading and initial inspection:")
data = load("problematic_data.csv")
print(f"Loaded data shape: {data.shape}")
print("First few rows:")
print(data.head())
print()

# Example 2: Comprehensive data validation
print("2. Comprehensive data validation:")
validation_rules = {
    'id': {
        'required': True,
        'unique': True,
        'numeric': {'min': 1}
    },
    'name': {
        'required': True,
        'length': {'min': 2, 'max': 50}
    },
    'email': {
        'required': True,
        'email': True
    },
    'age': {
        'required': True,
        'numeric': {'min': 18, 'max': 65}
    },
    'phone': {
        'required': True,
        'phone': True
    },
    'salary': {
        'required': True,
        'numeric': {'min': 0}
    },
    'department': {
        'required': True,
        'categorical': ['Engineering', 'Marketing', 'Sales', 'HR']
    },
    'hire_date': {
        'required': True,
        'date': {'format': '%Y-%m-%d'}
    },
    'status': {
        'required': True,
        'categorical': ['Active', 'Inactive', 'Terminated']
    }
}

# Validate the data
validation_errors = validate_dataframe(data.df, validation_rules)
validation_summary = get_validation_summary(validation_errors)

print("Validation Summary:")
print(f"  Total errors: {validation_summary['total_errors']}")
print(f"  Columns with errors: {validation_summary['columns_with_errors']}")
print(f"  Validation passed: {validation_summary['validation_passed']}")
print()

if validation_errors:
    print("Validation Errors:")
    for column, errors in validation_errors.items():
        print(f"  {column}:")
        for error in errors:
            print(f"    - {error}")
    print()

# Example 3: Data cleaning
print("3. Data cleaning:")
cleaning_rules = {
    'name': {
        'strip_whitespace': True,
        'title_case': True
    },
    'email': {
        'lowercase': True
    },
    'phone': {
        'regex_replace': {
            r'[^\d-]': ''  # Remove non-digit and non-dash characters
        }
    },
    'department': {
        'replace': {
            'InvalidDept': 'Other'
        }
    },
    'salary': {
        'custom': lambda x: max(0, x) if pd.notna(x) else x  # Ensure non-negative
    }
}

# Clean the data
cleaned_df = clean_dataframe(data.df, cleaning_rules)
cleaned_data = CSVData(cleaned_df)

print("Data after cleaning:")
print(cleaned_data[['name', 'email', 'phone', 'department', 'salary']].head())
print()

# Example 4: Advanced filtering with multiple conditions
print("4. Advanced filtering:")
# Filter for engineering employees with salary > 60000
engineering_high_salary = (cleaned_data
                          .where(cleaned_data['department'] == 'Engineering')
                          .where(cleaned_data['salary'] > 60000)
                          .sort_by('salary', ascending=False))

print(f"Engineering employees with salary > $60,000: {len(engineering_high_salary)}")
print(engineering_high_salary[['name', 'department', 'salary']].head())
print()

# Example 5: Data aggregation and analysis
print("5. Data aggregation and analysis:")
# Group by department and calculate statistics
dept_stats = cleaned_data.df.groupby('department').agg({
    'salary': ['mean', 'min', 'max', 'count'],
    'age': ['mean', 'min', 'max']
}).round(2)

print("Department statistics:")
print(dept_stats)
print()

# Example 6: Data transformation
print("6. Data transformation:")
# Add calculated columns
transformed_data = (cleaned_data
                   .add_column('salary_category', 
                              cleaned_data['salary'].apply(lambda x: 'High' if x > 70000 else 'Medium' if x > 50000 else 'Low'))
                   .add_column('years_employed', 
                              2024 - pd.to_datetime(cleaned_data['hire_date'], errors='coerce').dt.year.fillna(0))
                   .add_column('bonus', cleaned_data['salary'] * 0.1))

print("Data with calculated columns:")
print(transformed_data[['name', 'salary', 'salary_category', 'years_employed', 'bonus']].head())
print()

# Example 7: Error handling demonstration
print("7. Error handling demonstration:")
try:
    # Try to access a non-existent column
    result = data['non_existent_column']
except Exception as e:
    print(f"Error caught: {e}")
    print()

try:
    # Try to filter with invalid condition
    result = data.where(data['invalid_column'] > 10)
except Exception as e:
    print(f"Error caught: {e}")
    print()

# Example 8: Data export with multiple formats
print("8. Data export with multiple formats:")
# Export cleaned data to multiple formats
exported_files = transformed_data.export("cleaned_employee_data", 
                                        formats=['csv', 'json', 'excel'])
print("Exported files:")
for format_type, file_path in exported_files.items():
    print(f"  {format_type}: {file_path}")
print()

# Example 9: Data profiling and insights
print("9. Data profiling and insights:")
profile = transformed_data.profile()

print("Detailed column profiles:")
for col, stats in profile.items():
    print(f"\n{col}:")
    print(f"  Type: {stats['dtype']}")
    print(f"  Null count: {stats['null_count']} ({stats['null_percentage']:.1f}%)")
    print(f"  Unique values: {stats['unique_count']}")
    
    if 'min' in stats and 'max' in stats:
        print(f"  Range: {stats['min']} - {stats['max']}")
    if 'mean' in stats:
        print(f"  Mean: {stats['mean']:.2f}")
print()

# Example 10: Performance optimization
print("10. Performance optimization:")
# For large datasets, you can use chunking
print("Processing data in chunks (simulated):")

# Simulate processing large data in chunks
chunk_size = 3
total_rows = len(transformed_data)
processed_rows = 0

for i in range(0, total_rows, chunk_size):
    chunk = CSVData(transformed_data.df.iloc[i:i+chunk_size])
    processed_rows += len(chunk)
    print(f"  Processed chunk {i//chunk_size + 1}: {len(chunk)} rows (Total: {processed_rows}/{total_rows})")

print("\n=== Advanced Examples completed! ===") 