# Design Document

## Overview

The Customer Feedback Analyzer is a standalone Python script that automates the process of sentiment analysis on customer feedback. The system will use the TextBlob library for natural language processing and sentiment analysis, providing a simple yet effective solution for categorizing feedback into Happy, Sad, and Mild categories based on polarity scores.

The script will be designed as a command-line tool that can be easily integrated into automated workflows, accepting various input formats (text files, CSV files) and producing structured output both to the console and as exportable CSV files.

## Architecture

The system follows a simple pipeline architecture with three main stages:

1. **Input Stage**: Load and parse feedback from various sources (files, CSV)
2. **Analysis Stage**: Process each feedback entry through sentiment analysis
3. **Output Stage**: Display results and export to CSV format

The architecture is modular, with clear separation between input handling, sentiment analysis logic, and output formatting. This allows for easy extension to support additional input sources or output formats in the future.

```
[Input Sources] → [Parser] → [Sentiment Analyzer] → [Categorizer] → [Output Formatter] → [Results]
                                                                    ↓
                                                              [CSV Exporter]
```

## Components and Interfaces

### 1. FeedbackLoader
**Responsibility**: Load feedback from various input sources

**Interface**:
```python
class FeedbackLoader:
    def load_from_file(file_path: str) -> List[str]
    def load_from_csv(file_path: str, column_name: str = 'feedback') -> List[str]
    def validate_feedback(feedback: str) -> bool
```

**Behavior**:
- Reads feedback from text files (one entry per line) or CSV files
- Filters out empty or whitespace-only entries
- Handles file not found errors gracefully
- Returns a list of valid feedback strings

### 2. SentimentAnalyzer
**Responsibility**: Analyze sentiment and calculate polarity scores

**Interface**:
```python
class SentimentAnalyzer:
    def analyze(feedback: str) -> float
    def get_polarity_score(feedback: str) -> float
```

**Behavior**:
- Uses TextBlob library for sentiment analysis
- Returns polarity score ranging from -1.0 (most negative) to +1.0 (most positive)
- Handles short feedback (< 3 words) appropriately
- Processes negations and contextual sentiment

### 3. FeedbackCategorizer
**Responsibility**: Map sentiment scores to categories

**Interface**:
```python
class FeedbackCategorizer:
    def categorize(polarity_score: float) -> str
    def get_category_thresholds() -> Dict[str, Tuple[float, float]]
```

**Behavior**:
- Maps polarity scores to one of three categories:
  - Happy: polarity > 0.1
  - Sad: polarity < -0.1
  - Mild: -0.1 <= polarity <= 0.1
- Returns category as string ("Happy", "Sad", or "Mild")

### 4. ResultFormatter
**Responsibility**: Format and display analysis results

**Interface**:
```python
class ResultFormatter:
    def format_result(feedback: str, category: str, score: float) -> str
    def display_results(results: List[FeedbackResult]) -> None
    def display_summary(results: List[FeedbackResult]) -> None
```

**Behavior**:
- Formats individual results with feedback text, category, and score
- Displays all results in a structured table format
- Calculates and displays summary statistics (count per category)

### 5. CSVExporter
**Responsibility**: Export results to CSV format

**Interface**:
```python
class CSVExporter:
    def export(results: List[FeedbackResult], output_path: str) -> bool
    def create_output_directory(output_path: str) -> None
```

**Behavior**:
- Writes results to CSV with columns: feedback, category, sentiment_score
- Creates output directories if they don't exist
- Overwrites existing files
- Returns success status and confirms file creation

### 6. CommandLineInterface
**Responsibility**: Handle command-line arguments and orchestrate the analysis pipeline

**Interface**:
```python
class CommandLineInterface:
    def parse_arguments() -> argparse.Namespace
    def display_usage() -> None
    def run(args: argparse.Namespace) -> int
```

**Behavior**:
- Parses command-line arguments (input file, output file)
- Displays usage instructions when no arguments provided
- Orchestrates the complete analysis pipeline
- Returns appropriate exit codes (0 for success, non-zero for errors)

## Data Models

### FeedbackResult
```python
@dataclass
class FeedbackResult:
    feedback_text: str
    category: str  # "Happy", "Sad", or "Mild"
    sentiment_score: float
    
    def __post_init__(self):
        # Validate category is one of the three allowed values
        assert self.category in ["Happy", "Sad", "Mild"]
        # Validate sentiment score is in valid range
        assert -1.0 <= self.sentiment_score <= 1.0
```

### AnalysisSummary
```python
@dataclass
class AnalysisSummary:
    total_count: int
    happy_count: int
    sad_count: int
    mild_count: int
    
    def get_percentage(self, category: str) -> float:
        if self.total_count == 0:
            return 0.0
        count = getattr(self, f"{category.lower()}_count")
        return (count / self.total_count) * 100
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Single category assignment
*For any* feedback text, the sentiment analysis must assign exactly one category from the set {Happy, Sad, Mild}, and the category must be determined by the sentiment score using consistent thresholds (Happy: score > 0.1, Sad: score < -0.1, Mild: -0.1 ≤ score ≤ 0.1).
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 2: Sentiment score bounds
*For any* feedback text, the calculated sentiment score must be a numerical value within the range [-1.0, 1.0].
**Validates: Requirements 2.5**

### Property 3: Input completeness
*For any* list of valid (non-empty, non-whitespace) feedback entries from any input source, the number of analysis results produced must equal the number of valid input entries.
**Validates: Requirements 1.2, 1.3, 3.2**

### Property 4: Whitespace filtering
*For any* feedback string composed entirely of whitespace characters (spaces, tabs, newlines), the system must filter it out and not include it in the analysis results.
**Validates: Requirements 1.5**

### Property 5: Feedback text preservation
*For any* feedback text that is analyzed, the original text must appear unchanged in the corresponding result output.
**Validates: Requirements 3.1**

### Property 6: Summary count consistency
*For any* set of analysis results, the sum of (happy_count + sad_count + mild_count) must equal the total_count, and each individual category count must match the number of results with that category.
**Validates: Requirements 3.4**

### Property 7: CSV round-trip integrity
*For any* set of analysis results, writing them to CSV and reading them back must preserve the feedback text, category, and sentiment score for each entry.
**Validates: Requirements 4.1**

### Property 8: Positive indicator influence
*For any* feedback text containing common positive indicators (excellent, great, love, amazing, perfect), the sentiment score must be positive (> 0), contributing toward Happy categorization.
**Validates: Requirements 6.2**

### Property 9: Negative indicator influence
*For any* feedback text containing common negative indicators (terrible, awful, hate, worst, broken), the sentiment score must be negative (< 0), contributing toward Sad categorization.
**Validates: Requirements 6.3**

### Property 10: Negation handling
*For any* feedback text, adding a negation (not, no, never) before a sentiment word must change the polarity direction of the sentiment score (e.g., "good" vs "not good" should have opposite-signed scores).
**Validates: Requirements 6.4**

### Property 11: Successful execution exit code
*For any* successful analysis run (no errors encountered), the script must exit with status code 0.
**Validates: Requirements 5.4**

### Property 12: Error execution exit code
*For any* execution that encounters an error (file not found, invalid input, etc.), the script must exit with a non-zero status code and display an error message.
**Validates: Requirements 5.5**

## Error Handling

The system must handle errors gracefully and provide clear feedback to users:

### File Errors
- **File Not Found**: When an input file doesn't exist, log a clear error message with the file path and exit with code 1
- **Permission Errors**: When file permissions prevent reading/writing, log the error and exit with code 2
- **Invalid Format**: When CSV files are malformed, log the specific parsing error and exit with code 3

### Input Validation Errors
- **Empty Input**: When all feedback entries are empty/whitespace, log a warning and produce an empty results file
- **Invalid Encoding**: When files contain invalid character encodings, attempt to handle with UTF-8 fallback, log warnings for problematic entries

### Analysis Errors
- **Library Errors**: If TextBlob encounters errors during analysis, log the specific feedback entry and error, skip that entry, and continue processing
- **Unexpected Exceptions**: Catch all unexpected exceptions, log full stack trace, and exit with code 99

### Output Errors
- **Directory Creation Failure**: If output directory cannot be created, log the error and exit with code 4
- **Write Failure**: If CSV file cannot be written, log the error and exit with code 5

All error messages should include:
- Clear description of what went wrong
- The specific file/input that caused the error (when applicable)
- Suggested remediation steps

## Testing Strategy

The Customer Feedback Analyzer will employ a comprehensive testing approach combining unit tests and property-based tests to ensure correctness and reliability.

### Unit Testing

Unit tests will verify specific functionality and edge cases:

**FeedbackLoader Tests**:
- Test loading from a valid text file with multiple entries
- Test loading from a valid CSV file with feedback column
- Test handling of non-existent file (should raise appropriate error)
- Test filtering of empty and whitespace-only entries
- Test handling of files with mixed valid/invalid entries

**SentimentAnalyzer Tests**:
- Test analysis of clearly positive feedback (e.g., "This is excellent!")
- Test analysis of clearly negative feedback (e.g., "This is terrible!")
- Test analysis of neutral feedback (e.g., "This is okay.")
- Test handling of very short feedback (1-2 words)
- Test handling of feedback with negations

**FeedbackCategorizer Tests**:
- Test categorization with score > 0.1 returns "Happy"
- Test categorization with score < -0.1 returns "Sad"
- Test categorization with score in [-0.1, 0.1] returns "Mild"
- Test boundary values (exactly 0.1, -0.1, 0.0)

**CSVExporter Tests**:
- Test successful export to new file
- Test overwriting existing file
- Test creation of output directories
- Test CSV format correctness (headers, columns)

**CommandLineInterface Tests**:
- Test parsing of required input argument
- Test parsing of optional output argument
- Test display of usage when no arguments provided
- Test exit codes for success and error scenarios

### Property-Based Testing

Property-based tests will verify universal properties across many randomly generated inputs using the Hypothesis library for Python. Each property test will run a minimum of 100 iterations.

**Configuration**:
- Library: Hypothesis (Python property-based testing library)
- Minimum iterations per test: 100
- Random seed: Configurable for reproducibility

**Property Tests**:

1. **Property 1: Single category assignment** - Generate random feedback strings and verify each receives exactly one valid category
   - **Feature: customer-feedback-analyzer, Property 1: Single category assignment**

2. **Property 2: Sentiment score bounds** - Generate random feedback and verify all scores are in [-1.0, 1.0]
   - **Feature: customer-feedback-analyzer, Property 2: Sentiment score bounds**

3. **Property 3: Input completeness** - Generate random lists of valid feedback and verify result count equals input count
   - **Feature: customer-feedback-analyzer, Property 3: Input completeness**

4. **Property 4: Whitespace filtering** - Generate strings with various whitespace combinations and verify they're filtered
   - **Feature: customer-feedback-analyzer, Property 4: Whitespace filtering**

5. **Property 5: Feedback text preservation** - Generate random feedback and verify original text appears in results
   - **Feature: customer-feedback-analyzer, Property 5: Feedback text preservation**

6. **Property 6: Summary count consistency** - Generate random result sets and verify summary counts are mathematically consistent
   - **Feature: customer-feedback-analyzer, Property 6: Summary count consistency**

7. **Property 7: CSV round-trip integrity** - Generate random results, export to CSV, import back, and verify data preservation
   - **Feature: customer-feedback-analyzer, Property 7: CSV round-trip integrity**

8. **Property 8: Positive indicator influence** - Generate feedback with positive words and verify positive scores
   - **Feature: customer-feedback-analyzer, Property 8: Positive indicator influence**

9. **Property 9: Negative indicator influence** - Generate feedback with negative words and verify negative scores
   - **Feature: customer-feedback-analyzer, Property 9: Negative indicator influence**

10. **Property 10: Negation handling** - Generate feedback pairs with/without negations and verify polarity changes
    - **Feature: customer-feedback-analyzer, Property 10: Negation handling**

### Test Organization

Tests will be organized in a `tests/` directory with the following structure:
```
tests/
├── test_feedback_loader.py       # Unit tests for FeedbackLoader
├── test_sentiment_analyzer.py    # Unit tests for SentimentAnalyzer
├── test_categorizer.py            # Unit tests for FeedbackCategorizer
├── test_csv_exporter.py           # Unit tests for CSVExporter
├── test_cli.py                    # Unit tests for CLI
├── test_properties.py             # All property-based tests
└── fixtures/                      # Test data files
    ├── sample_feedback.txt
    ├── sample_feedback.csv
    └── expected_output.csv
```

### Testing Commands

```bash
# Run all tests
python -m pytest tests/

# Run only unit tests
python -m pytest tests/ -k "not property"

# Run only property tests
python -m pytest tests/test_properties.py

# Run with coverage
python -m pytest tests/ --cov=feedback_analyzer --cov-report=html
```

## Implementation Notes

### Dependencies
- **TextBlob**: For sentiment analysis (includes NLTK data)
- **Hypothesis**: For property-based testing
- **pytest**: For test execution
- Standard library: argparse, csv, pathlib, dataclasses

### Installation
```bash
pip install textblob hypothesis pytest pytest-cov
python -m textblob.download_corpora
```

### Project Structure
```
customer_feedback_analyzer/
├── feedback_analyzer.py          # Main script with all components
├── requirements.txt               # Python dependencies
├── README.md                      # Usage documentation
└── tests/                         # Test directory (as described above)
```

### Performance Considerations
- TextBlob sentiment analysis is relatively fast but may be slow for very large datasets (>10,000 entries)
- Consider batch processing or progress indicators for large files
- CSV reading/writing is efficient for files up to several MB

### Future Enhancements
- Support for additional input formats (JSON, database connections)
- Configurable sentiment thresholds via command-line arguments
- Multi-language sentiment analysis support
- Real-time analysis via API endpoint
- Visualization of sentiment distribution

