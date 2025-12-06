# Customer Feedback Analyzer

A Python command-line tool that automatically analyzes and categorizes customer feedback using sentiment analysis. The tool processes feedback from various sources and classifies it into three categories: Happy, Sad, and Mild.

## Features

- Analyze customer feedback from text files or CSV files
- Automatic sentiment categorization (Happy, Sad, Mild)
- Numerical sentiment scoring (-1.0 to +1.0)
- Export results to CSV format
- Summary statistics for all feedback categories
- Command-line interface for easy automation

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Download the required TextBlob corpora:

```bash
python -m textblob.download_corpora
```

## Usage

### Basic Usage

Analyze feedback from a text file:

```bash
python feedback_analyzer.py input.txt
```

Analyze feedback and save results to a specific output file:

```bash
python feedback_analyzer.py input.txt -o results.csv
```

### Command-Line Arguments

- `input_file` (required): Path to the input file containing customer feedback
  - Supported formats: `.txt` (one feedback per line) or `.csv` (with 'feedback' column)
  
- `-o, --output` (optional): Path to the output CSV file
  - Default: `feedback_analysis_results.csv`

### Display Help

```bash
python feedback_analyzer.py --help
```

## Input Formats

### Text File Format

One feedback entry per line:

```
This product is amazing! I love it.
The service was terrible and slow.
It's okay, nothing special.
```

### CSV File Format

CSV file with a 'feedback' column:

```csv
feedback
This product is amazing! I love it.
The service was terrible and slow.
It's okay, nothing special.
```

## Output Format

The tool generates a CSV file with the following columns:

- `feedback`: The original feedback text
- `category`: The assigned sentiment category (Happy, Sad, or Mild)
- `sentiment_score`: The numerical sentiment score (-1.0 to +1.0)

### Example Output

```csv
feedback,category,sentiment_score
This product is amazing! I love it.,Happy,0.625
The service was terrible and slow.,Sad,-0.7
It's okay, nothing special.,Mild,0.0
```

## Sentiment Categories

The tool categorizes feedback based on sentiment polarity scores:

- **Happy**: Sentiment score > 0.1 (positive feedback)
- **Sad**: Sentiment score < -0.1 (negative feedback)
- **Mild**: Sentiment score between -0.1 and 0.1 (neutral feedback)

## Example Session

```bash
$ python feedback_analyzer.py tests/fixtures/sample_feedback.txt -o my_results.csv

Customer Feedback Analysis Results
================================================================================

Feedback: This product is excellent! Best purchase ever.
Category: Happy
Sentiment Score: 0.75

Feedback: Terrible experience, would not recommend.
Category: Sad
Sentiment Score: -0.65

Feedback: It works as expected.
Category: Mild
Sentiment Score: 0.05

================================================================================
Summary Statistics
================================================================================
Total Feedback Analyzed: 3
Happy: 1 (33.33%)
Sad: 1 (33.33%)
Mild: 1 (33.33%)

Results exported to: my_results.csv
```

## Error Handling

The tool handles various error conditions gracefully:

- **File not found**: Displays error message with file path
- **Invalid file format**: Reports parsing errors
- **Empty input**: Processes successfully with empty results
- **Permission errors**: Reports access issues

Exit codes:
- `0`: Success
- `1`: File not found
- `2`: Permission error
- `3`: Invalid format
- `4`: Directory creation failure
- `5`: Write failure
- `99`: Unexpected error

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage report
python -m pytest tests/ --cov=feedback_analyzer --cov-report=html

# Run only unit tests
python -m pytest tests/ -k "not property"

# Run only property-based tests
python -m pytest tests/test_properties.py
```

## Dependencies

- **textblob** (0.17.1): Natural language processing and sentiment analysis
- **hypothesis** (6.92.1): Property-based testing framework
- **pytest** (7.4.3): Testing framework
- **pytest-cov** (4.1.0): Coverage reporting

## How It Works

1. **Load**: Reads feedback from text or CSV files
2. **Analyze**: Uses TextBlob to calculate sentiment polarity scores
3. **Categorize**: Maps scores to Happy/Sad/Mild categories
4. **Display**: Shows results in a formatted table
5. **Export**: Saves results to CSV file

## Limitations

- Sentiment analysis accuracy depends on TextBlob's capabilities
- Best results with English language feedback
- Very short feedback (< 3 words) may have less accurate sentiment scores
- Processing large datasets (>10,000 entries) may take some time

## License

This project is provided as-is for educational and commercial use.

## Contributing

Contributions are welcome! Please ensure all tests pass before submitting changes.

## Support

For issues or questions, please refer to the project documentation or create an issue in the repository.