# Run by:  python ConvertAll_WEBP_to_PNG_or_GIF_InAFolder.py
#! Requires ffmpeg and ffprobe.
# Converts all .webp files in a folder (recursively) to either .png or .gif based on animation detection.
# Static .webp → .png; Animated .webp → .gif.
# Optional file cleanup and logging supported.

# Imports
import os
import shutil
import subprocess
import traceback
from datetime import datetime


#! ==========<  CONFIG  >==========
# Set the path to scan for files.
#INPUT_PATH = r"C:\Path\To\Folder"
INPUT_PATH = r"D:\SpeedTest\WEBP2PNG\Test_1"

#! Toggle this (True / False) to (delete / move or keep), respectively.
DELETE_AFTER = False

# If MOVE_FILE_PATH is set, files are moved there. If empty, files stay unless DELETE_AFTER is True.
MOVE_FILE_PATH = r""

#@ Set to True to convert largest files first.
CONVERT_LARGEST_FIRST = False

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
LOG_PATH = 'Logs'
LOG_NAME = 'Convert_WEBP_to_PNG_or_GIF.txt'

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


def getFileSize(filePath):
    size = os.path.getsize(filePath)

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
        print(f'    {indexStr} - Start: {info["startTime"]}  ||  End: {info["endTime"]}  ||  WEBP: {info["convertingFileSize"]} -> PNG: {info["pngSize"]}  ||  {info["pngPath"].replace("\\", "/")}')

    if currentFile:
        indexStr = f'{len(completedFiles)+1:02}/{totalFiles:02}'
        print(f'\nAt {datetime.now().strftime('%I:%M:%S:%f %p')}, Started Processing {indexStr} - WEBP Size: {convertingFileStats["size"]}  ||  {convertingFileStats["path"].replace("\\", "/")}\n')


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


def isAnimatedWebP(filePath):
    # Uses ffprobe to detect if the .webp file contains animation frames.

    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'error',
                '-count_frames',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=nb_read_frames',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                filePath
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output = result.stdout.decode('utf-8').strip()

        return int(output) > 1
    except Exception:
        return False  # Assume static if ffprobe fails.



def convertFiles(logFile, inPath):
    webpFiles = collectFilesToProcess(inPath, '.webp')
    totalFiles = len(webpFiles)
    completedFiles = []

    for index, fileInfo in enumerate(webpFiles, 1):
        inputPath = fileInfo['path']
        startTime = datetime.now().strftime('%I:%M:%S:%f %p')
        indexStr = f'{index:02}/{totalFiles:02}'

        webpStats = {
            'path': inputPath,
            'size': fileInfo['size']
        }

        # Due to this script using a dynamic console, don't set logMsg print to True anywhere.
        printDynamicConsole(totalFiles, completedFiles, inputPath, webpStats)

        logMsg(logFile, f'Processing: {indexStr}')
        logMsg(logFile, f'    Start: {startTime}  ||  WEBP Size: {fileInfo["size"]}  ||  {inputPath.replace("\\", "/")}')

        # Determine output format based on animation check
        isAnimated = isAnimatedWebP(inputPath)

        if isAnimated:
            outputPath = os.path.splitext(inputPath)[0] + '.gif'
            ffmpegArgs = ['ffmpeg', '-i', inputPath, '-y', outputPath]
        else:
            outputPath = os.path.splitext(inputPath)[0] + '.png'
            ffmpegArgs = ['ffmpeg', '-i', inputPath, '-frames:v', '1', '-y', outputPath]

        # Converts .webp to .png (or .gif) using ffmpeg.
        result = subprocess.run(ffmpegArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        endTime = datetime.now().strftime('%I:%M:%S:%f %p')

        if result.returncode == 0 and os.path.exists(outputPath):
            outputSize = getFileSize(outputPath)
            completedFiles.append({
                'startTime': startTime,
                'endTime': endTime,
                'convertingFileSize': fileInfo['size'],
                'pngSize': outputSize,
                'pngPath': outputPath
            })

            logMsg(logFile, f'    [SUCCESS] End: {endTime}  ||  {inputPath.replace("\\", "/")}')
            logMsg(logFile, f'    File created: {endTime}  ||  Output Size: {outputSize}  ||  {outputPath.replace("\\", "/")}')

            try:
                if DELETE_AFTER:
                    os.remove(inputPath)
                    logMsg(logFile, f'    Deleted original WEBP: {indexStr}  ||  {inputPath.replace("\\", "/")}')
                elif MOVE_FILE_PATH:
                    dest = os.path.abspath(MOVE_FILE_PATH)
                    os.makedirs(dest, exist_ok=True)
                    shutil.move(inputPath, os.path.join(dest, os.path.basename(inputPath)))
                    logMsg(logFile, f'    Moved original WEBP: {indexStr}  ||  {dest.replace("\\", "/")}')
                else:
                    logMsg(logFile, f'    Kept original WEBP: {indexStr}  ||  {inputPath.replace("\\", "/")}')
            except Exception as e:
                logMsg(logFile, f'    [ERROR] Error handling original file: {e}')
        else:
            errorMsg = result.stderr.decode('utf-8', errors='ignore')
            logMsg(logFile, f'    [ERROR] Conversion failed: {inputPath}:\n{errorMsg}')

        logMsg(logFile, '-----')
        printDynamicConsole(totalFiles, completedFiles, None, webpStats)

    logMsg(logFile, f'\nTotal files processed: {totalFiles}, Successful: {len(completedFiles)}.')


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)

    try:
        logMsg(logFile, f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S:%f %p")}.\n', True)

        convertFiles(logFile, INPUT_PATH)

        logMsg(logFile, f'\nLogs saved to "{logFile.replace("\\", "/")}".', True)
        logMsg(logFile, f'[END] Script completed at {datetime.now().strftime("%m/%d/%y %I:%M:%S:%f %p")}.', True)
    except KeyboardInterrupt:
        err = '[ERROR] Script interrupted by user (KeyboardInterrupt / CTRL+C).\n'
        trace = traceback.format_exc()
        logMsg(logFile, err + trace, True)
    except Exception:
        err = '[ERROR] Unhandled Exception:\n'
        trace = traceback.format_exc()
        logMsg(logFile, err + trace, True)
    finally:
        logMsg(logFile, f'[FINAL] Script exited at {datetime.now().strftime("%m/%d/%y %I:%M:%S:%f %p")}.', True)

