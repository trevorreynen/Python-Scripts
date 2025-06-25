# Run by:  python example_pathlib_path_usage.py
# Demonstrates file operations using pathlib.Path instead of os.path.
# Shows how to create folders, resolve paths, and read/write content using modern Python idioms.

# Imports
import os  # Not used by anything other than clear console.
from pathlib import Path


#! ==========<  CONFIG  >==========
# Set up your paths (can be relative or absolute)
INPUT_PATH = Path('data') / 'input'
INPUT_FILE = INPUT_PATH / 'example.txt'  # Must be created prior to running script.

OUTPUT_PATH = Path('data') / 'output'
OUTPUT_FILE = OUTPUT_PATH / 'result.txt'

# Clear the console every time you run the script?
CLEAR_CONSOLE = True
if CLEAR_CONSOLE: os.system('cls' if os.name == 'nt' else 'clear')
#! ================================


def inputUsage(inputPath: Path, inputFile: Path):
    """Show how to work with an input folder and a single input file."""
    print('[INPUT USAGE]')

    # Resolve paths to absolute.
    print(f'- Input Path (resolved): {str(inputPath.resolve()).replace("\\", "/")}')
    print(f'- Input File (resolved): {str(inputFile.resolve()).replace("\\", "/")}')

    # Create the input directory if needed (for testing/demo purposes).
    inputPath.mkdir(parents=True, exist_ok=True)

    # Option 1: List all files inside the input folder.
    print('- Files found in input directory:')

    for file in inputPath.iterdir():
        if file.is_file():
            print(f'  -> {file.name}')

    # Option 2: Read a single specific file.
    if inputFile.exists():
        content = inputFile.read_text(encoding='utf-8')
        print(f'- Input file contents:\n{content}')
    else:
        print(f'- Input file not found: {str(inputFile).replace("\\", "/")}')


def outputUsage(outputPath: Path, outputFile: Path):
    """Show how to prepare and write to an output path/file."""
    print('\n[OUTPUT USAGE]')

    # Create the output folder if it doesn't exist.
    outputPath.mkdir(parents=True, exist_ok=True)
    print(f'- Output path created: {str(outputPath.resolve()).replace("\\", "/")}')

    # Example write.
    sampleText = 'This is a test output.'
    outputFile.write_text(sampleText, encoding='utf-8')
    print(f'- Wrote sample text to: {str(outputFile.resolve()).replace("\\", "/")}')


def useBothInAndOut(inputPath: Path, inputFile: Path, outputPath: Path, outputFile: Path):
    """Read from input file and save to output file. Also shows resolved full path chaining."""
    print('\n[USING BOTH INPUT AND OUTPUT TOGETHER]')

    if not inputFile.exists():
        print(f'- Cannot read input file (not found): {str(inputFile).replace("\\", "/")}')
        return

    # Read input.
    content = inputFile.read_text(encoding='utf-8')
    print(f'- Read content from input file.')

    # Ensure output folder exists.
    outputPath.mkdir(parents=True, exist_ok=True)

    # Write to output.
    outputFile.write_text(content, encoding='utf-8')
    print(f'- Copied content to output file: {str(outputFile.resolve()).replace("\\", "/")}')


if __name__ == '__main__':
    inputUsage(INPUT_PATH, INPUT_FILE)
    outputUsage(OUTPUT_PATH, OUTPUT_FILE)
    useBothInAndOut(INPUT_PATH, INPUT_FILE, OUTPUT_PATH, OUTPUT_FILE)

