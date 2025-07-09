# Run by:  python ConvertAll_AVI_to_MP4_InAFolder.py
#! Requires ffmpeg.
# Converts all .avi video files in a folder (recursively) to .mp4 using ffmpeg.
# Supports deletion or relocation of original files and logs conversion results.
# Outputs a dynamically updated console display and summary log.

# Imports
import os
import shutil
import subprocess
import traceback
from datetime import datetime


#! ==========<  CONFIG  >==========
# Folder to scan recursively for .avi files.
#INPUT_PATH = r"C:\Path\To\Folder"
INPUT_PATH = r"D:\SpeedTest\AVI2MP4\Test_1"

#! Toggle this (True / False) to (delete / move or keep), respectively.
DELETE_AFTER = True

# If MOVE_FILE_PATH is set, files are moved there. If empty, files stay unless DELETE_AFTER is True.
MOVE_FILE_PATH = r""

#@ Set to True to convert largest files first.
CONVERT_LARGEST_FIRST = False

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
USE_LOG_FILE = True  #! Enable or disable log file saving entirely.
LOG_PATH = 'Logs'
LOG_NAME = 'Convert_AVI_to_MP4.txt'

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


def getFileSize(filepath):
    size = os.path.getsize(filepath)

    if size < 1024:
        return f'{size} B'
    elif size < 1024 ** 2:
        return f'{size / 1024:.2f} KB'
    elif size < 1024 ** 3:
        return f'{size / 1024 ** 2:.2f} MB'

    return f'{size / 1024 ** 3:.2f} GB'


def printDynamicConsole(totalFiles, completedFiles, currentFile, convertingFileStats):
    os.system('cls' if os.name == 'nt' else 'clear')

    print(f'Total AVI files to process: {totalFiles}\n')
    print('Files Complete:')

    for index, info in enumerate(completedFiles, 1):
        indexStr = f'{index:02}/{totalFiles:02}'
        print(f'    {indexStr} - Start: {info["startTime"]}  ||  End: {info["endTime"]}  ||  AVI: {info["convertingFileSize"]} -> MP4: {info["mp4Size"]}  ||  {info["mp4Path"].replace("\\", "/")}')

    if currentFile:
        indexStr = f'{len(completedFiles)+1:02}/{totalFiles:02}'
        print(f'\nAt {datetime.now().strftime('%I:%M:%S:%f %p')}, Started Processing {indexStr} - AVI Size: {convertingFileStats["size"]}  ||  {convertingFileStats["path"].replace("\\", "/")}\n')


def collectFilesToProcess(inPath, extension):
    files = [
        {
            'path': os.path.join(root, file),
            'size': getFileSize(os.path.join(root, file))
        }
        for root, _, files in os.walk(inPath)
        for file in files
        if file.lower().endswith(extension)
    ]

    return sorted(files, key=lambda x: os.path.getsize(x['path']), reverse=CONVERT_LARGEST_FIRST)


def convertFiles(inPath):
    aviFiles = collectFilesToProcess(inPath, '.avi')
    totalFiles = len(aviFiles)
    completedFiles = []

    for index, fileInfo in enumerate(aviFiles, 1):
        inputPath = fileInfo['path']
        outputPath = os.path.splitext(inputPath)[0] + '.mp4'
        startTime = datetime.now().strftime('%I:%M:%S:%f %p')
        indexStr = f'{index:02}/{totalFiles:02}'

        aviStats = {
            'path': inputPath,
            'size': fileInfo['size']
        }

        # Due to this script using a dynamic console, don't set logMsg print to True anywhere.
        printDynamicConsole(totalFiles, completedFiles, inputPath, aviStats)

        LOG(f'Processing: {indexStr}')
        LOG(f'    Start: {startTime}  ||  AVI Size: {fileInfo["size"]}  ||  {inputPath.replace("\\", "/")}')

        # Converts .avi to .mp4 using ffmpeg.
        result = subprocess.run(
            ['ffmpeg', '-i', inputPath, '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-c:a', 'aac', '-b:a', '192k', outputPath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        endTime = datetime.now().strftime('%I:%M:%S:%f %p')

        if result.returncode == 0 and os.path.exists(outputPath):
            mp4Size = getFileSize(outputPath)
            completedFiles.append({
                'startTime': startTime,
                'endTime': endTime,
                'convertingFileSize': fileInfo['size'],
                'mp4Size': mp4Size,
                'mp4Path': outputPath
            })

            LOG(f'    [SUCCESS] End: {endTime}  ||  {inputPath.replace("\\", "/")}')
            LOG(f'    File created: {endTime}  ||  MP4 Size: {mp4Size}  ||  {outputPath.replace("\\", "/")}')

            try:
                if DELETE_AFTER:
                    os.remove(inputPath)
                    LOG(f'    Deleted original AVI: {indexStr}  ||  {inputPath.replace("\\", "/")}')
                elif MOVE_FILE_PATH:
                    dest = os.path.abspath(MOVE_FILE_PATH)
                    os.makedirs(dest, exist_ok=True)
                    shutil.move(inputPath, os.path.join(dest, os.path.basename(inputPath)))
                    LOG(f'    Moved original AVI to: {indexStr}  ||  {dest.replace("\\", "/")}')
                else:
                    LOG(f'    Kept original AVI: {indexStr}  ||  {inputPath.replace("\\", "/")}')
            except Exception as e:
                LOG(f'    [ERROR] Error handling original file: {e}')
        else:
            errorMsg = result.stderr.decode('utf-8', errors='ignore')
            LOG(f'    [ERROR] Conversion failed: {inputPath}:\n{errorMsg}')

        LOG('-----')
        printDynamicConsole(totalFiles, completedFiles, None, aviStats)

    LOG(f'\nTotal files processed: {totalFiles}, Successful: {len(completedFiles)}')


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)
    LOG = createLogger(logFile)

    try:
        LOG(f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S:%f %p")}.\n', True)

        convertFiles(INPUT_PATH)

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
        LOG(f'[FINAL] Script exited at {datetime.now().strftime("%m/%d/%y %I:%M:%S:%f %p")}.', True)

