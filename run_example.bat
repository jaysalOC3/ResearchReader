@echo off
REM Run ResearchReader on the example file

echo Running ResearchReader on ResearchExample.md...
python research_reader.py ResearchExample.md example_output.mp3

if %ERRORLEVEL% EQU 0 (
    echo Success! Output saved to example_output.mp3
) else (
    echo Error running ResearchReader. Please check the output above for details.
)

pause