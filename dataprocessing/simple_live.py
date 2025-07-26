"""
Simple live data processing API for DataProcessing package.
Provides intuitive functions for importing and streaming live data.
"""

import pandas as pd
import requests
from typing import Union, Optional, Callable
from pathlib import Path
import time
import threading
from datetime import datetime
from .core import CSVData
from .live_data import RealTimeDataStream
from .exceptions import DataProcessingError


class SimpleLiveData:
    """
    Simple wrapper for live data with SQL capabilities.
    """
    
    def __init__(self, data_source: Union[str, Callable], interval: int = 3600):
        """
        Initialize simple live data.
        
        Args:
            data_source: URL string or function that returns data
            interval: Refresh interval in seconds
        """
        self.data_source = data_source
        self.interval = interval
        self.current_data = None
        self.stream = None
        self._setup_stream()
    
    def _setup_stream(self):
        """Set up the data stream."""
        if isinstance(self.data_source, str):
            # URL source
            def fetch_from_url():
                try:
                    df = pd.read_csv(self.data_source)
                    return df.to_dict('records')
                except Exception as e:
                    print(f"Error fetching from URL: {e}")
                    return None
            
            self.stream = RealTimeDataStream(fetch_from_url, interval=self.interval)
            
            # Load initial data
            try:
                df = pd.read_csv(self.data_source)
                self.current_data = CSVData(df)
            except Exception as e:
                print(f"Error loading initial data: {e}")
        else:
            # Function source
            self.stream = RealTimeDataStream(self.data_source, interval=self.interval)
    
    def start(self):
        """Start the live data stream."""
        if self.stream:
            self.stream.start()
    
    def stop(self):
        """Stop the live data stream."""
        if self.stream:
            self.stream.stop()
    
    def refresh(self):
        """Manually refresh the data."""
        if self.stream:
            latest = self.stream.get_latest_data()
            if len(latest) > 0:
                self.current_data = CSVData(latest)
                return self.current_data
        return None
    
    def get_data(self) -> CSVData:
        """Get the current data."""
        if self.current_data is None:
            self.refresh()
        if self.current_data is None:
            # Try to load data directly
            try:
                if isinstance(self.data_source, str):
                    df = pd.read_csv(self.data_source)
                    self.current_data = CSVData(df)
            except Exception as e:
                print(f"Error loading data: {e}")
                return CSVData(pd.DataFrame())
        return self.current_data
    
    def sql(self, query: str) -> CSVData:
        """
        Execute SQL query on the current data.
        
        Args:
            query: SQL query string
            
        Returns:
            CSVData with query results
        """
        data = self.get_data()
        if data is not None:
            return data.sql(query)
        else:
            raise DataProcessingError("No data available for SQL query")
    
    @property
    def header(self):
        """Get column headers."""
        data = self.get_data()
        if data is not None:
            return list(data.columns)
        return []
    
    @property
    def shape(self):
        """Get data shape."""
        data = self.get_data()
        if data is not None:
            return data.shape
        return (0, 0)
    
    def head(self, n: int = 5):
        """Get first n rows."""
        data = self.get_data()
        if data is not None:
            return data.head(n)
        return None
    
    def tail(self, n: int = 5):
        """Get last n rows."""
        data = self.get_data()
        if data is not None:
            return data.tail(n)
        return None
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def import_data(source: Union[str, Callable]) -> SimpleLiveData:
    """
    Import data from URL or function.
    
    Args:
        source: URL string or function that returns data
        
    Returns:
        SimpleLiveData object
    """
    return SimpleLiveData(source)


def create_live_stream(source: Union[str, Callable], interval: int = 3600) -> SimpleLiveData:
    """
    Create a live data stream.
    
    Args:
        source: URL string or function that returns data
        interval: Refresh interval in seconds
        
    Returns:
        SimpleLiveData object with streaming capabilities
    """
    live_data = SimpleLiveData(source, interval)
    live_data.start()
    return live_data


# Convenience function for direct URL loading
def load_url(url: str) -> CSVData:
    """
    Load data directly from URL.
    
    Args:
        url: URL to load data from
        
    Returns:
        CSVData object
    """
    try:
        df = pd.read_csv(url)
        return CSVData(df)
    except Exception as e:
        raise DataProcessingError(f"Failed to load data from URL: {e}")


# Enhanced CSVData class with live capabilities
class LiveCSVData(CSVData):
    """CSVData with live streaming capabilities."""
    
    def __init__(self, source: Union[str, Callable], interval: int = 3600):
        """
        Initialize live CSV data.
        
        Args:
            source: URL string or function that returns data
            interval: Refresh interval in seconds
        """
        # Load initial data
        if isinstance(source, str):
            df = pd.read_csv(source)
        else:
            data = source()
            if isinstance(data, pd.DataFrame):
                df = data
            else:
                df = pd.DataFrame(data)
        
        super().__init__(df)
        
        # Set up streaming
        self.source = source
        self.interval = interval
        self.stream = None
        self._setup_stream()
    
    def _setup_stream(self):
        """Set up the data stream."""
        if isinstance(self.source, str):
            def fetch_from_url():
                try:
                    df = pd.read_csv(self.source)
                    return df.to_dict('records')
                except Exception as e:
                    print(f"Error fetching from URL: {e}")
                    return None
        else:
            fetch_from_url = self.source
        
        self.stream = RealTimeDataStream(fetch_from_url, interval=self.interval)
    
    def start_streaming(self):
        """Start the live data stream."""
        if self.stream:
            self.stream.start()
    
    def stop_streaming(self):
        """Stop the live data stream."""
        if self.stream:
            self.stream.stop()
    
    def refresh(self):
        """Refresh the data."""
        if self.stream:
            latest = self.stream.get_latest_data()
            if len(latest) > 0:
                self._df = pd.DataFrame(latest)
    
    def get_latest(self) -> CSVData:
        """Get the latest data as CSVData."""
        self.refresh()
        return CSVData(self._df.copy())


# Simple import function
def import_live(url: str, interval: int = 3600) -> LiveCSVData:
    """
    Import live data from URL.
    
    Args:
        url: URL to import from
        interval: Refresh interval in seconds
        
    Returns:
        LiveCSVData object
    """
    return LiveCSVData(url, interval) 