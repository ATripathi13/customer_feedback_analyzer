"""
Unit tests for CSVExporter component.
"""

import csv
import tempfile
import io
import contextlib
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback_analyzer import CSVExporter, FeedbackResult


def test_export_to_new_file():
    """Test successful export to a new CSV file."""
    # Create test results
    results = [
        FeedbackResult("Great product!", "Happy", 0.8),
        FeedbackResult("Not good at all", "Sad", -0.6),
        FeedbackResult("It's okay", "Mild", 0.05)
    ]
    
    # Create a temporary file path
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    # Delete the file so we can test creating a new one
    Path(temp_path).unlink()
    
    try:
        # Export results (suppress print output)
        with contextlib.redirect_stdout(io.StringIO()):
            success = CSVExporter.export(results, temp_path)
        
        # Verify export was successful
        assert success, "Export should succeed"
        
        # Verify file was created
        assert Path(temp_path).exists(), "CSV file should be created"
        
        # Verify file contents
        with open(temp_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 3, "Should have 3 rows"
        
        # Check first row
        assert rows[0]['feedback'] == "Great product!"
        assert rows[0]['category'] == "Happy"
        assert float(rows[0]['sentiment_score']) == 0.8
        
        # Check second row
        assert rows[1]['feedback'] == "Not good at all"
        assert rows[1]['category'] == "Sad"
        assert float(rows[1]['sentiment_score']) == -0.6
        
        # Check third row
        assert rows[2]['feedback'] == "It's okay"
        assert rows[2]['category'] == "Mild"
        assert float(rows[2]['sentiment_score']) == 0.05
    
    finally:
        # Clean up
        Path(temp_path).unlink(missing_ok=True)


def test_export_overwrites_existing_file():
    """Test that export overwrites an existing CSV file."""
    # Create initial results
    initial_results = [
        FeedbackResult("Old feedback", "Happy", 0.5)
    ]
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    try:
        # Export initial results
        with contextlib.redirect_stdout(io.StringIO()):
            CSVExporter.export(initial_results, temp_path)
        
        # Verify initial file exists
        assert Path(temp_path).exists()
        
        # Create new results
        new_results = [
            FeedbackResult("New feedback 1", "Sad", -0.3),
            FeedbackResult("New feedback 2", "Mild", 0.0)
        ]
        
        # Export new results (should overwrite)
        with contextlib.redirect_stdout(io.StringIO()):
            success = CSVExporter.export(new_results, temp_path)
        
        assert success, "Export should succeed"
        
        # Verify file was overwritten
        with open(temp_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Should only have the new results, not the old ones
        assert len(rows) == 2, "Should have 2 rows (old data overwritten)"
        assert rows[0]['feedback'] == "New feedback 1"
        assert rows[1]['feedback'] == "New feedback 2"
    
    finally:
        # Clean up
        Path(temp_path).unlink(missing_ok=True)


def test_export_creates_output_directories():
    """Test that export creates necessary output directories."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a path with nested directories that don't exist
        output_path = Path(temp_dir) / "output" / "results" / "feedback.csv"
        
        # Verify directories don't exist yet
        assert not output_path.parent.exists()
        
        # Create test results
        results = [
            FeedbackResult("Test feedback", "Happy", 0.7)
        ]
        
        # Export results
        with contextlib.redirect_stdout(io.StringIO()):
            success = CSVExporter.export(results, str(output_path))
        
        assert success, "Export should succeed"
        
        # Verify directories were created
        assert output_path.parent.exists(), "Output directories should be created"
        
        # Verify file was created
        assert output_path.exists(), "CSV file should be created"
        
        # Verify file contents
        with open(output_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 1
        assert rows[0]['feedback'] == "Test feedback"


def test_csv_format_correctness():
    """Test that the CSV file has correct format with proper headers and columns."""
    # Create test results
    results = [
        FeedbackResult("Feedback 1", "Happy", 0.9),
        FeedbackResult("Feedback 2", "Sad", -0.4)
    ]
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    try:
        # Export results
        with contextlib.redirect_stdout(io.StringIO()):
            CSVExporter.export(results, temp_path)
        
        # Read the raw CSV to check format
        with open(temp_path, 'r', encoding='utf-8', newline='') as f:
            lines = f.readlines()
        
        # Check header line
        assert lines[0].strip() == "feedback,category,sentiment_score", \
            "CSV should have correct header"
        
        # Check that we have the right number of lines (header + data rows)
        assert len(lines) == 3, "Should have header + 2 data rows"
        
        # Verify using DictReader
        with open(temp_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            
            # Check fieldnames
            assert reader.fieldnames == ['feedback', 'category', 'sentiment_score'], \
                "CSV should have correct column names"
            
            rows = list(reader)
            assert len(rows) == 2, "Should have 2 data rows"
    
    finally:
        # Clean up
        Path(temp_path).unlink(missing_ok=True)


def test_export_empty_results():
    """Test exporting an empty list of results."""
    # Create empty results list
    results = []
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        temp_path = f.name
    
    try:
        # Export empty results
        with contextlib.redirect_stdout(io.StringIO()):
            success = CSVExporter.export(results, temp_path)
        
        assert success, "Export should succeed even with empty results"
        
        # Verify file was created
        assert Path(temp_path).exists()
        
        # Verify file has header but no data rows
        with open(temp_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 0, "Should have no data rows"
    
    finally:
        # Clean up
        Path(temp_path).unlink(missing_ok=True)
