# Run by:  python findStringMatchesInsideFiles.py
# Searches through text-based files with specific extensions for one or more exact substring matches.
# Operates line-by-line (no regex or multiline support) and logs any matches with line numbers and context.
# Ideal for quickly locating hardcoded values, IDs, or phrases across config and data files.

# Imports
import os
import traceback
from datetime import datetime


#! ==========<  CONFIG  >==========
# Set the paths to scan.
SEARCH_PATHS = [
    r"C:\Path\To\Folder",
    r"C:\Path\To\Folder",
    r"C:\Path\To\Folder",
]

#@ Flag to set recursive search inside SEARCH_PATHS to search deeper into folders or not for specific VALID_EXTENSIONS files.
RECURSIVE_SEARCH = True


#@ The files (by extension) we are searching inside.
VALID_EXTENSIONS = ['.json', '.ini', '.csv', '.xml']


#@ Set the specific substrings to find inside each file.
# NOTE: No regex, no multi-line scanning. Each line is compared as-is (whitespace sensitive).
SUBSTRINGS = ['string 1', 'string 2', 'string 3']


# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
USE_LOG_FILE = True  #! Enable or disable log file saving entirely.
LOG_PATH = 'Logs'
LOG_NAME = 'findStringMatchesInsideFiles.txt'

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


def searchFile(filePath, subStr):
    try:
        with open(filePath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        # Read each line and search for any of the target strings (case-insensitive exact matches).
        for i, line in enumerate(lines):
            for target in subStr:
                if target in line:
                    LOG(f'\n[FOUND] Str: {target} - Line: {i+1}  ||  File: {filePath.replace("\\", "/")}\n\n', True)

                    # Write surrounding context.
                    start = max(0, i - 4)
                    end = min(len(lines), i + 5)

                    for j in range(start, end):
                        prefix = '>> ' if j == i else '   '
                        LOG(f'{prefix}Line {j+1:04}: {lines[j]}', True)

                    LOG('\n' + ('=' * 80), True)
    except Exception as e:
        LOG(f'[ERROR] Could not read file: {filePath.replace("\\", "/")}  ||  Reason: {str(e)}', True)


def scanPaths(searchPath, validExtensions, subStrings, recursiveSearch=True):
    for basePath in searchPath:
        if not os.path.exists(basePath):
            LOG(f'[WARNING] Path does not exist: {basePath}', True)
            continue

        for root, dirs, files in os.walk(basePath):
            for file in files:
                if any(file.lower().endswith(ext) for ext in validExtensions):
                    fullPath = os.path.join(root, file)
                    searchFile(fullPath, subStrings)

            if not recursiveSearch:
                break  # Only process top-level if not recursive.


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)
    LOG = createLogger(logFile)

    try:
        LOG(f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        scanPaths(SEARCH_PATHS, VALID_EXTENSIONS, SUBSTRINGS, RECURSIVE_SEARCH)

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

