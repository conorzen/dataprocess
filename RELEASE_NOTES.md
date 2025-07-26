# DataProcessing Package - Release Notes

## Version 0.1.0

### 🎉 Initial Release

DataProcessing is a user-friendly Python package for working with CSV data, featuring smart defaults, intuitive APIs, and powerful data manipulation capabilities.

### ✨ Key Features

#### Core Functionality
- **Smart CSV Loading**: Auto-detect encoding, delimiters, and handle malformed files
- **Intuitive API**: Chainable methods for filtering, sorting, and data manipulation
- **Data Exploration**: Quick summaries, profiling, and preview tools
- **Error Handling**: Clear, helpful error messages instead of cryptic pandas errors

#### Advanced Features
- **SQL Support**: Write SQL queries directly on CSV data using SQLite backend
- **Live Data**: Connect to databases, APIs, and real-time data streams
- **Data Validation**: Built-in validation for data types, formats, and business rules
- **Data Cleaning**: Handle missing values, duplicates, and data transformations

#### Simplified Live Data API
- **One-liner imports**: `data = import_live("@https://example.com/data.csv")`
- **Live streaming**: `live_data = create_live_stream(data, interval=60)`
- **SQL on live data**: `results = live_data.sql("SELECT * FROM data LIMIT 10")`

### 🚀 Quick Start

```python
from dataprocessing import load, import_live, create_live_stream

# Load CSV data
data = load("data.csv")

# Filter and manipulate
filtered = data.where(data['age'] > 25).sort_by("name")

# Use SQL
result = data.sql("SELECT * FROM data WHERE age > 25")

# Live data
data = import_live("@https://example.com/live-data.csv")
live_data = create_live_stream(data, interval=60)
results = live_data.sql("SELECT * FROM data LIMIT 10")
```

### 📦 Installation

```bash
pip install dataprocessing
```

### 🔧 Dependencies

- **Core**: pandas, chardet, python-dateutil, numpy
- **File Support**: openpyxl, pyarrow
- **Live Data**: requests, psycopg2-binary, mysql-connector-python

### 📁 Project Structure

```
dataprocessing/
├── dataprocessing/          # Main package
│   ├── __init__.py         # Public API
│   ├── core.py             # CSVData class
│   ├── exceptions.py       # Custom exceptions
│   ├── utils.py            # Utility functions
│   ├── readers.py          # File reading
│   ├── writers.py          # File writing
│   ├── validators.py       # Data validation
│   ├── sql.py              # SQL functionality
│   ├── live_data.py        # Live data connections
│   ├── simple_live.py      # Simple live data API
│   └── simple_import.py    # Import functions
├── examples/               # Usage examples
├── tests/                  # Unit tests
├── setup.py               # Package configuration
├── requirements.txt       # Dependencies
├── README.md             # Documentation
├── LICENSE               # MIT License
└── .gitignore           # Git ignores
```

### 🎯 Use Cases

- **Data Analysis**: Quick CSV exploration and manipulation
- **ETL Pipelines**: Data transformation and cleaning
- **Live Data Monitoring**: Real-time data streams and APIs
- **Database Integration**: Connect to various database systems
- **Data Validation**: Ensure data quality and consistency

### 🔮 Future Enhancements

- **Polars Backend**: Optional fast backend for large datasets
- **More Database Connectors**: Support for additional databases
- **Advanced Analytics**: Built-in statistical functions
- **Data Visualization**: Integration with plotting libraries
- **Cloud Storage**: Support for S3, GCS, Azure Blob

### 📄 License

MIT License - see LICENSE file for details.

### 🤝 Contributing

Contributions are welcome! Please feel free to submit Pull Requests.

---

**DataProcessing** - Making CSV data processing simple and powerful! 🚀 