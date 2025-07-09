# Run by:  python findEmptyFilesAndFolders.py
# Finds all Folders and Files in a given INPUT_PATH that are empty and lists them in a txt file.
# Has the option to toggle on and delete the same files/folders that are empty and move them to the recycling bin.

# Imports
import os
import traceback
from datetime import datetime
from send2trash import send2trash


#! ==========<  CONFIG  >==========
# Set the path to scan (recursively?).
INPUT_PATH = r"C:\Path\To\Folder"

#! Toggle this to delete (True) or not delete (False) empty files and/or folders.
# Does not permanently delete. Should always move files to recycling bin so you can restore just in case.
DELETE_EMPTY = False

# Set output path and file name.
# OUTPUT_PATH NOTE: Allows absolute and relative folder paths. Examples: 'Output', './Output', '../Output', or 'D:/Output/'. All are valid.
# OUTPUT_PATH NOTE: Set to None or '' to not have save file to any folder. It will just save the file to the same folder as the script.
OUTPUT_PATH = 'Output'
OUTPUT_NAME = 'EmptyFilesAndFolders.txt'

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
USE_LOG_FILE = True  #! Enable or disable log file saving entirely.
LOG_PATH = 'Logs'
LOG_NAME = 'findEmptyFilesAndFolders.txt'

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


def getNextOutputFilePath(outFolder, outFileName):
    if outFolder:
        outPath = os.path.abspath(outFolder)
    else:
        outPath = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(outPath, exist_ok=True)
    baseName, ext = os.path.splitext(outFileName)
    fileNumber = 1

    while True:
        fileName = f'{baseName}_{fileNumber}{ext}'
        fullOutPath = os.path.join(outPath, fileName)

        if not os.path.exists(fullOutPath):
            return fullOutPath

        fileNumber += 1


def findEmptyFolders(directory):
    emptyFolders = []
    for root, dirs, files in os.walk(directory, topdown=False):
        if not files and all(os.path.join(root, d) in emptyFolders for d in dirs):
            emptyFolders.append(root)

    return emptyFolders


def findEmptyFiles(directory):
    emptyFiles = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)

            if os.path.getsize(path) == 0:
                emptyFiles.append(path)

    return emptyFiles


def writeToFile(filePath, data):
    with open(filePath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(item.replace('\\', '/') + '\n')


def deleteItems(paths, label):
    for path in paths:
        try:
            send2trash(path)
            LOG(f'Deleted {label}: {path}', True)
        except (PermissionError, FileNotFoundError, OSError) as e:
            LOG(f'Error deleting {label}: {path} — {getattr(e, "strerror", str(e))}', True)


def mainScanAndDelete(inPath, outPath, outName, deleteEmpty=False):
    LOG(f'[INFO] Scanning: {inPath}', True)

    emptyFolders = findEmptyFolders(inPath)
    emptyFiles = findEmptyFiles(inPath)
    allEmpty = emptyFolders + emptyFiles

    # Determine where to save results.
    outFilePath = getNextOutputFilePath(outPath, outName)

    writeToFile(outFilePath, allEmpty)
    LOG(f'[INFO] Saved results to: {outFilePath}', True)

    # Optionally delete.
    if deleteEmpty:
        deleteItems(emptyFiles, 'file')
        deleteItems(sorted(emptyFolders, reverse=True), 'folder')



if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)
    LOG = createLogger(logFile)

    try:
        LOG(f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        mainScanAndDelete(INPUT_PATH, OUTPUT_PATH, OUTPUT_NAME, DELETE_EMPTY)

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
        err = f'[ERROR] Unhandled Exception at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}:\n'
        trace = traceback.format_exc()
        LOG(err + trace, True)
    finally:
        LOG(f'[FINAL] Script exited at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.', True)

