"""
Unit tests for SentimentAnalyzer component.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback_analyzer import SentimentAnalyzer


def test_clearly_positive_feedback():
    """Test that clearly positive feedback receives a positive sentiment score."""
    feedback = "This is excellent! I love it!"
    score = SentimentAnalyzer.analyze(feedback)
    
    assert score > 0, f"Expected positive score for positive feedback, got {score}"


def test_clearly_negative_feedback():
    """Test that clearly negative feedback receives a negative sentiment score."""
    feedback = "This is terrible! I hate it!"
    score = SentimentAnalyzer.analyze(feedback)
    
    assert score < 0, f"Expected negative score for negative feedback, got {score}"


def test_neutral_feedback():
    """Test that neutral feedback receives a score close to zero."""
    feedback = "This is a product."
    score = SentimentAnalyzer.analyze(feedback)
    
    # Neutral feedback should be close to zero (within reasonable range)
    assert -0.3 <= score <= 0.3, f"Expected neutral score close to 0, got {score}"


def test_very_short_feedback():
    """Test that very short feedback (< 3 words) is still analyzed."""
    feedback = "Great!"
    score = SentimentAnalyzer.analyze(feedback)
    
    # Should still return a valid score
    assert -1.0 <= score <= 1.0, f"Score should be in valid range, got {score}"
    # "Great" should be positive
    assert score > 0, f"Expected positive score for 'Great!', got {score}"


def test_feedback_with_negations():
    """Test that feedback with negations is handled appropriately."""
    positive_feedback = "This is good"
    negated_feedback = "This is not good"
    
    positive_score = SentimentAnalyzer.analyze(positive_feedback)
    negated_score = SentimentAnalyzer.analyze(negated_feedback)
    
    # The negated version should have a different (likely opposite or reduced) sentiment
    assert positive_score != negated_score, \
        "Negation should change the sentiment score"
    
    # Positive feedback should be positive
    assert positive_score > 0, f"Expected positive score for 'good', got {positive_score}"
    
    # Negated feedback should be less positive or negative
    assert negated_score < positive_score, \
        f"Negated feedback should have lower score: {negated_score} vs {positive_score}"


def test_get_polarity_score_method():
    """Test that get_polarity_score returns the same result as analyze."""
    feedback = "This product is amazing!"
    
    score_from_analyze = SentimentAnalyzer.analyze(feedback)
    score_from_polarity = SentimentAnalyzer.get_polarity_score(feedback)
    
    assert score_from_analyze == score_from_polarity, \
        "analyze() and get_polarity_score() should return the same value"
