"""Unit tests for data I/O operations."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from llm_dataset_engine.adapters.data_io import (
    CSVReader,
    CSVWriter,
    DataFrameReader,
    create_data_reader,
    create_data_writer,
)
from llm_dataset_engine.core.specifications import DataSourceType


class TestDataReaders:
    """Test suite for data readers."""

    def test_dataframe_reader(self):
        """Test reading from DataFrame."""
        df = pd.DataFrame({
            "text": ["sample1", "sample2"],
            "value": [1, 2],
        })
        
        reader = DataFrameReader(df)
        result = reader.read()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ["text", "value"]

    def test_csv_reader(self):
        """Test reading from CSV file."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("text,value\n")
            f.write("sample1,1\n")
            f.write("sample2,2\n")
            csv_path = f.name
        
        try:
            reader = CSVReader(csv_path)
            result = reader.read()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
            assert "text" in result.columns
            assert "value" in result.columns
        finally:
            Path(csv_path).unlink()

    def test_csv_reader_chunked(self):
        """Test reading CSV in chunks."""
        # Create temporary CSV file with more rows
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("text\n")
            for i in range(100):
                f.write(f"sample{i}\n")
            csv_path = f.name
        
        try:
            reader = CSVReader(csv_path)
            chunks = list(reader.read_chunked(chunk_size=25))
            
            assert len(chunks) == 4  # 100 rows / 25 per chunk
            assert all(isinstance(chunk, pd.DataFrame) for chunk in chunks)
            assert len(chunks[0]) == 25
            assert len(chunks[-1]) == 25
        finally:
            Path(csv_path).unlink()

    def test_create_data_reader_csv(self):
        """Test factory function for CSV reader."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("text\nsample\n")
            csv_path = f.name
        
        try:
            reader = create_data_reader(DataSourceType.CSV, csv_path)
            assert isinstance(reader, CSVReader)
            
            result = reader.read()
            assert len(result) == 1
        finally:
            Path(csv_path).unlink()

    def test_create_data_reader_dataframe(self):
        """Test factory function for DataFrame reader."""
        df = pd.DataFrame({"text": ["test"]})
        reader = create_data_reader(DataSourceType.DATAFRAME, dataframe=df)
        
        assert isinstance(reader, DataFrameReader)


class TestDataWriters:
    """Test suite for data writers."""

    def test_csv_writer(self):
        """Test writing to CSV file."""
        df = pd.DataFrame({
            "text": ["sample1", "sample2"],
            "value": [1, 2],
        })
        
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            csv_path = f.name
        
        try:
            writer = CSVWriter(csv_path)
            confirmation = writer.write(df)
            
            assert confirmation.success is True
            assert confirmation.rows_written == 2
            assert Path(csv_path).exists()
            
            # Verify written data
            written_df = pd.read_csv(csv_path)
            assert len(written_df) == 2
            assert list(written_df.columns) == ["text", "value"]
        finally:
            Path(csv_path).unlink(missing_ok=True)

    def test_csv_writer_append_mode(self):
        """Test appending to CSV file."""
        df1 = pd.DataFrame({"text": ["first"]})
        df2 = pd.DataFrame({"text": ["second"]})
        
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            csv_path = f.name
        
        try:
            writer = CSVWriter(csv_path)
            writer.write(df1)
            writer.write(df2, mode="append")
            
            # Verify both rows written
            result = pd.read_csv(csv_path)
            assert len(result) == 2
            assert result.iloc[0]["text"] == "first"
            assert result.iloc[1]["text"] == "second"
        finally:
            Path(csv_path).unlink(missing_ok=True)

    def test_create_data_writer_csv(self):
        """Test factory function for CSV writer."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            csv_path = f.name
        
        try:
            writer = create_data_writer(DataSourceType.CSV, csv_path)
            assert isinstance(writer, CSVWriter)
            
            df = pd.DataFrame({"text": ["test"]})
            confirmation = writer.write(df)
            assert confirmation.success is True
        finally:
            Path(csv_path).unlink(missing_ok=True)


class TestCheckpointStorage:
    """Test suite for checkpoint storage."""

    def test_checkpoint_save_and_load(self):
        """Test saving and loading checkpoints."""
        from uuid import uuid4
        from llm_dataset_engine.adapters import LocalFileCheckpointStorage
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LocalFileCheckpointStorage(temp_dir)
            session_id = uuid4()
            
            # Save checkpoint
            data = {
                "rows_processed": 100,
                "stage": "LLMInvocation",
                "timestamp": "2025-10-15T10:00:00",
            }
            
            success = storage.save(session_id, data)
            assert success is True
            
            # Load checkpoint
            loaded_data = storage.load(session_id)
            assert loaded_data is not None
            assert loaded_data["rows_processed"] == 100
            assert loaded_data["stage"] == "LLMInvocation"

    def test_checkpoint_list(self):
        """Test listing checkpoints."""
        from uuid import uuid4
        from llm_dataset_engine.adapters import LocalFileCheckpointStorage
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LocalFileCheckpointStorage(temp_dir)
            
            # Create multiple checkpoints
            session_ids = [uuid4() for _ in range(3)]
            for sid in session_ids:
                storage.save(sid, {"test": "data"})
            
            # List checkpoints
            checkpoints = storage.list_checkpoints()
            assert len(checkpoints) >= 3

    def test_checkpoint_delete(self):
        """Test deleting checkpoints."""
        from uuid import uuid4
        from llm_dataset_engine.adapters import LocalFileCheckpointStorage
        
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = LocalFileCheckpointStorage(temp_dir)
            session_id = uuid4()
            
            # Save and then delete
            storage.save(session_id, {"test": "data"})
            success = storage.delete(session_id)
            assert success is True
            
            # Verify deleted
            loaded = storage.load(session_id)
            assert loaded is None

