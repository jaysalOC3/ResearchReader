# ResearchReader Usage Guide

ResearchReader is a Python script that converts Markdown research files into optimized speech audio using the Kokoro-82M text-to-speech model.
https://github.com/remsky/Kokoro-FastAPI
It enhances the listening experience by adding pauses after headers and varying speech speed for better focus.

## Prerequisites

Before using ResearchReader, ensure you have the following:

1. Python 3.6 or higher installed
2. The Kokoro-82M FastAPI wrapper running locally on port 8880
3. ffmpeg installed on your system (for audio processing)
4. Required Python packages installed (see Installation section)

## Installation

1. Clone or download this repository
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with the following command:

```bash
python research_reader.py input_file.md output_file.mp3
```

### Command Line Arguments

- `input_file`: Path to the input Markdown file
- `output_file`: Path to the output MP3 file
- `--voice`: Voice to use (default: "af_bella")
- `--header-speed`: Speech speed for headers (default: 0.8)
- `--paragraph-speed`: Speech speed for paragraphs (default: 1.0)
- `--pause-duration`: Duration of pause after headers in seconds (default: 1.0)

### Example

```bash
python research_reader.py ResearchExample.md output.mp3
```

This will:
1. Read the Markdown file `ResearchExample.md`
2. Convert it to HTML and parse it to identify headers and paragraphs
3. Generate speech for headers at a slower speed (0.8)
4. Add a 1-second pause after each header
5. Generate speech for paragraphs at normal speed (1.0)
6. Concatenate all audio files and convert to MP3
7. Save the result as `output.mp3`

## Customization

You can customize the speech generation by adjusting the command line arguments:

```bash
python research_reader.py ResearchExample.md output.mp3 --voice "en_james" --header-speed 0.7 --paragraph-speed 0.9 --pause-duration 1.5
```

This will use the "en_james" voice, set header speed to 0.7, paragraph speed to 0.9, and add a 1.5-second pause after headers.

## Troubleshooting

If you encounter issues:

1. Ensure the Kokoro-82M FastAPI wrapper is running on port 8880
2. Check that ffmpeg is installed and accessible in your PATH
3. Verify that the input Markdown file exists and is readable
4. Make sure you have write permissions for the output file location
