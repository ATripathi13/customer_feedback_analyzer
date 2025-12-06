"""
Unit tests for FeedbackLoader component.
"""

import tempfile
import csv
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback_analyzer import FeedbackLoader


def test_load_from_valid_text_file():
    """Test loading from a valid text file with multiple entries."""
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        f.write("Great product!\n")
        f.write("Terrible experience\n")
        f.write("It's okay\n")
        temp_path = f.name
    
    try:
        # Load feedback
        feedback = FeedbackLoader.load_from_file(temp_path)
        
        # Verify results
        assert len(feedback) == 3
        assert feedback[0] == "Great product!"
        assert feedback[1] == "Terrible experience"
        assert feedback[2] == "It's okay"
    finally:
        Path(temp_path).unlink()


def test_load_from_valid_csv_file():
    """Test loading from a valid CSV file with feedback column."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['feedback', 'date'])
        writer.writeheader()
        writer.writerow({'feedback': 'Excellent service!', 'date': '2024-01-01'})
        writer.writerow({'feedback': 'Very disappointed', 'date': '2024-01-02'})
        writer.writerow({'feedback': 'Average quality', 'date': '2024-01-03'})
        temp_path = f.name
    
    try:
        # Load feedback
        feedback = FeedbackLoader.load_from_csv(temp_path)
        
        # Verify results
        assert len(feedback) == 3
        assert feedback[0] == "Excellent service!"
        assert feedback[1] == "Very disappointed"
        assert feedback[2] == "Average quality"
    finally:
        Path(temp_path).unlink()


def test_file_not_found_text_file():
    """Test handling of non-existent text file."""
    with pytest.raises(FileNotFoundError) as exc_info:
        FeedbackLoader.load_from_file("nonexistent_file.txt")
    
    assert "Input file not found" in str(exc_info.value)


def test_file_not_found_csv_file():
    """Test handling of non-existent CSV file."""
    with pytest.raises(FileNotFoundError) as exc_info:
        FeedbackLoader.load_from_csv("nonexistent_file.csv")
    
    assert "Input file not found" in str(exc_info.value)


def test_filtering_empty_entries_text_file():
    """Test filtering of empty and whitespace-only entries from text file."""
    # Create a temporary text file with mixed valid and invalid entries
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        f.write("Valid feedback\n")
        f.write("\n")  # Empty line
        f.write("   \n")  # Whitespace only
        f.write("Another valid entry\n")
        f.write("\t\t\n")  # Tabs only
        temp_path = f.name
    
    try:
        # Load feedback
        feedback = FeedbackLoader.load_from_file(temp_path)
        
        # Verify only valid entries are loaded
        assert len(feedback) == 2
        assert feedback[0] == "Valid feedback"
        assert feedback[1] == "Another valid entry"
    finally:
        Path(temp_path).unlink()


def test_filtering_empty_entries_csv_file():
    """Test filtering of empty and whitespace-only entries from CSV file."""
    # Create a temporary CSV file with mixed valid and invalid entries
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['feedback'])
        writer.writeheader()
        writer.writerow({'feedback': 'Valid feedback'})
        writer.writerow({'feedback': ''})  # Empty
        writer.writerow({'feedback': '   '})  # Whitespace only
        writer.writerow({'feedback': 'Another valid entry'})
        writer.writerow({'feedback': '\t\t'})  # Tabs only
        temp_path = f.name
    
    try:
        # Load feedback
        feedback = FeedbackLoader.load_from_csv(temp_path)
        
        # Verify only valid entries are loaded
        assert len(feedback) == 2
        assert feedback[0] == "Valid feedback"
        assert feedback[1] == "Another valid entry"
    finally:
        Path(temp_path).unlink()


def test_validate_feedback():
    """Test the validate_feedback method."""
    # Valid feedback
    assert FeedbackLoader.validate_feedback("This is valid feedback") == True
    assert FeedbackLoader.validate_feedback("x") == True
    
    # Invalid feedback
    assert FeedbackLoader.validate_feedback("") == False
    assert FeedbackLoader.validate_feedback("   ") == False
    assert FeedbackLoader.validate_feedback("\t\t") == False
    assert FeedbackLoader.validate_feedback("\n") == False
    assert FeedbackLoader.validate_feedback(None) == False
