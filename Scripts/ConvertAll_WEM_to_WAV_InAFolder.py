# Run by:  python ConvertAll_WEM_to_WAV_InAFolder.py
#! Requires the vgmstream-cli tool.
# Converts all .wem audio files in a folder (recursively) to .wav format.
# Supports optional deletion or moving of source files.

# Imports
import os
import subprocess
import shutil
import traceback
from datetime import datetime


#! ==========<  CONFIG  >==========
# Set the path to scan for WEM files.
#INPUT_PATH = r"C:\Path\To\Folder"
INPUT_PATH = r"D:\SpeedTest\WEM2WAV\Test_1"

# Set the output path for WAV files. If empty, converts wav's to same as INPUT_PATH.
OUTPUT_PATH = r""

#! Toggle this (True / False) to (delete / move or keep), respectively.
DELETE_AFTER = False

# If MOVE_FILE_PATH is set, files are moved there. If empty, files stay unless DELETE_AFTER is True.
MOVE_FILE_PATH = r""

#@ Set to True to convert largest files first.
CONVERT_LARGEST_FIRST = False

# Path to vgmstream-cli.exe (required for decoding .wem files).
# Download from: https://github.com/vgmstream/vgmstream
VGMSTREAM_CLI = r"C:\\Programs\\CLI-Tools\\vgmstream\\vgmstream-cli.exe"

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
LOG_PATH = 'Logs'
LOG_NAME = 'Convert_WEM_to_WAV.txt'

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


def getFileSize(filepath):
    size = os.path.getsize(filepath)

    if size < 1024:
        return f'{size} B'
    elif size < 1024 ** 2:
        return f'{size / 1024:.2f} KB'
    elif size < 1024 ** 3:
        return f'{size / 1024 ** 2:.2f} MB'

    return f'{size / 1024 ** 3:.2f} GB'


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


def convertFiles(logFile, inPath, outPath):
    # NOTE: Avoid excessive logging inside tight loops. It can significantly slow down processing.

    wemFiles = collectFilesToProcess(inPath, '.wem')
    totalFiles = len(wemFiles)
    completedFiles = []

    # Since no dynamic console used in this script, use logMsg but don't use it too much otherwise it slows the script down.
    logMsg(logFile, f'Total WEM files to process: {totalFiles}\n', True)

    for index, fileInfo in enumerate(wemFiles, 1):
        inputPath = fileInfo['path']
        wemRelativePath = os.path.relpath(inputPath, inPath)
        wavRelativePath = os.path.splitext(wemRelativePath)[0] + '.wav'
        outputPath = os.path.join(outPath or os.path.dirname(inputPath), wavRelativePath if outPath else os.path.basename(wavRelativePath))

        startTime = datetime.now().strftime('%I:%M:%S:%f %p')
        indexStr = f'{index:02}/{totalFiles:02}'

        # This logMsg specifically might slow down the script. If it seems slow (or just want to double check), comment it out.
        #logMsg(logFile, f'At {startTime}, Started Processing {indexStr} - WEM Size: {fileInfo["size"]}  ||  {inputPath.replace("\\", "/")}', True)
        os.makedirs(os.path.dirname(outputPath), exist_ok=True)

        # Converts .wem to .wav using vgmstream-cli (CLI-only, external tool required).
        result = subprocess.run(
            [VGMSTREAM_CLI, '-o', outputPath, inputPath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        endTime = datetime.now().strftime('%I:%M:%S:%f %p')

        if result.returncode == 0 and os.path.exists(outputPath):
            wavSize = getFileSize(outputPath)
            completedFiles.append({
                'startTime': startTime,
                'endTime': endTime,
                'convertingFileSize': fileInfo['size'],
                'wavSize': wavSize,
                'wavPath': outputPath
            })

            logMsg(logFile, f'    [SUCCESS] End: {endTime}  ||  {inputPath.replace("\\", "/")}', True)
            #logMsg(logFile, f'    File created: {endTime}  ||  WAV Size: {wavSize}  ||  {outputPath.replace("\\", "/")}', True)  # Not using due to logging slowing down the script more than anything.

            try:
                if DELETE_AFTER:
                    os.remove(inputPath)
                    logMsg(logFile, f'    Deleted original WEM: {indexStr}  ||  {inputPath.replace("\\", "/")}', True)
                elif MOVE_FILE_PATH:
                    dest = os.path.abspath(MOVE_FILE_PATH)
                    os.makedirs(dest, exist_ok=True)
                    shutil.move(inputPath, os.path.join(dest, os.path.basename(inputPath)))
                    #logMsg(logFile, f'    Moved original WEM to: {indexStr}  ||  {dest.replace("\\", "/")}', True)  # Not using due to logging slowing down the script more than anything.
                #else:
                    #logMsg(logFile, f'    Kept original WEM: {indexStr}  ||  {inputPath.replace("\\", "/")}', True)  # Not using due to logging slowing down the script more than anything.
            except Exception as e:
                logMsg(logFile, f'    [ERROR] Error handling original file: {e}', True)
        else:
            errorMsg = result.stderr.decode('utf-8', errors='ignore')
            logMsg(logFile, f'    [ERROR] Conversion failed: {inputPath}:\n{errorMsg}', True)

        logMsg(logFile, '-----')

    logMsg(logFile, f'\nTotal files processed: {totalFiles}, Successful: {len(completedFiles)}', True)


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)

    try:
        logMsg(logFile, f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S:%f %p")}.\n', True)

        convertFiles(logFile, INPUT_PATH, OUTPUT_PATH)

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

