"""
Customer Feedback Analyzer

A Python script that analyzes customer feedback and categorizes it into
sentiment categories: Happy, Sad, and Mild.
"""

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List
from textblob import TextBlob


@dataclass
class FeedbackResult:
    """Represents the result of analyzing a single feedback entry."""
    feedback_text: str
    category: str  # "Happy", "Sad", or "Mild"
    sentiment_score: float
    
    def __post_init__(self):
        """Validate category and sentiment score after initialization."""
        # Validate category is one of the three allowed values
        if self.category not in ["Happy", "Sad", "Mild"]:
            raise ValueError(f"Category must be 'Happy', 'Sad', or 'Mild', got '{self.category}'")
        
        # Validate sentiment score is in valid range
        if not (-1.0 <= self.sentiment_score <= 1.0):
            raise ValueError(f"Sentiment score must be between -1.0 and 1.0, got {self.sentiment_score}")


@dataclass
class AnalysisSummary:
    """Represents summary statistics for a set of feedback analysis results."""
    total_count: int
    happy_count: int
    sad_count: int
    mild_count: int
    
    def get_percentage(self, category: str) -> float:
        """Calculate the percentage of feedback in a given category.
        
        Args:
            category: The category name ("happy", "sad", or "mild")
            
        Returns:
            The percentage (0-100) of feedback in that category
        """
        if self.total_count == 0:
            return 0.0
        
        count = getattr(self, f"{category.lower()}_count")
        return (count / self.total_count) * 100


class FeedbackLoader:
    """Loads customer feedback from various input sources."""
    
    @staticmethod
    def validate_feedback(feedback: str) -> bool:
        """Validate that feedback is not empty or whitespace-only.
        
        Args:
            feedback: The feedback string to validate
            
        Returns:
            True if feedback is valid (non-empty and not just whitespace), False otherwise
        """
        return feedback is not None and feedback.strip() != ""
    
    @staticmethod
    def load_from_file(file_path: str) -> List[str]:
        """Load feedback from a text file (one entry per line).
        
        Args:
            file_path: Path to the text file containing feedback
            
        Returns:
            List of valid feedback strings (empty/whitespace entries filtered out)
            
        Raises:
            FileNotFoundError: If the specified file does not exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        feedback_list = []
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if FeedbackLoader.validate_feedback(line):
                    feedback_list.append(line.strip())
        
        return feedback_list
    
    @staticmethod
    def load_from_csv(file_path: str, column_name: str = 'feedback') -> List[str]:
        """Load feedback from a CSV file.
        
        Args:
            file_path: Path to the CSV file containing feedback
            column_name: Name of the column containing feedback text (default: 'feedback')
            
        Returns:
            List of valid feedback strings (empty/whitespace entries filtered out)
            
        Raises:
            FileNotFoundError: If the specified file does not exist
            KeyError: If the specified column does not exist in the CSV
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        feedback_list = []
        with open(path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if column_name not in row:
                    raise KeyError(f"Column '{column_name}' not found in CSV file")
                
                feedback = row[column_name]
                if FeedbackLoader.validate_feedback(feedback):
                    feedback_list.append(feedback.strip())
        
        return feedback_list


class SentimentAnalyzer:
    """Analyzes sentiment and calculates polarity scores for feedback text."""
    
    @staticmethod
    def get_polarity_score(feedback: str) -> float:
        """Calculate the polarity score for feedback text.
        
        Args:
            feedback: The feedback string to analyze
            
        Returns:
            Polarity score ranging from -1.0 (most negative) to +1.0 (most positive)
        """
        blob = TextBlob(feedback)
        return blob.sentiment.polarity
    
    @staticmethod
    def analyze(feedback: str) -> float:
        """Analyze sentiment and return polarity score.
        
        This method handles short feedback (< 3 words) appropriately by still
        attempting analysis based on available content.
        
        Args:
            feedback: The feedback string to analyze
            
        Returns:
            Polarity score ranging from -1.0 (most negative) to +1.0 (most positive)
        """
        # Even for short feedback, TextBlob can provide meaningful sentiment analysis
        return SentimentAnalyzer.get_polarity_score(feedback)
