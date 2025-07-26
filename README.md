# DataProcessing

A user-friendly Python package for working with CSV data. DataProcessing makes common CSV operations simple and intuitive, with smart defaults and helpful error messages.

## Features

- **Smart Loading**: Auto-detect encoding, delimiters, and handle malformed files
- **Intuitive API**: Chainable methods for filtering, sorting, and data manipulation
- **SQL Support**: Write SQL queries directly on CSV data
- **Live Data**: Connect to databases, APIs, and real-time data streams
- **Helpful Errors**: Clear error messages instead of cryptic pandas errors
- **Smart Defaults**: Works out of the box with minimal configuration
- **Data Exploration**: Quick summaries and data profiling

## Quick Start

```python
from dataprocessing import load, save, import_live, create_live_stream

# Load CSV with smart defaults
data = load("data.csv")

# Filter and manipulate
filtered = data.where(data['age'] > 25).sort_by("name")

# Or use SQL
filtered = data.sql("SELECT * FROM data WHERE age > 25 ORDER BY name")

# Load from database
from dataprocessing import load_from_db
db_data = load_from_db('postgresql', 'postgresql://user:pass@localhost/db', 'SELECT * FROM users')

# Load from API
from dataprocessing import load_from_api
api_data = load_from_api('https://api.example.com', '/data')

# Simple live data import
data = import_live("@https://example.com/live-data.csv")
live_data = create_live_stream(data, interval=60)
results = live_data.sql("SELECT * FROM data LIMIT 10")

# Save with automatic formatting
filtered.save("output.csv")
```

## Installation

```bash
pip install dataprocessing
```

For faster performance with large datasets:
```bash
pip install dataprocessing[fast]
```

## Basic Usage

### Loading Data

```python
from dataprocessing import load

# Simple loading with auto-detection
data = load("data.csv")

# With custom options
data = load("data.csv", encoding="utf-8", delimiter=";")
```

### Data Manipulation

```python
# Filtering
young_users = data.where(data['age'] < 30)
active_users = data.where(data['status'] == "active")

# Sorting
sorted_data = data.sort_by("name")
sorted_data = data.sort_by("age", ascending=False)

# Column operations
data = data.rename_column("old_name", "new_name")
data = data.select_columns(["name", "age", "email"])
data = data.drop_columns(["unused_column"])

# Adding columns
data = data.add_column("full_name", data["first_name"] + " " + data["last_name"])
```

### Data Exploration

```python
# Quick summary
print(data.summary())

# Data profiling
print(data.profile())

# Preview data
print(data.head())
print(data.tail())
print(data.sample(5))
```

### SQL Support

```python
# Basic queries
result = data.sql("SELECT * FROM data WHERE age > 25")

# Aggregations
summary = data.sql("SELECT COUNT(*) as count, AVG(age) as avg_age FROM data")

# Group by
grouped = data.sql("SELECT city, COUNT(*) as count FROM data GROUP BY city")

# Complex queries
complex_result = data.sql("""
    SELECT 
        city,
        COUNT(*) as total_users,
        AVG(age) as avg_age,
        MAX(salary) as max_salary
    FROM data 
    WHERE age > 25 
    GROUP BY city 
    HAVING COUNT(*) > 1
    ORDER BY avg_age DESC
""")
```

### Live Data Connections

```python
from dataprocessing import load_from_db, load_from_api, create_live_stream

# Database connections
data = load_from_db('postgresql', 'postgresql://user:pass@localhost/db', 'SELECT * FROM users')

# API connections
data = load_from_api('https://api.example.com', '/users', headers={'Authorization': 'Bearer token'})

# Real-time data streams
def get_sensor_data():
    return {'temperature': 25.5, 'humidity': 60}

stream = create_live_stream(get_sensor_data, interval=1.0)
stream.start()
data = CSVData(stream.get_latest_data())
```

### Simple Live Data Import

```python
from dataprocessing import import_live, create_live_stream

# Super simple syntax
data = import_live("@https://example.com/live-data.csv")
live_data = create_live_stream(data, interval=60)

print(live_data.header)
results = live_data.sql("SELECT * FROM data LIMIT 10")
print(results)
```

### Chaining Operations

```python
result = (load("data.csv")
          .where(data['age'] > 18)
          .where(data['status'] == "active")
          .sort_by("name")
          .select_columns(["name", "email", "age"])
          .save("filtered_data.csv"))
```

### Data Validation

```python
# Validate data types
data = data.validate_types({
    "age": "int",
    "email": "email",
    "date": "date"
})

# Check for missing values
missing_report = data.check_missing()
```

### Data Cleaning

```python
# Handle missing values
data = data.fill_missing("age", 0)
data = data.drop_missing(["email"])

# Remove duplicates
data = data.drop_duplicates()
```

## Error Handling

DataProcessing provides helpful error messages:

```python
# Instead of: KeyError: 'age'
# You get: Column 'age' not found. Did you mean 'Age'?

# Instead of: UnicodeDecodeError
# You get: Unable to read file encoding. Try specifying encoding='utf-8'
```

## Performance

For large datasets, use the fast backend:

```python
from dataprocessing import load

# Uses Polars for faster performance
data = load("large_file.csv", backend="polars")
```

## Examples

Check out the `examples/` directory for comprehensive usage examples:

- `basic_usage.py` - Basic CSV operations
- `advanced_usage.py` - Advanced data manipulation
- `sql_usage.py` - SQL query examples
- `live_data_usage.py` - Database and API connections
- `simple_live_usage.py` - Simple live data import

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 