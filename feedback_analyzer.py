"""
Customer Feedback Analyzer

A Python script that analyzes customer feedback and categorizes it into
sentiment categories: Happy, Sad, and Mild.
"""

import csv
import sys
import traceback
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
            PermissionError: If the file cannot be read due to permissions
            UnicodeDecodeError: If the file contains invalid character encodings
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(
                f"Input file not found: {file_path}\n"
                f"Remediation: Please check that the file path is correct and the file exists."
            )
        
        feedback_list = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if FeedbackLoader.validate_feedback(line):
                        feedback_list.append(line.strip())
        except PermissionError:
            raise PermissionError(
                f"Permission denied when reading file: {file_path}\n"
                f"Remediation: Please check that you have read permissions for this file."
            )
        except UnicodeDecodeError as e:
            # Try with a fallback encoding
            print(f"Warning: UTF-8 decoding failed at line {line_num}, attempting with latin-1 encoding...")
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    for line_num, line in enumerate(f, 1):
                        try:
                            if FeedbackLoader.validate_feedback(line):
                                feedback_list.append(line.strip())
                        except Exception as line_error:
                            print(f"Warning: Skipping line {line_num} due to encoding error: {line_error}")
                            continue
            except Exception as fallback_error:
                raise UnicodeDecodeError(
                    e.encoding, e.object, e.start, e.end,
                    f"Failed to decode file {file_path} with UTF-8 or latin-1 encoding.\n"
                    f"Remediation: Please ensure the file is saved with UTF-8 encoding."
                )
        
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
            PermissionError: If the file cannot be read due to permissions
            KeyError: If the specified column does not exist in the CSV
            csv.Error: If the CSV file is malformed
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(
                f"Input file not found: {file_path}\n"
                f"Remediation: Please check that the file path is correct and the file exists."
            )
        
        feedback_list = []
        try:
            with open(path, 'r', encoding='utf-8', newline='') as f:
                try:
                    reader = csv.DictReader(f)
                    
                    # Check if column exists by reading first row
                    first_row = True
                    for row_num, row in enumerate(reader, 1):
                        if first_row:
                            if column_name not in row:
                                available_columns = ', '.join(row.keys())
                                raise KeyError(
                                    f"Column '{column_name}' not found in CSV file: {file_path}\n"
                                    f"Available columns: {available_columns}\n"
                                    f"Remediation: Use --csv-column to specify the correct column name."
                                )
                            first_row = False
                        
                        feedback = row[column_name]
                        if FeedbackLoader.validate_feedback(feedback):
                            feedback_list.append(feedback.strip())
                
                except csv.Error as e:
                    raise csv.Error(
                        f"Malformed CSV file at line {reader.line_num}: {e}\n"
                        f"Remediation: Please check that the CSV file is properly formatted."
                    )
        
        except PermissionError:
            raise PermissionError(
                f"Permission denied when reading file: {file_path}\n"
                f"Remediation: Please check that you have read permissions for this file."
            )
        except UnicodeDecodeError as e:
            # Try with a fallback encoding
            print(f"Warning: UTF-8 decoding failed, attempting with latin-1 encoding...")
            try:
                with open(path, 'r', encoding='latin-1', newline='') as f:
                    reader = csv.DictReader(f)
                    first_row = True
                    for row_num, row in enumerate(reader, 1):
                        try:
                            if first_row:
                                if column_name not in row:
                                    available_columns = ', '.join(row.keys())
                                    raise KeyError(
                                        f"Column '{column_name}' not found in CSV file: {file_path}\n"
                                        f"Available columns: {available_columns}\n"
                                        f"Remediation: Use --csv-column to specify the correct column name."
                                    )
                                first_row = False
                            
                            feedback = row[column_name]
                            if FeedbackLoader.validate_feedback(feedback):
                                feedback_list.append(feedback.strip())
                        except Exception as line_error:
                            print(f"Warning: Skipping row {row_num} due to encoding error: {line_error}")
                            continue
            except Exception as fallback_error:
                raise UnicodeDecodeError(
                    e.encoding, e.object, e.start, e.end,
                    f"Failed to decode CSV file {file_path} with UTF-8 or latin-1 encoding.\n"
                    f"Remediation: Please ensure the file is saved with UTF-8 encoding."
                )
        
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
            
        Raises:
            Exception: If TextBlob encounters an error during analysis
        """
        try:
            blob = TextBlob(feedback)
            return blob.sentiment.polarity
        except Exception as e:
            # Log the error and re-raise with more context
            raise Exception(
                f"Error analyzing sentiment for feedback: '{feedback[:50]}...'\n"
                f"Error details: {str(e)}\n"
                f"Remediation: This feedback entry will be skipped."
            )
    
    @staticmethod
    def analyze(feedback: str) -> float:
        """Analyze sentiment and return polarity score.
        
        This method handles short feedback (< 3 words) appropriately by still
        attempting analysis based on available content.
        
        Args:
            feedback: The feedback string to analyze
            
        Returns:
            Polarity score ranging from -1.0 (most negative) to +1.0 (most positive)
            
        Raises:
            Exception: If TextBlob encounters an error during analysis
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
            
        Raises:
            PermissionError: If directory cannot be created due to permissions
            OSError: If directory creation fails for other reasons
        """
        path = Path(output_path)
        directory = path.parent
        
        # Create directory if it doesn't exist
        if directory and not directory.exists():
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                raise PermissionError(
                    f"Permission denied when creating output directory: {directory}\n"
                    f"Remediation: Please check that you have write permissions for this location."
                )
            except OSError as e:
                raise OSError(
                    f"Failed to create output directory: {directory}\n"
                    f"Error details: {str(e)}\n"
                    f"Remediation: Please check that the path is valid and you have sufficient permissions."
                )
    
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
            
        Raises:
            PermissionError: If the file cannot be written due to permissions
            OSError: If the file cannot be written for other reasons
        """
        try:
            # Create output directory if needed
            CSVExporter.create_output_directory(output_path)
            
            # Write results to CSV
            try:
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
            
            except PermissionError:
                raise PermissionError(
                    f"Permission denied when writing to file: {output_path}\n"
                    f"Remediation: Please check that you have write permissions for this file."
                )
            except OSError as e:
                raise OSError(
                    f"Failed to write to file: {output_path}\n"
                    f"Error details: {str(e)}\n"
                    f"Remediation: Please check that the path is valid and the disk has sufficient space."
                )
            
        except (PermissionError, OSError):
            # Re-raise these specific exceptions to be caught by the caller
            raise
        except Exception as e:
            print(f"Unexpected error exporting results to CSV: {e}")
            traceback.print_exc()
            return False


class CommandLineInterface:
    """Handles command-line arguments and orchestrates the analysis pipeline."""
    
    @staticmethod
    def parse_arguments():
        """Parse command-line arguments.
        
        Returns:
            argparse.Namespace object containing parsed arguments
        """
        import argparse
        
        parser = argparse.ArgumentParser(
            description='Customer Feedback Analyzer - Categorize feedback into Happy, Sad, and Mild sentiments',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            'input',
            help='Path to input file (text file with one feedback per line, or CSV file)'
        )
        
        parser.add_argument(
            '-o', '--output',
            default='output.csv',
            help='Path to output CSV file (default: output.csv)'
        )
        
        parser.add_argument(
            '--csv-column',
            default='feedback',
            help='Column name for CSV input files (default: feedback)'
        )
        
        return parser.parse_args()
    
    @staticmethod
    def display_usage():
        """Display usage instructions."""
        import argparse
        
        parser = argparse.ArgumentParser(
            description='Customer Feedback Analyzer - Categorize feedback into Happy, Sad, and Mild sentiments',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            'input',
            help='Path to input file (text file with one feedback per line, or CSV file)'
        )
        
        parser.add_argument(
            '-o', '--output',
            default='output.csv',
            help='Path to output CSV file (default: output.csv)'
        )
        
        parser.add_argument(
            '--csv-column',
            default='feedback',
            help='Column name for CSV input files (default: feedback)'
        )
        
        parser.print_help()
    
    @staticmethod
    def run(args) -> int:
        """Orchestrate the complete analysis pipeline.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            Exit code (0 for success, non-zero for errors)
        """
        try:
            # Determine input file type and load feedback
            input_path = args.input
            
            print(f"Loading feedback from: {input_path}")
            
            try:
                if input_path.endswith('.csv'):
                    feedback_list = FeedbackLoader.load_from_csv(input_path, args.csv_column)
                else:
                    feedback_list = FeedbackLoader.load_from_file(input_path)
            except FileNotFoundError as e:
                print(f"\nError: File not found")
                print(f"  {e}")
                return 1  # Exit code 1 for file not found
            except PermissionError as e:
                print(f"\nError: Permission denied")
                print(f"  {e}")
                return 2  # Exit code 2 for permission errors
            except KeyError as e:
                print(f"\nError: Invalid CSV format")
                print(f"  {e}")
                return 3  # Exit code 3 for invalid format
            except csv.Error as e:
                print(f"\nError: Malformed CSV file")
                print(f"  {e}")
                return 3  # Exit code 3 for invalid format
            except UnicodeDecodeError as e:
                print(f"\nError: File encoding issue")
                print(f"  {e}")
                return 3  # Exit code 3 for invalid format
            
            if not feedback_list:
                print("\nWarning: No valid feedback entries found in input file.")
                print("All entries were either empty or contained only whitespace.")
                print("Creating empty results file...")
                
                # Create empty results file
                try:
                    CSVExporter.export([], args.output)
                except (PermissionError, OSError) as e:
                    print(f"\nError: Failed to create output file")
                    print(f"  {e}")
                    return 4 if isinstance(e, OSError) and "directory" in str(e).lower() else 5
                
                return 0
            
            print(f"Loaded {len(feedback_list)} valid feedback entries.")
            print("Analyzing sentiment...")
            
            # Analyze and categorize each feedback
            results = []
            skipped_count = 0
            
            for idx, feedback in enumerate(feedback_list, 1):
                try:
                    # Analyze sentiment
                    score = SentimentAnalyzer.analyze(feedback)
                    
                    # Categorize based on score
                    category = FeedbackCategorizer.categorize(score)
                    
                    # Create result object
                    result = FeedbackResult(
                        feedback_text=feedback,
                        category=category,
                        sentiment_score=score
                    )
                    results.append(result)
                    
                except Exception as e:
                    # Log the error and skip this entry
                    print(f"\nWarning: Skipping feedback entry {idx} due to analysis error:")
                    print(f"  Feedback: {feedback[:50]}{'...' if len(feedback) > 50 else ''}")
                    print(f"  Error: {str(e)}")
                    skipped_count += 1
                    continue
            
            if skipped_count > 0:
                print(f"\nNote: {skipped_count} feedback entries were skipped due to errors.")
            
            if not results:
                print("\nError: All feedback entries failed analysis.")
                print("Remediation: Please check that your feedback entries contain valid text.")
                return 99
            
            print(f"Successfully analyzed {len(results)} feedback entries.")
            
            # Display results
            ResultFormatter.display_results(results)
            ResultFormatter.display_summary(results)
            
            # Export to CSV
            print(f"\nExporting results to: {args.output}")
            
            try:
                CSVExporter.export(results, args.output)
            except PermissionError as e:
                print(f"\nError: Permission denied when writing output")
                print(f"  {e}")
                return 2  # Exit code 2 for permission errors
            except OSError as e:
                # Check if it's a directory creation error or write error
                if "directory" in str(e).lower() or "mkdir" in str(e).lower():
                    print(f"\nError: Failed to create output directory")
                    print(f"  {e}")
                    return 4  # Exit code 4 for directory creation failure
                else:
                    print(f"\nError: Failed to write output file")
                    print(f"  {e}")
                    return 5  # Exit code 5 for write failure
            
            return 0  # Success
            
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            return 130  # Standard exit code for SIGINT
        
        except Exception as e:
            print(f"\nUnexpected error occurred:")
            print(f"  {str(e)}")
            print("\nFull traceback:")
            traceback.print_exc()
            print("\nRemediation: This is an unexpected error. Please report this issue with the traceback above.")
            return 99  # Exit code 99 for unexpected exceptions


def main():
    """Main entry point for the script."""
    # Check if arguments were provided
    if len(sys.argv) < 2:
        CommandLineInterface.display_usage()
        sys.exit(0)
    
    # Parse arguments and run
    args = CommandLineInterface.parse_arguments()
    exit_code = CommandLineInterface.run(args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
