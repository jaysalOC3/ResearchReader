#!/usr/bin/env python3
"""
Test script for ResearchReader

This script creates a small Markdown file and runs the research_reader.py script on it
to demonstrate its functionality and verify that it's working correctly.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Test Markdown content
TEST_MARKDOWN = """# Test Header

This is a test paragraph to demonstrate the ResearchReader functionality.

## Second Level Header

Another paragraph with some more text to show how the script handles multiple elements.
"""

def main():
    """Main function to test the research_reader.py script."""
    # Create a temporary Markdown file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(TEST_MARKDOWN)
        test_md_file = f.name
    
    # Define the output MP3 file
    output_mp3 = "test_output.mp3"
    output_wav = Path(output_mp3).with_suffix('.wav')
    
    try:
        print(f"Created test Markdown file: {test_md_file}")
        print(f"Content:\n{TEST_MARKDOWN}")
        
        # Check if research_reader.py exists
        if not os.path.exists("research_reader.py"):
            print("Error: research_reader.py not found in the current directory")
            return 1
        
        # Run the research_reader.py script
        print("\nRunning research_reader.py...")
        cmd = [sys.executable, "research_reader.py", test_md_file, output_mp3]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
            
            # Check if either the MP3 or WAV output file was created
            if os.path.exists(output_mp3):
                print(f"\nSuccess! Output MP3 file created: {output_mp3}")
                print(f"File size: {os.path.getsize(output_mp3)} bytes")
                return 0
            elif os.path.exists(output_wav):
                print(f"\nSuccess! Output WAV file created: {output_wav}")
                print(f"File size: {os.path.getsize(output_wav)} bytes")
                print(f"Note: MP3 conversion was skipped because ffmpeg is not available.")
                return 0
            else:
                print(f"\nError: Neither MP3 nor WAV output file was created")
                return 1
                
        except subprocess.CalledProcessError as e:
            print(f"Error running research_reader.py: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error: {e.stderr}")
            return 1
            
    finally:
        # Clean up the temporary file
        if os.path.exists(test_md_file):
            os.unlink(test_md_file)
            print(f"\nCleaned up test Markdown file: {test_md_file}")

if __name__ == "__main__":
    sys.exit(main())