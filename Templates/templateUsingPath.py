# Run by:  python templateUsingPath.py

# Imports
import os
import traceback
from datetime import datetime
from pathlib import Path


#! ==========<  CONFIG  >==========
# Set the path to scan (recursively?).
INPUT_PATH = Path(r"C:\Path\To\Folder") if r'' else None

# Set the output path.
OUTPUT_PATH = Path(r"C:\Path\To\Folder") if r'' else None

#! Enable or disable log file saving entirely.
USE_LOG_FILE = True

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
LOG_PATH = Path('Logs') if 'Logs' else None
LOG_NAME = 'LogFile.txt'

# Clear the console every time you run the script?
CLEAR_CONSOLE = True
if CLEAR_CONSOLE: os.system('cls' if os.name == 'nt' else 'clear')

# Enables global use of LOG() without needing to pass createLogger() or logFile between functions.
LOG = lambda *args, **kwargs: None
#! ================================


def getNextLogFilePath(logFolder: Path, logFileName: str) -> Path:
    # Skip creating log path if logging is disabled.
    if not USE_LOG_FILE:
        return None

    if logFolder:
        logPath = logFolder.resolve()
    else:
        logPath = Path(__file__).resolve().parent

    logPath.mkdir(parents=True, exist_ok=True)
    baseName = Path(logFileName).stem
    ext = Path(logFileName).suffix
    logNumber = 1

    while True:
        fileName = f'{baseName}_{logNumber}{ext}'
        fullLogPath = logPath / fileName

        if not fullLogPath.exists():
            return fullLogPath

        logNumber += 1


def logMsg(msg: str, printMsg=False, logFile: Path | None = None, skipLogFile=False):
    # Optional: Print to console (default: False).
    if printMsg:
        print(msg)

    # Optional: Skip log file (default: False).
    if USE_LOG_FILE and not skipLogFile and logFile:
        with logFile.open('a', encoding='utf-8') as log:
            log.write(msg + '\n')


def createLogger(logFile: Path | None):
    """
    Returns a logging function with the given log file pre-attached.
    This allows using LOG(msg) globally without passing the log file into every call.
    Respects USE_LOG_FILE automatically.
    """
    return lambda msg, printMsg=False, skipLogFile=False: logMsg(msg, printMsg, logFile, skipLogFile)




def mainExample(inPath: Path | None, outPath: Path | None):
    LOG('Start of mainExample() function.', True)
    LOG('Common script stuff here and a log or two...', True)

    LOG('This will only print to the console but not the log file (if using one)', True, True)
    LOG('This will only print to the log file (if using one) but not console', False)

    if inPath:
        LOG(f'Here is your input path: {inPath}')

    if outPath:
        LOG(f'Here is your output path: {outPath}')

    LOG('End of mainExample() function.', True)


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)
    LOG = createLogger(logFile)

    try:
        LOG(f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        # Run the main script function.
        mainExample(INPUT_PATH, OUTPUT_PATH)

        if USE_LOG_FILE:
            LOG(f'\nLogs saved to "{logFile.as_posix()}"', True)
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

