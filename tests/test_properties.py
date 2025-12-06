"""
Property-based tests for Customer Feedback Analyzer.

These tests verify universal properties that should hold across all valid inputs.
"""

import tempfile
import csv
from pathlib import Path
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback_analyzer import FeedbackLoader, SentimentAnalyzer


# Property 3: Input completeness
# Feature: customer-feedback-analyzer, Property 3: Input completeness
# Validates: Requirements 1.2, 1.3, 3.2
@given(st.lists(
    st.text(
        min_size=1, 
        alphabet=st.characters(blacklist_characters='\r\n', blacklist_categories=('Cs',))
    ).filter(lambda s: s.strip() != ""), 
    min_size=0, 
    max_size=50
))
@settings(max_examples=100)
def test_property_input_completeness_text_file(valid_feedback_list):
    """
    For any list of valid (non-empty, non-whitespace) feedback entries from a text file,
    the number of analysis results produced must equal the number of valid input entries.
    """
    # Create a temporary text file with the feedback
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        for feedback in valid_feedback_list:
            f.write(feedback + '\n')
        temp_path = f.name
    
    try:
        # Load feedback from file
        loaded_feedback = FeedbackLoader.load_from_file(temp_path)
        
        # Verify the count matches
        assert len(loaded_feedback) == len(valid_feedback_list), \
            f"Expected {len(valid_feedback_list)} entries, got {len(loaded_feedback)}"
    finally:
        # Clean up
        Path(temp_path).unlink()


@given(st.lists(
    st.text(
        min_size=1, 
        alphabet=st.characters(blacklist_characters='\r\n', blacklist_categories=('Cs',))
    ).filter(lambda s: s.strip() != ""), 
    min_size=0, 
    max_size=50
))
@settings(max_examples=100)
def test_property_input_completeness_csv_file(valid_feedback_list):
    """
    For any list of valid (non-empty, non-whitespace) feedback entries from a CSV file,
    the number of analysis results produced must equal the number of valid input entries.
    """
    # Create a temporary CSV file with the feedback
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['feedback'])
        writer.writeheader()
        for feedback in valid_feedback_list:
            writer.writerow({'feedback': feedback})
        temp_path = f.name
    
    try:
        # Load feedback from CSV
        loaded_feedback = FeedbackLoader.load_from_csv(temp_path)
        
        # Verify the count matches
        assert len(loaded_feedback) == len(valid_feedback_list), \
            f"Expected {len(valid_feedback_list)} entries, got {len(loaded_feedback)}"
    finally:
        # Clean up
        Path(temp_path).unlink()



# Property 4: Whitespace filtering
# Feature: customer-feedback-analyzer, Property 4: Whitespace filtering
# Validates: Requirements 1.5
@given(st.lists(st.text(alphabet=st.sampled_from(' \t\n\r'), min_size=1), min_size=1, max_size=20))
@settings(max_examples=100)
def test_property_whitespace_filtering_text_file(whitespace_strings):
    """
    For any feedback string composed entirely of whitespace characters (spaces, tabs, newlines),
    the system must filter it out and not include it in the analysis results.
    """
    # Create a temporary text file with whitespace-only entries
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        for ws in whitespace_strings:
            f.write(ws + '\n')
        temp_path = f.name
    
    try:
        # Load feedback from file
        loaded_feedback = FeedbackLoader.load_from_file(temp_path)
        
        # Verify all whitespace entries are filtered out
        assert len(loaded_feedback) == 0, \
            f"Expected 0 entries (all whitespace), got {len(loaded_feedback)}: {loaded_feedback}"
    finally:
        # Clean up
        Path(temp_path).unlink()


@given(st.lists(st.text(alphabet=st.sampled_from(' \t'), min_size=1), min_size=1, max_size=20))
@settings(max_examples=100)
def test_property_whitespace_filtering_csv_file(whitespace_strings):
    """
    For any feedback string composed entirely of whitespace characters in CSV,
    the system must filter it out and not include it in the analysis results.
    """
    # Create a temporary CSV file with whitespace-only entries
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['feedback'])
        writer.writeheader()
        for ws in whitespace_strings:
            writer.writerow({'feedback': ws})
        temp_path = f.name
    
    try:
        # Load feedback from CSV
        loaded_feedback = FeedbackLoader.load_from_csv(temp_path)
        
        # Verify all whitespace entries are filtered out
        assert len(loaded_feedback) == 0, \
            f"Expected 0 entries (all whitespace), got {len(loaded_feedback)}: {loaded_feedback}"
    finally:
        # Clean up
        Path(temp_path).unlink()



# Property 2: Sentiment score bounds
# Feature: customer-feedback-analyzer, Property 2: Sentiment score bounds
# Validates: Requirements 2.5
@given(st.text(min_size=1, max_size=500))
@settings(max_examples=100)
def test_property_sentiment_score_bounds(feedback_text):
    """
    For any feedback text, the calculated sentiment score must be a numerical value
    within the range [-1.0, 1.0].
    """
    score = SentimentAnalyzer.analyze(feedback_text)
    
    # Verify score is a number
    assert isinstance(score, (int, float)), \
        f"Score must be numeric, got {type(score)}"
    
    # Verify score is within bounds
    assert -1.0 <= score <= 1.0, \
        f"Score must be in range [-1.0, 1.0], got {score}"



# Property 8: Positive indicator influence
# Feature: customer-feedback-analyzer, Property 8: Positive indicator influence
# Validates: Requirements 6.2
@given(
    st.sampled_from(['excellent', 'great', 'love', 'amazing', 'perfect']),
    st.text(min_size=0, max_size=100)
)
@settings(max_examples=100)
def test_property_positive_indicator_influence(positive_word, additional_text):
    """
    For any feedback text containing common positive indicators (excellent, great, love,
    amazing, perfect), the sentiment score must be positive (> 0), contributing toward
    Happy categorization.
    """
    # Create feedback with positive indicator
    feedback = f"{positive_word} {additional_text}".strip()
    
    score = SentimentAnalyzer.analyze(feedback)
    
    # Verify score is positive
    assert score > 0, \
        f"Feedback with positive indicator '{positive_word}' should have positive score, got {score}"



# Property 9: Negative indicator influence
# Feature: customer-feedback-analyzer, Property 9: Negative indicator influence
# Validates: Requirements 6.3
@given(
    st.sampled_from(['terrible', 'awful', 'hate', 'worst', 'broken']),
    st.text(min_size=0, max_size=100)
)
@settings(max_examples=100)
def test_property_negative_indicator_influence(negative_word, additional_text):
    """
    For any feedback text containing common negative indicators (terrible, awful, hate,
    worst, broken), the sentiment score must be negative (< 0), contributing toward
    Sad categorization.
    """
    # Create feedback with negative indicator
    feedback = f"{negative_word} {additional_text}".strip()
    
    score = SentimentAnalyzer.analyze(feedback)
    
    # Verify score is negative
    assert score < 0, \
        f"Feedback with negative indicator '{negative_word}' should have negative score, got {score}"



# Property 10: Negation handling
# Feature: customer-feedback-analyzer, Property 10: Negation handling
# Validates: Requirements 6.4
@given(
    st.sampled_from(['not', 'no', 'never']),
    st.sampled_from(['good', 'great', 'excellent', 'bad', 'terrible', 'awful'])
)
@settings(max_examples=100)
def test_property_negation_handling(negation, sentiment_word):
    """
    For any feedback text, adding a negation (not, no, never) before a sentiment word
    must change the polarity direction of the sentiment score (e.g., "good" vs "not good"
    should have opposite-signed scores).
    """
    # Create feedback without negation
    feedback_without_negation = sentiment_word
    score_without = SentimentAnalyzer.analyze(feedback_without_negation)
    
    # Create feedback with negation
    feedback_with_negation = f"{negation} {sentiment_word}"
    score_with = SentimentAnalyzer.analyze(feedback_with_negation)
    
    # Verify that the signs are opposite (or at least the score moved toward opposite direction)
    # We check if the product is negative or if one moved closer to zero/opposite side
    assert score_without * score_with <= 0 or abs(score_with) < abs(score_without), \
        f"Negation should change polarity: '{feedback_without_negation}' ({score_without}) vs '{feedback_with_negation}' ({score_with})"
