"""
Basic usage examples for DataProcessing package.
"""

import pandas as pd
from dataprocessing import load, save, CSVData

print("=== DataProcessing Basic Usage Examples ===\n")

# Create sample data for demonstration
sample_data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'age': [25, 30, 35, 28, 32],
    'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'diana@example.com', 'eve@example.com'],
    'city': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
    'salary': [50000, 60000, 70000, 55000, 65000]
}

# Create a DataFrame and save it as CSV for demonstration
df = pd.DataFrame(sample_data)
df.to_csv('demo_data.csv', index=False)

# Example 1: Simple loading and saving
print("1. Simple loading and saving:")
data = load("demo_data.csv")
print(f"Loaded data shape: {data.shape}")
print(f"Columns: {data.columns}")
print()

# Example 2: Data exploration
print("2. Data exploration:")
print("First 3 rows:")
print(data.head(3))
print()

print("Data summary:")
summary = data.summary()
print(f"Shape: {summary['shape']}")
print(f"Memory usage: {summary['memory_usage']} bytes")
print(f"Numeric columns: {summary['numeric_columns']}")
print()

# Example 3: Filtering and sorting
print("3. Filtering and sorting:")
young_people = data.where(data['age'] < 30)
print(f"Young people (age < 30): {len(young_people)} rows")

sorted_by_age = data.sort_by("age", ascending=False)
print("Top 3 oldest people:")
print(sorted_by_age.head(3)[['name', 'age']])
print()

# Example 4: Column operations
print("4. Column operations:")
# Select specific columns
selected = data.select_columns(['name', 'age', 'email'])
print(f"Selected columns: {selected.columns}")

# Add a new column
with_bonus = data.add_column('bonus', data['salary'] * 0.1)
print("Added bonus column (10% of salary)")
print(with_bonus[['name', 'salary', 'bonus']].head(3))
print()

# Example 5: Data cleaning
print("5. Data cleaning:")
# Add some missing values for demonstration
data_with_missing = CSVData(data.df.copy())
data_with_missing.df.loc[1, 'email'] = None
data_with_missing.df.loc[3, 'age'] = None

# Fill missing values
cleaned = data_with_missing.fill_missing('email', 'unknown@example.com')
cleaned = cleaned.fill_missing('age', 0)
print("Filled missing values:")
print(cleaned[['name', 'age', 'email']].head())
print()

# Example 6: Chaining operations
print("6. Chaining operations:")
result = (load("demo_data.csv")
          .where(data['age'] > 25)
          .sort_by("salary", ascending=False)
          .select_columns(['name', 'age', 'salary'])
          .head(3))

print("Top 3 highest earners over 25:")
print(result)
print()

# Example 7: Data validation
print("7. Data validation:")
validation_rules = {
    'age': {'numeric': {'min': 0, 'max': 120}},
    'email': {'email': True},
    'salary': {'numeric': {'min': 0}}
}

try:
    validated = data.validate_types(validation_rules)
    print("✅ Data validation passed")
except Exception as e:
    print(f"❌ Data validation failed: {e}")
print()

# Example 8: Saving data
print("8. Saving data:")
# Save filtered data
young_people.save("young_people.csv")
print("Saved young people data to 'young_people.csv'")

# Save in multiple formats
data.export("employee_data", formats=['csv', 'json', 'xlsx'])
print("Exported data in multiple formats")
print()

# Clean up demo file
import os
if os.path.exists('demo_data.csv'):
    os.remove('demo_data.csv')
if os.path.exists('young_people.csv'):
    os.remove('young_people.csv')
if os.path.exists('employee_data.csv'):
    os.remove('employee_data.csv')
if os.path.exists('employee_data.json'):
    os.remove('employee_data.json')
if os.path.exists('employee_data.xlsx'):
    os.remove('employee_data.xlsx')

print("=== Basic Usage Examples Complete ===")
print("\n💡 Key takeaways:")
print("- Use .head() to preview data")
print("- Chain operations for complex transformations")
print("- Built-in validation and cleaning tools")
print("- Export to multiple formats easily") 