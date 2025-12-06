"""
Unit tests for CommandLineInterface.
"""

import sys
import tempfile
import io
import contextlib
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback_analyzer import CommandLineInterface


def test_parse_arguments_with_input_only():
    """Test parsing of required input argument."""
    # Mock sys.argv
    test_args = ['script.py', 'input.txt']
    
    with contextlib.redirect_stdout(io.StringIO()):
        # Temporarily replace sys.argv
        original_argv = sys.argv
        try:
            sys.argv = test_args
            args = CommandLineInterface.parse_arguments()
            
            assert args.input == 'input.txt'
            assert args.output == 'output.csv'  # default value
            assert args.csv_column == 'feedback'  # default value
        finally:
            sys.argv = original_argv


def test_parse_arguments_with_output():
    """Test parsing of optional output argument."""
    # Mock sys.argv
    test_args = ['script.py', 'input.txt', '-o', 'custom_output.csv']
    
    with contextlib.redirect_stdout(io.StringIO()):
        # Temporarily replace sys.argv
        original_argv = sys.argv
        try:
            sys.argv = test_args
            args = CommandLineInterface.parse_arguments()
            
            assert args.input == 'input.txt'
            assert args.output == 'custom_output.csv'
            assert args.csv_column == 'feedback'  # default value
        finally:
            sys.argv = original_argv


def test_parse_arguments_with_csv_column():
    """Test parsing of optional csv-column argument."""
    # Mock sys.argv
    test_args = ['script.py', 'input.csv', '--csv-column', 'comments']
    
    with contextlib.redirect_stdout(io.StringIO()):
        # Temporarily replace sys.argv
        original_argv = sys.argv
        try:
            sys.argv = test_args
            args = CommandLineInterface.parse_arguments()
            
            assert args.input == 'input.csv'
            assert args.output == 'output.csv'  # default value
            assert args.csv_column == 'comments'
        finally:
            sys.argv = original_argv


def test_display_usage():
    """Test display of usage when no arguments provided."""
    output = io.StringIO()
    
    with contextlib.redirect_stdout(output):
        CommandLineInterface.display_usage()
    
    usage_text = output.getvalue()
    
    # Verify usage text contains key information
    assert 'Customer Feedback Analyzer' in usage_text
    assert 'input' in usage_text
    assert 'output' in usage_text


def test_exit_code_success():
    """Test exit code 0 for successful execution."""
    # Create temporary input file with valid feedback
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        f.write("This is great!\n")
        f.write("I love this product.\n")
        input_path = f.name
    
    # Create temporary output file path
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as f:
        output_path = f.name
    
    try:
        # Create args namespace
        args = argparse.Namespace(
            input=input_path,
            output=output_path,
            csv_column='feedback'
        )
        
        # Run the CLI with suppressed output
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = CommandLineInterface.run(args)
        
        # Verify exit code is 0 for success
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
    
    finally:
        # Clean up
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def test_exit_code_file_not_found():
    """Test exit code 1 for file not found error."""
    # Create args namespace with non-existent file
    args = argparse.Namespace(
        input='nonexistent_file_12345.txt',
        output='output.csv',
        csv_column='feedback'
    )
    
    # Run the CLI with suppressed output
    with contextlib.redirect_stdout(io.StringIO()):
        exit_code = CommandLineInterface.run(args)
    
    # Verify exit code is 1 for file not found
    assert exit_code == 1, f"Expected exit code 1 for file not found, got {exit_code}"


def test_exit_code_csv_column_not_found():
    """Test exit code 3 for invalid CSV format (missing column)."""
    import csv
    
    # Create temporary CSV file without the expected column
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['wrong_column'])
        writer.writeheader()
        writer.writerow({'wrong_column': 'some data'})
        input_path = f.name
    
    try:
        # Create args namespace
        args = argparse.Namespace(
            input=input_path,
            output='output.csv',
            csv_column='feedback'
        )
        
        # Run the CLI with suppressed output
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = CommandLineInterface.run(args)
        
        # Verify exit code is 3 for invalid format
        assert exit_code == 3, f"Expected exit code 3 for invalid format, got {exit_code}"
    
    finally:
        # Clean up
        Path(input_path).unlink(missing_ok=True)


def test_empty_input_file():
    """Test handling of empty input file (should return 0 with warning)."""
    # Create temporary empty input file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        input_path = f.name
    
    # Create temporary output file path
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as f:
        output_path = f.name
    
    try:
        # Create args namespace
        args = argparse.Namespace(
            input=input_path,
            output=output_path,
            csv_column='feedback'
        )
        
        # Run the CLI and capture output
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exit_code = CommandLineInterface.run(args)
        
        # Verify exit code is 0 (graceful handling)
        assert exit_code == 0, f"Expected exit code 0 for empty file, got {exit_code}"
        
        # Verify warning message was displayed
        output_text = output.getvalue()
        assert 'Warning' in output_text or 'No valid feedback' in output_text
    
    finally:
        # Clean up
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)


def test_csv_input_processing():
    """Test processing of CSV input file."""
    import csv
    
    # Create temporary CSV file with feedback
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['feedback'])
        writer.writeheader()
        writer.writerow({'feedback': 'This is excellent!'})
        writer.writerow({'feedback': 'This is terrible!'})
        input_path = f.name
    
    # Create temporary output file path
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as f:
        output_path = f.name
    
    try:
        # Create args namespace
        args = argparse.Namespace(
            input=input_path,
            output=output_path,
            csv_column='feedback'
        )
        
        # Run the CLI with suppressed output
        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = CommandLineInterface.run(args)
        
        # Verify exit code is 0 for success
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
        
        # Verify output file was created
        assert Path(output_path).exists(), "Output file should be created"
    
    finally:
        # Clean up
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)
