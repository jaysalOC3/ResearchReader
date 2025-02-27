#!/bin/bash
# Run ResearchReader on the example file

echo "Running ResearchReader on ResearchExample.md..."
python3 research_reader.py ResearchExample.md example_output.mp3

if [ $? -eq 0 ]; then
    echo "Success! Output saved to example_output.mp3"
else
    echo "Error running ResearchReader. Please check the output above for details."
fi