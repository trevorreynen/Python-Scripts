# Run by:  python example_os_path_usage.py
# Demonstrates how to work with input and output files using the os module.
# Shows how to resolve paths, read/write files, and chain input/output operations.

# Imports
import os


#! ==========<  CONFIG  >==========
# Set up your paths (can be relative or absolute)
INPUT_PATH = os.path.join('data', 'input')
INPUT_FILE = os.path.join(INPUT_PATH, 'example.txt')  # Must be created prior to running script.

OUTPUT_PATH = os.path.join('data', 'output')
OUTPUT_FILE = os.path.join(OUTPUT_PATH, 'result.txt')

# Clear the console every time you run the script?
CLEAR_CONSOLE = True
if CLEAR_CONSOLE: os.system('cls' if os.name == 'nt' else 'clear')
#! ================================


def inputUsage(inputPath: str, inputFile: str):
    """Show how to work with an input folder and a single input file."""
    print('[INPUT USAGE]')

    # Resolve absolute paths.
    print(f'- Input Path (resolved): {os.path.abspath(inputPath).replace("\\", "/")}')
    print(f'- Input File (resolved): {os.path.abspath(inputFile).replace("\\", "/")}')

    # Create the input directory if needed (for testing/demo purposes).
    os.makedirs(inputPath, exist_ok=True)

    # Option 1: List all files inside the input folder.
    print('- Files found in input directory:')

    for entry in os.listdir(inputPath):
        fullPath = os.path.join(inputPath, entry)

        if os.path.isfile(fullPath):
            print(f'  -> {entry}')

    # Option 2: Read a single specific file.
    if os.path.exists(inputFile):
        with open(inputFile, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f'- Input file contents:\n{content}')
    else:
        print(f'- Input file not found: {inputFile.replace("\\", "/")}')


def outputUsage(outputPath: str, outputFile: str):
    """Show how to prepare and write to an output path/file."""
    print('\n[OUTPUT USAGE]')

    # Create the output folder if it doesn't exist.
    os.makedirs(outputPath, exist_ok=True)
    print(f'- Output path created: {os.path.abspath(outputPath).replace("\\", "/")}')

    # Example write.
    sampleText = 'This is a test output.'

    with open(outputFile, 'w', encoding='utf-8') as f:
        f.write(sampleText)

    print(f'- Wrote sample text to: {os.path.abspath(outputFile).replace("\\", "/")}')


def useBothInAndOut(inputPath: str, inputFile: str, outputPath: str, outputFile: str):
    """Read from input file and save to output file. Also shows resolved full path chaining."""
    print('\n[USING BOTH INPUT AND OUTPUT TOGETHER]')

    if not os.path.exists(inputFile):
        print(f'- Cannot read input file (not found): {inputFile.replace("\\", "/")}')
        return

    # Read input.
    with open(inputFile, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f'- Read content from input file.')

    # Ensure output folder exists.
    os.makedirs(outputPath, exist_ok=True)

    # Write to output.
    with open(outputFile, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'- Copied content to output file: {os.path.abspath(outputFile).replace("\\", "/")}')


if __name__ == '__main__':
    inputUsage(INPUT_PATH, INPUT_FILE)
    outputUsage(OUTPUT_PATH, OUTPUT_FILE)
    useBothInAndOut(INPUT_PATH, INPUT_FILE, OUTPUT_PATH, OUTPUT_FILE)

