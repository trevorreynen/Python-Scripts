# Run by:  python combinationMatrix.py

# Imports
import csv
import itertools
import os
import traceback
from datetime import datetime


#! ==========<  CONFIG  >==========
# Set the combinations to create. Can add as many as you want, with any name for the keys.
COMBINATION_SLOTS = {
    'Head': ['Light', 'Medium', 'Heavy'],
    'Chest': ['Light', 'Medium', 'Heavy'],
    'Hands': ['Light', 'Medium', 'Heavy'],
    'Legs': ['Light', 'Medium', 'Heavy'],
    'Feet': ['Light', 'Medium', 'Heavy'],
    'Shield': ['', 'Round Shield', 'Kite Shield', 'Tower Shield'],

    # Add as many slots as you want...
}


# Set the output path.
OUTPUT_PATH = r"Output"

# Set the output file name and type.
# '.txt' = Each combination on a line, space-separated
# '.csv' = Each combination in columns (with headers)
OUTPUT_FILE_NAME = 'combinations'
OUTPUT_FILE_TYPE = '.csv'  # Options: '.txt', '.csv', 'txt', 'csv'


# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
USE_LOG_FILE = True  #! Enable or disable log file saving entirely.
LOG_PATH = 'Logs'
LOG_NAME = 'combinationMatrix.txt'

# Clear the console every time you run the script?
CLEAR_CONSOLE = True
if CLEAR_CONSOLE: os.system('cls' if os.name == 'nt' else 'clear')

# Enables global use of LOG() without needing to pass createLogger() or logFile between functions.
LOG = lambda *args, **kwargs: None
#! ================================


def getNextLogFilePath(logFolder, logFileName):
    # Skip creating log path if logging is disabled.
    if not USE_LOG_FILE:
        return None

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


def logMsg(msg, printMsg=False, logFile=None, skipLogFile=False):
    # Optional: Print to console (default: False).
    if printMsg:
        print(msg)

    # Optional: Skip log file (default: False).
    if USE_LOG_FILE and not skipLogFile and logFile:
        with open(logFile, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')


def createLogger(logFile):
    """
    Returns a logging function with the given log file pre-attached.
    This allows using LOG(msg) globally without passing the log file into every call.
    Respects USE_LOG_FILE automatically.
    """
    return lambda msg, printMsg=False, skipLogFile=False: logMsg(msg, printMsg, logFile, skipLogFile)


def generateCombinations(slots, outPath, outFileName, outFileType):
    headers = list(slots.keys())
    slotValues = list(slots.values())

    # Validate that all slot values are non-empty lists
    for key, values in slots.items():
        if not values:
            LOG(f'[WARNING] Slot "{key}" has no values. Skipping generation.')
            return

    combinations = list(itertools.product(*slotValues))

    # Normalize extension
    if outFileType.startswith('.'):
        ext = outFileType[1:].lower()
    else:
        ext = outFileType.lower()

    # Ensure output folder exists if set.
    if outPath:
        outputDir = os.path.abspath(outPath)
    else:
        outputDir = os.path.dirname(os.path.abspath(__file__))

    # Ensure the output directory exists
    os.makedirs(outputDir, exist_ok=True)
    outputFilePath = os.path.join(outputDir, f'{outFileName}.{ext}')

    try:
        if ext == 'txt':
            with open(outputFilePath, 'w', encoding='utf-8') as file:
                for combo in combinations:
                    file.write(' '.join(combo) + '\n')
        elif ext == 'csv':
            with open(outputFilePath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(combinations)
        else:
            LOG(f'[ERROR] Unsupported file type: {outFileType}', True)
            return

        LOG(f'[SUCCESS] Generated {len(combinations)} combinations and saved to {outputFilePath}', True)

    except Exception as e:
        LOG(f'[ERROR] Failed to generate combinations: {e}', True)


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)
    LOG = createLogger(logFile)

    try:
        LOG(f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        generateCombinations(COMBINATION_SLOTS, OUTPUT_PATH, OUTPUT_FILE_NAME, OUTPUT_FILE_TYPE)

        if USE_LOG_FILE:
            LOG(f'\nLogs saved to "{logFile.replace("\\", "/")}"', True)
            LOG(f'[END] Script completed at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.', True)
        else:
            LOG(f'\n[END] Script completed at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.', True)
    except KeyboardInterrupt:
        err = '[ERROR] Script interrupted by user (KeyboardInterrupt / CTRL+C).\n'
        trace = traceback.format_exc()
        LOG(err + trace, True)
    except Exception:
        err = '[ERROR] Unhandled Exception:\n'
        trace = traceback.format_exc()
        LOG(err + trace, True)
    finally:
        LOG(f'[FINAL] Script exited at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.', True)

