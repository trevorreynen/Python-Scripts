# Run by:  python templateUsingPath.py

# Imports
import os
import traceback
from datetime import datetime
from pathlib import Path


#! ==========<  CONFIG  >==========
# Set the path to scan (recursively?).
INPUT_PATH = Path(r'') if r'' else None

# Set the output path.
OUTPUT_PATH = Path(r'') if r'' else None

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
LOG_PATH = Path('Logs') if 'Logs' else None
LOG_NAME = 'LogFile.txt'

# Clear the console every time you run the script?
CLEAR_CONSOLE = True
if CLEAR_CONSOLE: os.system('cls' if os.name == 'nt' else 'clear')
#! ================================


def getNextLogFilePath(logFolder: Path, logFileName: str) -> Path:
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


def logMsg(logFile: Path, msg: str, printMsg=False, skipLogFile=False):
    # Optional: Print to console (default: False).
    if printMsg:
        print(msg)

    # Optional: Skip log file (default: False).
    if not skipLogFile:
        with logFile.open('a', encoding='utf-8') as log:
            log.write(msg + '\n')




def mainExample(logFile: Path, inPath: Path, outPath: Path):
    logMsg(logFile, 'Start of mainExample() function.', True)
    logMsg(logFile, 'Common script stuff here and a log or two...', True)

    if inPath:
        logMsg(logFile, f'Here is your input path: {inPath}')

    if outPath:
        logMsg(logFile, f'Here is your output path: {outPath}')

    logMsg(logFile, 'End of mainExample() function.', True)


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)

    try:
        logMsg(logFile, f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        mainExample(logFile, INPUT_PATH, OUTPUT_PATH)

        logMsg(logFile, f'\nLogs saved to "{logFile.as_posix()}".', True)
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

