"""
Live data functionality for DataProcessing package.
Supports databases, APIs, and real-time data sources.
"""

import pandas as pd
import requests
import json
import sqlite3
import psycopg2
import mysql.connector
from typing import Union, Dict, List, Any, Optional, Callable
from pathlib import Path
import time
import threading
from datetime import datetime, timedelta
from .exceptions import DataProcessingError


class DatabaseConnector:
    """Base class for database connections."""
    
    def __init__(self, connection_string: str, **kwargs):
        """
        Initialize database connector.
        
        Args:
            connection_string: Database connection string
            **kwargs: Additional connection parameters
        """
        self.connection_string = connection_string
        self.connection = None
        self.kwargs = kwargs
    
    def connect(self):
        """Establish database connection."""
        raise NotImplementedError("Subclasses must implement connect()")
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame."""
        raise NotImplementedError("Subclasses must implement query()")
    
    def execute(self, sql: str) -> None:
        """Execute SQL statement."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class SQLiteConnector(DatabaseConnector):
    """SQLite database connector."""
    
    def connect(self):
        """Connect to SQLite database."""
        self.connection = sqlite3.connect(self.connection_string)
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame."""
        return pd.read_sql_query(sql, self.connection)
    
    def execute(self, sql: str) -> None:
        """Execute SQL statement."""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()


class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL database connector."""
    
    def connect(self):
        """Connect to PostgreSQL database."""
        # Parse connection string or use kwargs
        if self.connection_string.startswith('postgresql://'):
            # Parse URL-style connection string
            import urllib.parse
            parsed = urllib.parse.urlparse(self.connection_string)
            self.connection = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                **self.kwargs
            )
        else:
            # Use connection string directly
            self.connection = psycopg2.connect(self.connection_string, **self.kwargs)
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame."""
        return pd.read_sql_query(sql, self.connection)
    
    def execute(self, sql: str) -> None:
        """Execute SQL statement."""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()


class MySQLConnector(DatabaseConnector):
    """MySQL database connector."""
    
    def connect(self):
        """Connect to MySQL database."""
        # Parse connection string or use kwargs
        if self.connection_string.startswith('mysql://'):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.connection_string)
            self.connection = mysql.connector.connect(
                host=parsed.hostname,
                port=parsed.port or 3306,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                **self.kwargs
            )
        else:
            # Use connection string directly
            self.connection = mysql.connector.connect(self.connection_string, **self.kwargs)
    
    def query(self, sql: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame."""
        return pd.read_sql_query(sql, self.connection)
    
    def execute(self, sql: str) -> None:
        """Execute SQL statement."""
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()


class APIConnector:
    """API data connector."""
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None, 
                 auth: Optional[tuple] = None, timeout: int = 30):
        """
        Initialize API connector.
        
        Args:
            base_url: Base URL for the API
            headers: Request headers
            auth: Authentication tuple (username, password) or token
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.auth = auth
        self.timeout = timeout
        self.session = requests.Session()
        
        if auth:
            if isinstance(auth, tuple) and len(auth) == 2:
                self.session.auth = auth
            else:
                self.headers['Authorization'] = f'Bearer {auth}'
        
        self.session.headers.update(self.headers)
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """
        Make GET request and return DataFrame.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            DataFrame with response data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        return self._json_to_dataframe(data)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, 
             json_data: Optional[Dict] = None) -> pd.DataFrame:
        """
        Make POST request and return DataFrame.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data
            
        Returns:
            DataFrame with response data
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.post(url, data=data, json=json_data, timeout=self.timeout)
        response.raise_for_status()
        
        data = response.json()
        return self._json_to_dataframe(data)
    
    def _json_to_dataframe(self, data: Any) -> pd.DataFrame:
        """Convert JSON response to DataFrame."""
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            if 'data' in data:
                return pd.DataFrame(data['data'])
            elif 'results' in data:
                return pd.DataFrame(data['results'])
            else:
                return pd.DataFrame([data])
        else:
            return pd.DataFrame(data)


class RealTimeDataStream:
    """Real-time data stream connector."""
    
    def __init__(self, data_source: Callable, interval: float = 1.0, 
                 max_records: Optional[int] = None):
        """
        Initialize real-time data stream.
        
        Args:
            data_source: Function that returns data
            interval: Time interval between data collection (seconds)
            max_records: Maximum number of records to collect
        """
        self.data_source = data_source
        self.interval = interval
        self.max_records = max_records
        self.data_buffer = []
        self.is_running = False
        self.thread = None
        self.lock = threading.Lock()
    
    def start(self):
        """Start data collection."""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._collect_data)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self):
        """Stop data collection."""
        self.is_running = False
        if self.thread:
            self.thread.join()
    
    def _collect_data(self):
        """Collect data in background thread."""
        while self.is_running:
            try:
                data = self.data_source()
                if data is not None:
                    with self.lock:
                        self.data_buffer.append({
                            'timestamp': datetime.now(),
                            'data': data
                        })
                        
                        # Limit buffer size
                        if self.max_records and len(self.data_buffer) > self.max_records:
                            self.data_buffer = self.data_buffer[-self.max_records:]
                
                time.sleep(self.interval)
            except Exception as e:
                print(f"Error collecting data: {e}")
                time.sleep(self.interval)
    
    def get_latest_data(self) -> pd.DataFrame:
        """Get latest collected data as DataFrame."""
        with self.lock:
            if not self.data_buffer:
                return pd.DataFrame()
            
            # Convert buffer to DataFrame
            records = []
            for item in self.data_buffer:
                if isinstance(item['data'], dict):
                    record = item['data'].copy()
                    record['timestamp'] = item['timestamp']
                    records.append(record)
                else:
                    records.append({
                        'timestamp': item['timestamp'],
                        'value': item['data']
                    })
            
            return pd.DataFrame(records)
    
    def clear_buffer(self):
        """Clear data buffer."""
        with self.lock:
            self.data_buffer.clear()


class LiveDataManager:
    """Manager for live data connections."""
    
    def __init__(self):
        """Initialize live data manager."""
        self.connections = {}
        self.streams = {}
    
    def connect_database(self, name: str, db_type: str, connection_string: str, **kwargs) -> DatabaseConnector:
        """
        Connect to a database.
        
        Args:
            name: Connection name
            db_type: Database type ('sqlite', 'postgresql', 'mysql')
            connection_string: Database connection string
            **kwargs: Additional connection parameters
            
        Returns:
            Database connector
        """
        db_type = db_type.lower()
        
        if db_type == 'sqlite':
            connector = SQLiteConnector(connection_string, **kwargs)
        elif db_type == 'postgresql':
            connector = PostgreSQLConnector(connection_string, **kwargs)
        elif db_type == 'mysql':
            connector = MySQLConnector(connection_string, **kwargs)
        else:
            raise DataProcessingError(f"Unsupported database type: {db_type}")
        
        self.connections[name] = connector
        return connector
    
    def connect_api(self, name: str, base_url: str, **kwargs) -> APIConnector:
        """
        Connect to an API.
        
        Args:
            name: Connection name
            base_url: API base URL
            **kwargs: Additional API parameters
            
        Returns:
            API connector
        """
        connector = APIConnector(base_url, **kwargs)
        self.connections[name] = connector
        return connector
    
    def create_stream(self, name: str, data_source: Callable, **kwargs) -> RealTimeDataStream:
        """
        Create a real-time data stream.
        
        Args:
            name: Stream name
            data_source: Function that returns data
            **kwargs: Additional stream parameters
            
        Returns:
            Real-time data stream
        """
        stream = RealTimeDataStream(data_source, **kwargs)
        self.streams[name] = stream
        return stream
    
    def get_connection(self, name: str):
        """Get a connection by name."""
        return self.connections.get(name)
    
    def get_stream(self, name: str) -> RealTimeDataStream:
        """Get a stream by name."""
        return self.streams.get(name)
    
    def close_all(self):
        """Close all connections and streams."""
        for connector in self.connections.values():
            if hasattr(connector, 'disconnect'):
                connector.disconnect()
        
        for stream in self.streams.values():
            stream.stop()
        
        self.connections.clear()
        self.streams.clear()


# Convenience functions
def connect_database(db_type: str, connection_string: str, **kwargs) -> DatabaseConnector:
    """Quick database connection."""
    manager = LiveDataManager()
    return manager.connect_database('default', db_type, connection_string, **kwargs)


def connect_api(base_url: str, **kwargs) -> APIConnector:
    """Quick API connection."""
    manager = LiveDataManager()
    return manager.connect_api('default', base_url, **kwargs)


def create_stream(data_source: Callable, **kwargs) -> RealTimeDataStream:
    """Quick stream creation."""
    manager = LiveDataManager()
    return manager.create_stream('default', data_source, **kwargs)


def load_from_database(db_type: str, connection_string: str, query: str, **kwargs) -> pd.DataFrame:
    """
    Load data from database using a query.
    
    Args:
        db_type: Database type
        connection_string: Database connection string
        query: SQL query
        **kwargs: Additional connection parameters
        
    Returns:
        DataFrame with query results
    """
    with connect_database(db_type, connection_string, **kwargs) as db:
        return db.query(query)


def load_from_api(base_url: str, endpoint: str, **kwargs) -> pd.DataFrame:
    """
    Load data from API.
    
    Args:
        base_url: API base URL
        endpoint: API endpoint
        **kwargs: Additional API parameters
        
    Returns:
        DataFrame with API response
    """
    api = connect_api(base_url, **kwargs)
    return api.get(endpoint) 