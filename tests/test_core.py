"""
Unit tests for CSV Buddy core functionality.
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from dataprocessing import CSVData, load, save
from dataprocessing.exceptions import ColumnNotFoundError, FileReadError


class TestCSVData:
    """Test cases for CSVData class."""
    
    def setup_method(self):
        """Set up test data."""
        self.sample_data = {
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'city': ['New York', 'Los Angeles', 'Chicago']
        }
        self.df = pd.DataFrame(self.sample_data)
        self.csv_data = CSVData(self.df)
    
    def test_init_with_dataframe(self):
        """Test initialization with DataFrame."""
        assert len(self.csv_data) == 3
        assert self.csv_data.columns == ['name', 'age', 'city']
        assert self.csv_data.shape == (3, 3)
    
    def test_init_with_file_path(self):
        """Test initialization with file path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.df.to_csv(f.name, index=False)
            file_path = f.name
        
        try:
            csv_data = CSVData(file_path)
            assert len(csv_data) == 3
            assert csv_data.columns == ['name', 'age', 'city']
        finally:
            os.unlink(file_path)
    
    def test_getitem_column(self):
        """Test getting a column."""
        age_series = self.csv_data['age']
        assert list(age_series) == [25, 30, 35]
    
    def test_getitem_nonexistent_column(self):
        """Test getting a non-existent column raises error."""
        with pytest.raises(ColumnNotFoundError):
            _ = self.csv_data['nonexistent']
    
    def test_where_filtering(self):
        """Test where filtering."""
        filtered = self.csv_data.where(self.csv_data['age'] > 25)
        assert len(filtered) == 2
        assert list(filtered['name']) == ['Bob', 'Charlie']
    
    def test_sort_by(self):
        """Test sorting."""
        sorted_data = self.csv_data.sort_by('age', ascending=False)
        assert list(sorted_data['name']) == ['Charlie', 'Bob', 'Alice']
    
    def test_select_columns(self):
        """Test column selection."""
        selected = self.csv_data.select_columns(['name', 'age'])
        assert selected.columns == ['name', 'age']
        assert len(selected) == 3
    
    def test_drop_columns(self):
        """Test column dropping."""
        dropped = self.csv_data.drop_columns(['city'])
        assert dropped.columns == ['name', 'age']
        assert len(dropped) == 3
    
    def test_rename_column(self):
        """Test column renaming."""
        renamed = self.csv_data.rename_column('age', 'years')
        assert 'years' in renamed.columns
        assert 'age' not in renamed.columns
    
    def test_add_column(self):
        """Test adding a column."""
        added = self.csv_data.add_column('salary', [50000, 60000, 70000])
        assert 'salary' in added.columns
        assert list(added['salary']) == [50000, 60000, 70000]
    
    def test_fill_missing(self):
        """Test filling missing values."""
        # Create data with missing values
        df_with_missing = self.df.copy()
        df_with_missing.loc[1, 'age'] = None
        csv_with_missing = CSVData(df_with_missing)
        
        filled = csv_with_missing.fill_missing('age', 0)
        assert filled['age'].isna().sum() == 0
    
    def test_drop_missing(self):
        """Test dropping missing values."""
        # Create data with missing values
        df_with_missing = self.df.copy()
        df_with_missing.loc[1, 'age'] = None
        csv_with_missing = CSVData(df_with_missing)
        
        dropped = csv_with_missing.drop_missing(['age'])
        assert len(dropped) == 2
    
    def test_drop_duplicates(self):
        """Test dropping duplicates."""
        # Create data with duplicates
        df_with_duplicates = pd.concat([self.df, self.df.iloc[0:1]])
        csv_with_duplicates = CSVData(df_with_duplicates)
        
        deduplicated = csv_with_duplicates.drop_duplicates()
        assert len(deduplicated) == 3
    
    def test_summary(self):
        """Test summary method."""
        summary = self.csv_data.summary()
        assert summary['shape'] == (3, 3)
        assert summary['columns'] == 3
        assert 'memory_usage' in summary
    
    def test_profile(self):
        """Test profile method."""
        profile = self.csv_data.profile()
        assert 'name' in profile
        assert 'age' in profile
        assert 'city' in profile
        assert profile['age']['dtype'] == 'int64'
    
    def test_check_missing(self):
        """Test missing value check."""
        missing_info = self.csv_data.check_missing()
        assert missing_info['total_rows'] == 3
        assert missing_info['total_missing'] == 0
    
    def test_save(self):
        """Test saving to file."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            file_path = f.name
        
        try:
            self.csv_data.save(file_path)
            assert os.path.exists(file_path)
            
            # Verify the saved file
            saved_data = pd.read_csv(file_path)
            assert len(saved_data) == 3
            assert list(saved_data.columns) == ['name', 'age', 'city']
        finally:
            os.unlink(file_path)
    
    def test_to_pandas(self):
        """Test conversion to pandas DataFrame."""
        df_result = self.csv_data.to_pandas()
        assert isinstance(df_result, pd.DataFrame)
        assert len(df_result) == 3
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        dict_result = self.csv_data.to_dict()
        assert isinstance(dict_result, list)
        assert len(dict_result) == 3
        assert 'name' in dict_result[0]
    
    def test_to_list(self):
        """Test conversion to list of lists."""
        list_result = self.csv_data.to_list()
        assert isinstance(list_result, list)
        assert len(list_result) == 3
        assert len(list_result[0]) == 3


class TestLoadSave:
    """Test cases for load and save functions."""
    
    def setup_method(self):
        """Set up test data."""
        self.sample_data = {
            'name': ['Alice', 'Bob'],
            'age': [25, 30]
        }
        self.df = pd.DataFrame(self.sample_data)
    
    def test_load_function(self):
        """Test load function."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.df.to_csv(f.name, index=False)
            file_path = f.name
        
        try:
            data = load(file_path)
            assert isinstance(data, CSVData)
            assert len(data) == 2
        finally:
            os.unlink(file_path)
    
    def test_save_function(self):
        """Test save function."""
        csv_data = CSVData(self.df)
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            file_path = f.name
        
        try:
            save(csv_data, file_path)
            assert os.path.exists(file_path)
        finally:
            os.unlink(file_path)
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises error."""
        with pytest.raises(FileReadError):
            load("nonexistent_file.csv")


class TestChaining:
    """Test cases for method chaining."""
    
    def setup_method(self):
        """Set up test data."""
        self.sample_data = {
            'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'age': [25, 30, 35, 28],
            'salary': [50000, 60000, 70000, 55000]
        }
        self.df = pd.DataFrame(self.sample_data)
        self.csv_data = CSVData(self.df)
    
    def test_chaining_operations(self):
        """Test chaining multiple operations."""
        result = (self.csv_data
                 .where(self.csv_data['age'] > 25)
                 .sort_by('salary', ascending=False)
                 .select_columns(['name', 'salary']))
        
        assert len(result) == 3
        assert result.columns == ['name', 'salary']
        assert list(result['name']) == ['Charlie', 'Bob', 'Diana']
    
    def test_complex_chaining(self):
        """Test complex chaining with multiple operations."""
        result = (self.csv_data
                 .where(self.csv_data['age'] > 25)
                 .add_column('bonus', self.csv_data['salary'] * 0.1)
                 .sort_by('bonus', ascending=False)
                 .select_columns(['name', 'salary', 'bonus']))
        
        assert len(result) == 3
        assert 'bonus' in result.columns
        assert list(result['name']) == ['Charlie', 'Bob', 'Diana']


if __name__ == '__main__':
    pytest.main([__file__]) 