# Run by:  python transferFilesByExtension.py
# Recursively finds files with given extensions in a directory and moves or copies them to a new location.
# Supports two behaviors:
#   - Flattened transfer (all files into one output folder)
#   - Preserve directory structure during transfer
# Designed for sorting files by type across messy or large folder trees.

# Imports
import os
import shutil
import traceback
from collections import defaultdict
from datetime import datetime


#! ==========<  CONFIG  >==========
# Set input path to search inside (all depths).
INPUT_PATH = r"C:\Path\To\Folder"

# Set the output path.
OUTPUT_PATH = r"C:\Path\To\Folder"

# List the file extensions to focus on. Include the dot. Case-insensitive.
EXTENSIONS = ['.wav', '.png', '.etc']

# If True, show "X/Y" progress for each file transfer (e.g., "3/40"). If False, just shows index.
SHOW_PROGRESS_NUMBERS = False

# MODE OPTIONS:
#   1 = Move files (flattened)
#   2 = Move files (preserve folder structure)
#   3 = Copy files (flattened)
#   4 = Copy files (preserve folder structure)
MODE = 4

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
LOG_PATH = 'Logs'
LOG_NAME = 'transferFilesByExtension.txt'

# Clear the console every time you run the script?
CLEAR_CONSOLE = True
if CLEAR_CONSOLE: os.system('cls' if os.name == 'nt' else 'clear')
#! ================================


def getNextLogFilePath(logFolder, logFileName):
    if logFolder:
        logPath = os.path.abspath(logFolder)
    else:
        logPath = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(logPath, exist_ok=True)
    baseName, ext = os.path.splitext(logFileName)
    logNumber = 1

    while True:
        fileName = f'{baseName}_{logNumber}{ext}'
        fullLogPath = os.path.join(logPath, fileName)

        if not os.path.exists(fullLogPath):
            return fullLogPath

        logNumber += 1


def logMsg(logFile, msg, printMsg=False, skipLogFile=False):
    # Optional: Print to console (default: False).
    if printMsg:
            print(msg)

    # Optional: Skip log file (default: False).
    if not skipLogFile:
        with open(logFile, 'a', encoding='utf-8') as log:
            log.write(msg + '\n')


def gatherFileStats(inputPath, extensions):
    """
    Count how many files exist per extension before proceeding.

    Helps generate a summary and skip empty extensions.
    """
    extensionCounts = defaultdict(int)

    for root, _, files in os.walk(inputPath):
        for file in files:
            for ext in extensions:
                if file.lower().endswith(ext.lower()):
                    extensionCounts[ext] += 1
                    break  # Prevent double counting if two extensions overlap.

    return extensionCounts


def printSummary(extensionCounts):
    logMsg(logFile, 'Extension Summary:', True)

    for ext in EXTENSIONS:
        count = extensionCounts.get(ext, 0)
        logMsg(logFile, f'  - {ext} -- Found {count} file{"s" if count != 1 else ""} with this extension in the input folder.', True)

    total = sum(extensionCounts.values())
    logMsg(logFile, '', True)

    if total == 0:
        logMsg(logFile, f'No files found with the given extension{"s" if len(EXTENSIONS) > 1 else ""}, exiting program.', True)
    else:
        action = 'moving' if MODE in (1, 2) else 'copying'
        logMsg(logFile, f'Now {action} {total} file{"s" if total != 1 else ""}...\n', True)

    return total


def transferFlat(logFile, inputPath, outputPath, extensions, mode, extensionCounts, showProgCt):
    # Transfers matching files to OUTPUT_PATH in a flat structure (no folders preserved).

    for ext in extensions:
        count = extensionCounts.get(ext, 0)

        if count == 0:
            continue

        logMsg(logFile, f'Starting Extension {ext} - {count}:', True)

        fileCounter = 0
        paddingWidth = len(str(count))

        for root, _, files in os.walk(inputPath):
            for file in files:
                if not file.lower().endswith(ext.lower()):
                    continue

                # Handle padded number for file count.
                fileCounter += 1
                paddedNum = str(fileCounter).zfill(paddingWidth)
                countOutOf = f'{paddedNum}/{count}'

                src = os.path.join(root, file)
                destination = os.path.join(outputPath, file)

                # Handle filename collisions.
                counter = 1
                base, extInner = os.path.splitext(file)

                while os.path.exists(destination):
                    # Handle duplicate filenames by appending a number (e.g., file.png → file (1).png).
                    destination = os.path.join(outputPath, f'{base} ({counter}){extInner}')
                    counter += 1

                if mode == 1:
                    # Mode 1: Move files to temp folder.
                    shutil.move(src, destination)
                    if showProgCt:
                        padding = ' ' * len(countOutOf)
                        logMsg(logFile, f'\t{countOutOf} Moved: {src}\n\t{padding} To ->   {destination}\n', True)
                    else:
                        padding = ' ' * paddingWidth
                        logMsg(logFile, f'\t{paddedNum} Moved: {src}\n\t{padding} To ->   {destination}\n', True)
                elif mode == 3:
                    # Mode 3: Copy files to temp folder.
                    shutil.copy(src, destination)
                    if showProgCt:
                        padding = ' ' * len(countOutOf)
                        logMsg(logFile, f'\t{countOutOf} Copied: {src}\n\t{padding} To ->   {destination}\n', True)
                    else:
                        padding = ' ' * paddingWidth
                        logMsg(logFile, f'\t{paddedNum} Copied: {src}\n\t{padding} To ->   {destination}\n', True)


def transferWithStructure(logFile, inputPath, outputPath, extensions, mode, extensionCounts, showProgCt):
    # Transfers matching files to OUTPUT_PATH while preserving original folder structure.

    for ext in extensions:
        count = extensionCounts.get(ext, 0)

        if count == 0:
            continue

        logMsg(logFile, f'Starting Extension {ext} - {count}:', True)

        fileCounter = 0
        paddingWidth = len(str(count))

        for root, _, files in os.walk(inputPath):
            for file in files:
                if not file.lower().endswith(ext.lower()):
                    continue

                # Handle padded number for file count.
                fileCounter += 1
                paddedNum = str(fileCounter).zfill(paddingWidth)
                countOutOf = f'{paddedNum}/{count}'

                src = os.path.join(root, file)  # Get file path.
                relativePath = os.path.relpath(root, inputPath)  # Get relative path from inputPath.
                destinationPath = os.path.join(outputPath, relativePath)  # Get path inside outputPath
                os.makedirs(destinationPath, exist_ok=True)  # Make new output path if not already.
                destination = os.path.join(destinationPath, file)  # Set the destination of the file

                if mode == 2:
                    # Mode 2: Move files to temp folder, maintaining structure.
                    shutil.move(src, destination)
                    if showProgCt:
                        padding = ' ' * len(countOutOf)
                        logMsg(logFile, f'\t{countOutOf} Moved: {src}\n\t{padding} To ->   {destination}\n', True)
                    else:
                        padding = ' ' * paddingWidth
                        logMsg(logFile, f'\t{paddedNum} Moved: {src}\n\t{padding} To ->   {destination}\n', True)
                elif mode == 4:
                    # Mode 4: Copy files to temp folder, maintaining structure.
                    shutil.copy(src, destination)
                    if showProgCt:
                        padding = ' ' * len(countOutOf)
                        logMsg(logFile, f'\t{countOutOf} Copied: {src}\n\t{padding} To ->   {destination}\n', True)
                    else:
                        padding = ' ' * paddingWidth
                        logMsg(logFile, f'\t{paddedNum} Copied: {src}\n\t{padding} To ->   {destination}\n', True)


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)

    try:
        logMsg(logFile, f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        os.makedirs(OUTPUT_PATH, exist_ok=True)
        extensionCounts = gatherFileStats(INPUT_PATH, EXTENSIONS)
        totalFiles = printSummary(extensionCounts)

        if totalFiles == 0:
            exit()

        if MODE == 1 or MODE == 3:
            # Mode 1: Move files to temp folder.
            # Mode 3: Copy files to temp folder.
            transferFlat(logFile, INPUT_PATH, OUTPUT_PATH, EXTENSIONS, MODE, extensionCounts, SHOW_PROGRESS_NUMBERS)
        elif MODE == 2 or MODE == 4:
            # Mode 2: Move files to temp folder, maintaining structure.
            # Mode 4: Copy files to temp folder, maintaining structure.
            transferWithStructure(logFile, INPUT_PATH, OUTPUT_PATH, EXTENSIONS, MODE, extensionCounts, SHOW_PROGRESS_NUMBERS)
        else:
            logMsg(logFile, 'Invalid MODE', True)

        logMsg(logFile, f'\nLogs saved to "{logFile.replace("\\", "/")}".', True)
        logMsg(logFile, f'[END] Script completed at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.', True)
    except KeyboardInterrupt:
        err = '[ERROR] Script interrupted by user (KeyboardInterrupt / CTRL+C).\n'
        trace = traceback.format_exc()
        logMsg(logFile, err + trace, True)
    except Exception:
        err = '[ERROR] Unhandled Exception:\n'
        trace = traceback.format_exc()
        logMsg(logFile, err + trace, True)
    finally:
        logMsg(logFile, f'[FINAL] Script exited at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.', True)

