"""
Unit tests for FeedbackCategorizer component.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback_analyzer import FeedbackCategorizer


def test_categorize_happy_positive_score():
    """Test categorization with score > 0.1 returns 'Happy'."""
    # Test with various scores above 0.1
    assert FeedbackCategorizer.categorize(0.2) == "Happy"
    assert FeedbackCategorizer.categorize(0.5) == "Happy"
    assert FeedbackCategorizer.categorize(0.9) == "Happy"
    assert FeedbackCategorizer.categorize(1.0) == "Happy"


def test_categorize_sad_negative_score():
    """Test categorization with score < -0.1 returns 'Sad'."""
    # Test with various scores below -0.1
    assert FeedbackCategorizer.categorize(-0.2) == "Sad"
    assert FeedbackCategorizer.categorize(-0.5) == "Sad"
    assert FeedbackCategorizer.categorize(-0.9) == "Sad"
    assert FeedbackCategorizer.categorize(-1.0) == "Sad"


def test_categorize_mild_neutral_score():
    """Test categorization with score in [-0.1, 0.1] returns 'Mild'."""
    # Test with various scores in the mild range
    assert FeedbackCategorizer.categorize(0.0) == "Mild"
    assert FeedbackCategorizer.categorize(0.05) == "Mild"
    assert FeedbackCategorizer.categorize(-0.05) == "Mild"


def test_categorize_boundary_values():
    """Test boundary values for categorization thresholds."""
    # Test exact boundary values
    assert FeedbackCategorizer.categorize(0.1) == "Mild"  # Exactly 0.1 is Mild (not > 0.1)
    assert FeedbackCategorizer.categorize(-0.1) == "Mild"  # Exactly -0.1 is Mild (not < -0.1)
    
    # Test just above/below boundaries
    assert FeedbackCategorizer.categorize(0.10001) == "Happy"
    assert FeedbackCategorizer.categorize(-0.10001) == "Sad"


def test_get_category_thresholds():
    """Test that get_category_thresholds returns correct threshold values."""
    thresholds = FeedbackCategorizer.get_category_thresholds()
    
    # Verify structure
    assert isinstance(thresholds, dict)
    assert 'Happy' in thresholds
    assert 'Sad' in thresholds
    assert 'Mild' in thresholds
    
    # Verify threshold values
    assert thresholds['Happy'] == (0.1, 1.0)
    assert thresholds['Sad'] == (-1.0, -0.1)
    assert thresholds['Mild'] == (-0.1, 0.1)
