# Run by:  python listUniqueFileExtensions.py
# Recursively scans all files in a directory and logs each unique file extension it finds.
# Helps identify which file types are present in a large or unknown folder structure.
# Especially useful before filtering, transferring, or bulk-processing files by type (see transferFilesByExtension.py).

# Imports
import os
import traceback
from datetime import datetime


#! ==========<  CONFIG  >==========
# Root path to search recursively for files (all subfolders will be included).
INPUT_PATH = r"C:\Path\To\Folder"

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
LOG_PATH = 'Logs'
LOG_NAME = 'listUniqueFileExtensions.txt'

# Clear the console every time you run the script?
CLEAR_CONSOLE = True
if CLEAR_CONSOLE: os.system('cls' if os.name == 'nt' else 'clear')
#! ================================


def getNextLogFilePath(logFolder, logFileName):
    logPath = os.path.abspath(logFolder) if logFolder else os.path.dirname(os.path.abspath(__file__))

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


def findAllExt(logFile, inPath):
    # Set to store unique extensions.
    extensions = set()

    # Walk through the folder.
    for root, _, files in os.walk(inPath):
        for file in files:
            ext = os.path.splitext(file)[1].lower()

            if ext:  # Skip files with no extension.
                extensions.add(ext)

    logMsg(logFile, 'Unique file extensions found:', True)

    # Sort alphabetically for easier viewing and comparison.
    for ext in sorted(extensions):
        logMsg(logFile, f"\'{ext}\',", True)


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)

    try:
        logMsg(logFile, f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        findAllExt(logFile, INPUT_PATH)

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

