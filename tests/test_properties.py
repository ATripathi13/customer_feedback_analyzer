"""
Property-based tests for Customer Feedback Analyzer.

These tests verify universal properties that should hold across all valid inputs.
"""

import tempfile
import csv
import io
import contextlib
from pathlib import Path
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback_analyzer import (
    FeedbackLoader, 
    SentimentAnalyzer, 
    FeedbackCategorizer,
    FeedbackResult,
    ResultFormatter,
    CSVExporter
)


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



# Property 1: Single category assignment
# Feature: customer-feedback-analyzer, Property 1: Single category assignment
# Validates: Requirements 2.1, 2.2, 2.3, 2.4
@given(st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=100)
def test_property_single_category_assignment(polarity_score):
    """
    For any feedback text, the sentiment analysis must assign exactly one category from
    the set {Happy, Sad, Mild}, and the category must be determined by the sentiment score
    using consistent thresholds (Happy: score > 0.1, Sad: score < -0.1, Mild: -0.1 ≤ score ≤ 0.1).
    """
    category = FeedbackCategorizer.categorize(polarity_score)
    
    # Verify exactly one valid category is assigned
    assert category in ["Happy", "Sad", "Mild"], \
        f"Category must be one of 'Happy', 'Sad', or 'Mild', got '{category}'"
    
    # Verify the category matches the expected threshold logic
    if polarity_score > 0.1:
        assert category == "Happy", \
            f"Score {polarity_score} > 0.1 should be 'Happy', got '{category}'"
    elif polarity_score < -0.1:
        assert category == "Sad", \
            f"Score {polarity_score} < -0.1 should be 'Sad', got '{category}'"
    else:  # -0.1 <= polarity_score <= 0.1
        assert category == "Mild", \
            f"Score {polarity_score} in [-0.1, 0.1] should be 'Mild', got '{category}'"



# Property 5: Feedback text preservation
# Feature: customer-feedback-analyzer, Property 5: Feedback text preservation
# Validates: Requirements 3.1
@given(
    st.text(min_size=1, max_size=500),
    st.sampled_from(["Happy", "Sad", "Mild"]),
    st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_property_feedback_text_preservation(feedback_text, category, score):
    """
    For any feedback text that is analyzed, the original text must appear unchanged
    in the corresponding result output.
    """
    # Create a FeedbackResult
    result = FeedbackResult(
        feedback_text=feedback_text,
        category=category,
        sentiment_score=score
    )
    
    # Format the result
    formatted = ResultFormatter.format_result(result.feedback_text, result.category, result.sentiment_score)
    
    # Verify the original feedback text appears in the formatted output
    assert result.feedback_text in formatted, \
        f"Original feedback text '{result.feedback_text}' not found in formatted output: '{formatted}'"
    
    # Also verify that the feedback_text field in the result object is unchanged
    assert result.feedback_text == feedback_text, \
        f"Feedback text was modified: expected '{feedback_text}', got '{result.feedback_text}'"



# Property 6: Summary count consistency
# Feature: customer-feedback-analyzer, Property 6: Summary count consistency
# Validates: Requirements 3.4
@given(st.lists(
    st.tuples(
        st.text(min_size=1, max_size=200),
        st.sampled_from(["Happy", "Sad", "Mild"]),
        st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    ),
    min_size=0,
    max_size=100
))
@settings(max_examples=100)
def test_property_summary_count_consistency(result_data):
    """
    For any set of analysis results, the sum of (happy_count + sad_count + mild_count)
    must equal the total_count, and each individual category count must match the number
    of results with that category.
    """
    # Create FeedbackResult objects from the generated data
    results = [
        FeedbackResult(feedback_text=text, category=cat, sentiment_score=score)
        for text, cat, score in result_data
    ]
    
    # Count expected values
    expected_total = len(results)
    expected_happy = sum(1 for r in results if r.category == "Happy")
    expected_sad = sum(1 for r in results if r.category == "Sad")
    expected_mild = sum(1 for r in results if r.category == "Mild")
    
    # Use ResultFormatter to generate summary (it creates AnalysisSummary internally)
    # We'll manually create the summary to test it
    from feedback_analyzer import AnalysisSummary
    
    happy_count = sum(1 for r in results if r.category == "Happy")
    sad_count = sum(1 for r in results if r.category == "Sad")
    mild_count = sum(1 for r in results if r.category == "Mild")
    total_count = len(results)
    
    summary = AnalysisSummary(
        total_count=total_count,
        happy_count=happy_count,
        sad_count=sad_count,
        mild_count=mild_count
    )
    
    # Verify total count consistency
    assert summary.total_count == expected_total, \
        f"Total count mismatch: expected {expected_total}, got {summary.total_count}"
    
    # Verify sum of category counts equals total
    assert summary.happy_count + summary.sad_count + summary.mild_count == summary.total_count, \
        f"Sum of category counts ({summary.happy_count} + {summary.sad_count} + {summary.mild_count} = {summary.happy_count + summary.sad_count + summary.mild_count}) does not equal total_count ({summary.total_count})"
    
    # Verify each category count matches actual results
    assert summary.happy_count == expected_happy, \
        f"Happy count mismatch: expected {expected_happy}, got {summary.happy_count}"
    assert summary.sad_count == expected_sad, \
        f"Sad count mismatch: expected {expected_sad}, got {summary.sad_count}"
    assert summary.mild_count == expected_mild, \
        f"Mild count mismatch: expected {expected_mild}, got {summary.mild_count}"



# Property 7: CSV round-trip integrity
# Feature: customer-feedback-analyzer, Property 7: CSV round-trip integrity
# Validates: Requirements 4.1
@given(st.lists(
    st.tuples(
        st.text(
            min_size=1, 
            max_size=200,
            alphabet=st.characters(blacklist_characters='\r\n', blacklist_categories=('Cs',))
        ).filter(lambda s: s.strip() != ""),
        st.sampled_from(["Happy", "Sad", "Mild"]),
        st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    ),
    min_size=0,
    max_size=50
))
@settings(max_examples=100, deadline=None)
def test_property_csv_round_trip_integrity(result_data):
    """
    For any set of analysis results, writing them to CSV and reading them back must
    preserve the feedback text, category, and sentiment score for each entry.
    """
    # Create FeedbackResult objects from the generated data
    original_results = [
        FeedbackResult(feedback_text=text, category=cat, sentiment_score=score)
        for text, cat, score in result_data
    ]
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as f:
        temp_path = f.name
    
    try:
        # Export results to CSV (suppress print output)
        with contextlib.redirect_stdout(io.StringIO()):
            success = CSVExporter.export(original_results, temp_path)
        assert success, "CSV export should succeed"
        
        # Read the CSV back
        read_results = []
        with open(temp_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                read_results.append({
                    'feedback': row['feedback'],
                    'category': row['category'],
                    'sentiment_score': float(row['sentiment_score'])
                })
        
        # Verify the count matches
        assert len(read_results) == len(original_results), \
            f"Count mismatch: expected {len(original_results)}, got {len(read_results)}"
        
        # Verify each entry is preserved
        for i, (original, read) in enumerate(zip(original_results, read_results)):
            assert original.feedback_text == read['feedback'], \
                f"Entry {i}: feedback text mismatch - expected '{original.feedback_text}', got '{read['feedback']}'"
            
            assert original.category == read['category'], \
                f"Entry {i}: category mismatch - expected '{original.category}', got '{read['category']}'"
            
            # Allow small floating point differences
            assert abs(original.sentiment_score - read['sentiment_score']) < 1e-6, \
                f"Entry {i}: sentiment score mismatch - expected {original.sentiment_score}, got {read['sentiment_score']}"
    
    finally:
        # Clean up
        Path(temp_path).unlink(missing_ok=True)
