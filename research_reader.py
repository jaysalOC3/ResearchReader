#!/usr/bin/env python3
"""
ResearchReader - Convert Markdown research files to optimized speech audio

This script reads a Markdown file, parses it to identify headers and paragraphs,
and generates optimized speech audio with appropriate pauses and speed variations
using the Kokoro-82M text-to-speech model.
"""

import argparse
import os
import tempfile
import subprocess
import requests
from bs4 import BeautifulSoup
import markdown
import shutil
import time
import sys
import wave
import struct
from pathlib import Path

# Constants
KOKORO_API_URL = "http://localhost:8880/v1/audio/speech"
DEFAULT_VOICE = "af_heart"
HEADER_SPEED = 0.8
PARAGRAPH_SPEED = 1.0
SAMPLE_RATE = 24000  # 24 kHz for Kokoro-82M

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert Markdown research to optimized speech audio")
    parser.add_argument("input_file", help="Path to the input Markdown file")
    parser.add_argument("output_file", help="Path to the output MP3 file")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Voice to use (default: {DEFAULT_VOICE})")
    parser.add_argument("--header-speed", type=float, default=HEADER_SPEED, 
                        help=f"Speech speed for headers (default: {HEADER_SPEED})")
    parser.add_argument("--paragraph-speed", type=float, default=PARAGRAPH_SPEED, 
                        help=f"Speech speed for paragraphs (default: {PARAGRAPH_SPEED})")
    parser.add_argument("--pause-duration", type=float, default=1.0, 
                        help="Duration of pause after headers in seconds (default: 1.0)")
    return parser.parse_args()

def read_markdown_file(file_path):
    """Read the content of a Markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        sys.exit(1)

def convert_markdown_to_html(markdown_content):
    """Convert Markdown content to HTML."""
    return markdown.markdown(markdown_content)

def parse_html(html_content):
    """Parse HTML to extract headers and paragraphs."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all headers (h1, h2, h3, etc.) and paragraphs
    elements = []
    
    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
        # Skip empty elements
        if not tag.get_text().strip():
            continue
            
        element_type = 'header' if tag.name.startswith('h') else 'paragraph'
        elements.append({
            'type': element_type,
            'text': tag.get_text().strip()
        })
    
    return elements

def generate_speech(text, output_file, speed, voice):
    """Generate speech using the Kokoro-82M API."""
    try:
        payload = {
            "model": "kokoro",
            "input": text,
            "voice": voice,
            "response_format": "wav",
            "speed": speed
        }
        
        response = requests.post(KOKORO_API_URL, json=payload)
        
        if response.status_code != 200:
            print(f"Error generating speech: {response.status_code} - {response.text}")
            return False
        
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"Error calling Kokoro API: {e}")
        return False

def is_ffmpeg_available():
    """Check if ffmpeg is available."""
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def generate_silence_python(output_file, duration):
    """Generate a silent WAV file using Python's wave module."""
    try:
        # Calculate the number of frames
        n_frames = int(SAMPLE_RATE * duration)
        
        # Create a silent audio file using wave module
        with wave.open(output_file, 'w') as wav_file:
            wav_file.setparams((1, 2, SAMPLE_RATE, n_frames, 'NONE', 'not compressed'))
            
            # Generate silent frames (all zeros)
            silent_frames = struct.pack('h' * n_frames, *([0] * n_frames))
            wav_file.writeframes(silent_frames)
        
        return True
    except Exception as e:
        print(f"Error generating silence with Python: {e}")
        return False

def generate_silence_ffmpeg(output_file, duration):
    """Generate a silent WAV file using ffmpeg."""
    try:
        # Create a silent audio file using ffmpeg
        cmd = [
            "ffmpeg", "-f", "lavfi", "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono", 
            "-t", str(duration), "-q:a", "0", "-c:a", "pcm_s16le", 
            "-y", output_file
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        print(f"Error generating silence with ffmpeg: {e}")
        return False

def generate_silence(output_file, duration):
    """Generate a silent WAV file using ffmpeg or Python's wave module as fallback."""
    if is_ffmpeg_available():
        print("Using ffmpeg to generate silence")
        return generate_silence_ffmpeg(output_file, duration)
    else:
        print("ffmpeg not available, using Python to generate silence")
        return generate_silence_python(output_file, duration)

def concatenate_audio_files_python(audio_files, output_file):
    """Concatenate multiple WAV files into a single WAV file using Python's wave module."""
    try:
        # Get parameters from the first file
        with wave.open(audio_files[0], 'rb') as first_file:
            params = first_file.getparams()
        
        # Create output file with the same parameters
        with wave.open(output_file, 'wb') as output:
            output.setparams(params)
            
            # Append each file's frames to the output
            for audio_file in audio_files:
                with wave.open(audio_file, 'rb') as wav_file:
                    output.writeframes(wav_file.readframes(wav_file.getnframes()))
        
        return True
    except Exception as e:
        print(f"Error concatenating audio files with Python: {e}")
        return False

def concatenate_audio_files_ffmpeg(audio_files, output_file):
    """Concatenate multiple WAV files into a single WAV file using ffmpeg."""
    try:
        # Create a temporary file with the list of files to concatenate
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for audio_file in audio_files:
                f.write(f"file '{os.path.abspath(audio_file)}'\n")
            concat_list_file = f.name
        
        # Concatenate the files using ffmpeg
        cmd = [
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list_file,
            "-c", "copy", "-y", output_file
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Remove the temporary file
        os.unlink(concat_list_file)
        
        return True
    except Exception as e:
        print(f"Error concatenating audio files with ffmpeg: {e}")
        return False

def concatenate_audio_files(audio_files, output_file):
    """Concatenate multiple WAV files into a single WAV file using ffmpeg or Python's wave module as fallback."""
    if is_ffmpeg_available():
        print("Using ffmpeg to concatenate audio files")
        return concatenate_audio_files_ffmpeg(audio_files, output_file)
    else:
        print("ffmpeg not available, using Python to concatenate audio files")
        return concatenate_audio_files_python(audio_files, output_file)

def convert_wav_to_mp3(wav_file, mp3_file):
    """Convert a WAV file to MP3 using ffmpeg."""
    if not is_ffmpeg_available():
        print("Warning: ffmpeg is not available, cannot convert to MP3")
        print(f"The output will remain as a WAV file: {wav_file}")
        # Copy the WAV file to the output path but with .wav extension
        mp3_path = Path(mp3_file)
        wav_output = mp3_path.with_suffix('.wav')
        shutil.copy(wav_file, wav_output)
        print(f"Copied WAV file to: {wav_output}")
        return True
    
    try:
        cmd = [
            "ffmpeg", "-i", wav_file, "-codec:a", "libmp3lame", 
            "-qscale:a", "2", "-y", mp3_file
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        print(f"Error converting WAV to MP3: {e}")
        return False

def main():
    """Main function to process the Markdown file and generate speech."""
    args = parse_args()
    
    print(f"Reading Markdown file: {args.input_file}")
    markdown_content = read_markdown_file(args.input_file)
    
    print("Converting Markdown to HTML")
    html_content = convert_markdown_to_html(markdown_content)
    
    print("Parsing HTML to extract headers and paragraphs")
    elements = parse_html(html_content)
    
    # Create a temporary directory for audio files
    temp_dir = tempfile.mkdtemp()
    audio_files = []
    
    try:
        print("Generating speech for each element")
        
        # Generate a silent pause file
        silence_file = os.path.join(temp_dir, "silence.wav")
        if not generate_silence(silence_file, args.pause_duration):
            print("Failed to generate silence file")
            sys.exit(1)
        
        for i, element in enumerate(elements):
            element_type = element['type']
            text = element['text']
            
            print(f"Processing {element_type}: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Set speed based on element type
            speed = args.header_speed if element_type == 'header' else args.paragraph_speed
            
            # Generate speech for the element
            audio_file = os.path.join(temp_dir, f"element_{i:04d}.wav")
            if not generate_speech(text, audio_file, speed, args.voice):
                print(f"Failed to generate speech for element {i}")
                continue
            
            audio_files.append(audio_file)
            
            # Add a pause after headers
            if element_type == 'header':
                audio_files.append(silence_file)
        
        if not audio_files:
            print("No audio files were generated")
            sys.exit(1)
        
        # Concatenate all audio files
        print("Concatenating audio files")
        concatenated_wav = os.path.join(temp_dir, "concatenated.wav")
        if not concatenate_audio_files(audio_files, concatenated_wav):
            print("Failed to concatenate audio files")
            sys.exit(1)
        
        # Convert to MP3
        print(f"Converting to MP3: {args.output_file}")
        if not convert_wav_to_mp3(concatenated_wav, args.output_file):
            print("Failed to convert to MP3")
            sys.exit(1)
        
        print(f"Successfully created output file: {args.output_file}")
        
    finally:
        # Clean up temporary files
        print("Cleaning up temporary files")
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()
