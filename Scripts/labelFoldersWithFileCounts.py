# Run by:  python labelFoldersWithFileCounts.py
# Renames each top-level folder inside the input path by appending a summary of its contents:
# - Number of files it contains (including subdirectories)
# - Total size on disk (true allocated size, not just file sizes)
# Useful for visually comparing folder content sizes directly from the filesystem.

# Imports
import ctypes
import os
import re
import traceback
from datetime import datetime


#! ==========<  CONFIG  >==========
# Set path to input path root.
INPUT_PATH = r"C:\Path\To\Folder"

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
LOG_PATH = 'Logs'
LOG_NAME = 'labelFoldersWithFileCounts.txt'

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
        print(logFile, msg)

    # Optional: Skip log file (default: False).
    if not skipLogFile:
        with open(logFile, 'a', encoding='utf-8') as log:
            log.write(msg + '\n')


def formatFileSize(bytes):
    if bytes < 1024:
        return f'{bytes} B'
    elif bytes < 1024 ** 2:
        return f'{bytes / 1024:.2f} KB'
    elif bytes < 1024 ** 3:
        return f'{bytes / 1024 ** 2:.2f} MB'
    else:
        return f'{bytes / 1024 ** 3:.2f} GB'


def formatNumber(n):
    return '{:,}'.format(n)


def folderAlreadyLabeled(name):
    return re.search(r'\(\d{1,3}(,\d{3})* Files, .+\)$', name)


def getClusterSize(path):
    sectorsPerCluster = ctypes.c_ulong()
    bytesPerSector = ctypes.c_ulong()
    rootPath = os.path.splitdrive(path)[0] + '\\'

    res = ctypes.windll.kernel32.GetDiskFreeSpaceW(
        ctypes.c_wchar_p(rootPath),
        ctypes.byref(sectorsPerCluster),
        ctypes.byref(bytesPerSector),
        None, None
    )

    if res == 0:
        raise ctypes.WinError()

    return sectorsPerCluster.value * bytesPerSector.value


def getTrueSizeOnDisk(filePath, clusterSize):
    actualSize = os.path.getsize(filePath)

    return ((actualSize + clusterSize - 1) // clusterSize) * clusterSize


def getFolderInfoTrueDiskUsage(logFile, path):
    fileCount = 0
    totalAllocated = 0
    clusterSize = getClusterSize(path)

    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                fp = os.path.join(root, f)
                totalAllocated += getTrueSizeOnDisk(fp, clusterSize)
                fileCount += 1
            except Exception as e:
                logMsg(logFile, f'Error reading file: {fp} → {e}', True)

    return fileCount, totalAllocated


def main(logFile, inPath):
    logMsg(logFile, f'\nRenaming folders in: {inPath}\n', True)

    # Accumulate true on-disk size (accounts for filesystem block usage, not just file byte size).
    for folder in os.listdir(inPath):
        folderPath = os.path.join(inPath, folder)

        if os.path.isdir(folderPath) and not folderAlreadyLabeled(folder):
            fileCount, totalBytes = getFolderInfoTrueDiskUsage(folderPath)
            fileCountStr = formatNumber(fileCount)
            sizeStr = formatFileSize(totalBytes)

            newName = f'{folder} ({fileCountStr} Files, {sizeStr})'
            newPath = os.path.join(inPath, newName)

            try:
                # Final folder name format: OriginalName (3 Files, 2.71 MB).
                os.rename(folderPath, newPath)
                logMsg(logFile, f'Renamed: {folder} → {newName}', True)
            except Exception as e:
                logMsg(logFile, f'Failed to rename {folder}: {e}', True)


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)

    try:
        logMsg(logFile, f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        main(logFile, INPUT_PATH)

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

