# Run by:  python autoSortFilesToMatchingFolders.py
# Moves files from the top level of a folder into subfolders whose names match the file name prefix.
# The match is based on everything before the last underscore (_) in the file name.
# Useful when files are named after categories that have corresponding folders.
''' Example:
Given input path is:
    INPUT_PATH/
    ├── Unit_Knight/
    │   └── (currently empty)
    ├── Unit_Archer/
    │   └── (currently empty)
    ├── Unit_Knight_01.wav
    ├── Unit_Knight_02.wav
    ├── Unit_Archer_01.wav
    └── Unit_Catapult_01.wav  <-- no matching folder

The script would move:
    Moved: Unit_Knight_01.wav → Unit_Knight/
    Moved: Unit_Knight_02.wav → Unit_Knight/
    Moved: Unit_Archer_01.wav → Unit_Archer/
'''

# Imports
import os
import shutil
import traceback
from datetime import datetime


#! ==========<  CONFIG  >==========
# All files at the top level of this folder will be matched to subfolders (by prefix) and moved accordingly.
INPUT_PATH = r"C:\Path\To\Folder"

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
USE_LOG_FILE = True  #! Enable or disable log file saving entirely.
LOG_PATH = 'Logs'
LOG_NAME = 'autoSortFilesToMatchingFolders.txt'

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


def main(inPath):
    # Get all folder names once.
    folderNames = set(f for f in os.listdir(inPath) if os.path.isdir(os.path.join(inPath, f)))

    # Loop through all files in the root of inPath
    for item in os.listdir(inPath):
        itemPath = os.path.join(inPath, item)

        if os.path.isfile(itemPath) and '_' in item:
            # Extract folder prefix based on everything before the last underscore in the filename.
            prefix = '_'.join(item.split('_')[:-1])

            if prefix in folderNames:
                try:
                    shutil.move(itemPath, os.path.join(inPath, prefix, item))
                    LOG(f'Moved: {item} → {prefix}/', True)
                except Exception as e:
                    LOG(f'Error moving {item}: {e}', True)


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)
    LOG = createLogger(logFile)

    try:
        LOG(f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        main(logFile, INPUT_PATH)

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

