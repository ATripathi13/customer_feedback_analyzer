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


class FeedbackCategorizer:
    """Maps sentiment scores to categories (Happy, Sad, Mild)."""
    
    @staticmethod
    def get_category_thresholds() -> dict:
        """Get the threshold values for each category.
        
        Returns:
            Dictionary mapping category names to their (min, max) threshold tuples
        """
        return {
            'Happy': (0.1, 1.0),
            'Sad': (-1.0, -0.1),
            'Mild': (-0.1, 0.1)
        }
    
    @staticmethod
    def categorize(polarity_score: float) -> str:
        """Map a polarity score to a sentiment category.
        
        Categorization logic:
        - Happy: polarity > 0.1
        - Sad: polarity < -0.1
        - Mild: -0.1 <= polarity <= 0.1
        
        Args:
            polarity_score: The sentiment polarity score to categorize
            
        Returns:
            Category as string ("Happy", "Sad", or "Mild")
        """
        if polarity_score > 0.1:
            return "Happy"
        elif polarity_score < -0.1:
            return "Sad"
        else:
            return "Mild"


class ResultFormatter:
    """Formats and displays analysis results."""
    
    @staticmethod
    def format_result(feedback: str, category: str, score: float) -> str:
        """Format a single feedback result as a string.
        
        Args:
            feedback: The original feedback text
            category: The assigned sentiment category
            score: The sentiment polarity score
            
        Returns:
            Formatted string representation of the result
        """
        return f"{feedback} | {category} | {score:.3f}"
    
    @staticmethod
    def display_results(results: List[FeedbackResult]) -> None:
        """Display all analysis results in a structured table format.
        
        Args:
            results: List of FeedbackResult objects to display
        """
        if not results:
            print("No results to display.")
            return
        
        # Print header
        print("\n" + "=" * 80)
        print(f"{'Feedback':<50} | {'Category':<10} | {'Score':<10}")
        print("=" * 80)
        
        # Print each result
        for result in results:
            # Truncate long feedback for display
            feedback_display = result.feedback_text[:47] + "..." if len(result.feedback_text) > 50 else result.feedback_text
            print(f"{feedback_display:<50} | {result.category:<10} | {result.sentiment_score:<10.3f}")
        
        print("=" * 80 + "\n")
    
    @staticmethod
    def display_summary(results: List[FeedbackResult]) -> None:
        """Display summary statistics with category counts.
        
        Args:
            results: List of FeedbackResult objects to summarize
        """
        if not results:
            print("No results to summarize.")
            return
        
        # Count feedback by category
        happy_count = sum(1 for r in results if r.category == "Happy")
        sad_count = sum(1 for r in results if r.category == "Sad")
        mild_count = sum(1 for r in results if r.category == "Mild")
        total_count = len(results)
        
        # Create summary object
        summary = AnalysisSummary(
            total_count=total_count,
            happy_count=happy_count,
            sad_count=sad_count,
            mild_count=mild_count
        )
        
        # Display summary
        print("\n" + "=" * 50)
        print("ANALYSIS SUMMARY")
        print("=" * 50)
        print(f"Total Feedback: {summary.total_count}")
        print(f"Happy: {summary.happy_count} ({summary.get_percentage('happy'):.1f}%)")
        print(f"Sad: {summary.sad_count} ({summary.get_percentage('sad'):.1f}%)")
        print(f"Mild: {summary.mild_count} ({summary.get_percentage('mild'):.1f}%)")
        print("=" * 50 + "\n")


class CSVExporter:
    """Exports analysis results to CSV format."""
    
    @staticmethod
    def create_output_directory(output_path: str) -> None:
        """Create the output directory if it doesn't exist.
        
        Args:
            output_path: Path to the output file
        """
        path = Path(output_path)
        directory = path.parent
        
        # Create directory if it doesn't exist
        if directory and not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def export(results: List[FeedbackResult], output_path: str) -> bool:
        """Export analysis results to a CSV file.
        
        The CSV file will contain three columns: feedback, category, and sentiment_score.
        If the output file already exists, it will be overwritten.
        
        Args:
            results: List of FeedbackResult objects to export
            output_path: Path where the CSV file should be saved
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Create output directory if needed
            CSVExporter.create_output_directory(output_path)
            
            # Write results to CSV
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['feedback', 'category', 'sentiment_score'])
                
                # Write each result
                for result in results:
                    writer.writerow([
                        result.feedback_text,
                        result.category,
                        result.sentiment_score
                    ])
            
            # Confirm successful file creation
            print(f"Results successfully exported to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error exporting results to CSV: {e}")
            return False
