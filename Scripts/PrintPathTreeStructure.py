# Run by:  python PrintPathTreeStructure.py

# Imports
import ctypes
import os
import traceback
from datetime import datetime


#! ==========<  CONFIG  >==========
# Set the directory to scan. For DIRECTORY, must change the back slashes to forward slashes.
DIRECTORY = ""
# DIRECTORY_WINDOWS: Allows simple quick copy/paste from windows file explore. Prioritized over DIRECTORY if both valid paths.
DIRECTORY_WINDOWS = r"C:\Path\To\Folder"

#! Toggle this True/False to scan files or just folders in the given directory.
# If True, it creates two output files instead of one (one with folders only, one with files and folders).
SCAN_FILES = True

#! Toggle this True/False to show or hide file sizes.
SHOW_FILE_SIZE = False

#! Toggle this True/False to show root folder name or not inside the tree structure.
SHOW_ROOT_FOLDER = True


# Set output path and file name.
# OUTPUT_PATH NOTE: Allows absolute and relative folder paths. Examples: 'Output', './Output', '../Output', or 'D:/Output/'. All are valid.
# OUTPUT_PATH NOTE: Set to None or '' to not have save file to any folder. It will just save the file to the same folder as the script.
OUTPUT_PATH = 'Output'
OUTPUT_NAME = 'TreeStructure.txt'


# NOTE for IGNORE_LIST & ONLY_SELECT_LIST: Options: 'folder', 'file' (value can be file w/ extension or without), 'ext' OR 'extension'
# Define the list of folders and files to ignore.
IGNORE_LIST = [
    { 'folder': '__pycache__' },
    { 'folder': 'node_modules' },
    { 'file': 'ignored_file.txt' },
    { 'folder': '.git' },

    { 'folder': 'Windows' },             # C:/Windows/
    { 'folder': 'ProgramData' },         # C:/ProgramData/
    { 'folder': 'Program Files' },       # C:/Program Files/
    { 'folder': 'Program Files (x86)' }, # C:/Program Files (x86)/
    { 'folder': '$Recycle.Bin' },        # C:/$Recycle.Bin/         (assumed)
    { 'folder': 'Recovery' },            # C:/Recovery/             (assumed)

    { 'folder': 'Programs' },            # C:/Programs/

    { 'folder': 'All Users' },           # C:/Users/All Users/
    { 'folder': 'Default' },             # C:/Users/Default/
    { 'folder': 'Public' },              # C:/Users/Public/

    { 'folder': '.vscode' },             # C:/Users/<User>/.vscode/
    { 'folder': 'AppData' },             # C:/Users/<User>/AppData/
]

# Define a list of folders, files, and/or extensions to select specifically.
# NOTE: All of ONLY_SELECT must be true. If you specify a folder, only things inside that folder will be "noticed" otherwise it wont find all other files or extensions in other folders.
ONLY_SELECT_LIST = [
    #{ 'extension': '.py' },
]


# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
USE_LOG_FILE = True  #! Enable or disable log file saving entirely.
LOG_PATH = 'Logs'
LOG_NAME = 'PrintPathTreeStructure.txt'


# Clear the console every time you run the script?
CLEAR_CONSOLE = True
if CLEAR_CONSOLE: os.system('cls' if os.name == 'nt' else 'clear')

# Enables global use of LOG() without needing to pass createLogger() or logFile between functions.
LOG = lambda *args, **kwargs: None

# Determine SELECT_PATH with priority:
# 1. If DIRECTORY_WINDOWS exists and is non-empty, use it.
# 2. Else, if DIRECTORY exists and is non-empty, use it.
# 3. Else, set SELECT_PATH to an empty string (or raise an error/log if desired).
SELECT_PATH = ''
if 'DIRECTORY_WINDOWS' in locals() and DIRECTORY_WINDOWS:
    SELECT_PATH = DIRECTORY_WINDOWS
elif 'DIRECTORY' in locals() and DIRECTORY:
    SELECT_PATH = DIRECTORY
if not SELECT_PATH: raise ValueError('No valid directory path provided.')

# Separate ignore rules and select rules.
IGNORE_FOLDERS = set()
IGNORE_FILES = set()
IGNORE_EXTS = set()
ONLY_FOLDERS = set()
ONLY_FILES = set()
ONLY_EXTS = set()
for item in IGNORE_LIST:
    if 'folder' in item:
        IGNORE_FOLDERS.add(item['folder'])
    elif 'file' in item:
        IGNORE_FILES.add(item['file'])
    elif 'ext' in item or 'extension' in item:
        IGNORE_EXTS.add(item.get('ext') or item.get('extension'))

for item in ONLY_SELECT_LIST:
    if 'folder' in item:
        ONLY_FOLDERS.add(item['folder'])
    elif 'file' in item:
        ONLY_FILES.add(item['file'])
    elif 'ext' in item or 'extension' in item:
        ONLY_EXTS.add(item.get('ext') or item.get('extension'))
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


def formatFileSize(bytes):
    if bytes < 1024:
        return f'{bytes} B'
    elif bytes < 1024 ** 2:
        return f'{bytes / 1024:.2f} KB'
    elif bytes < 1024 ** 3:
        return f'{bytes / 1024 ** 2:.2f} MB'
    else:
        return f'{bytes / 1024 ** 3:.2f} GB'


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


def getClusterAwareDiskSize(filePath, clusterSize):
    actualSize = os.path.getsize(filePath)

    # Get reported on-disk size
    try:
        high = ctypes.c_ulong()
        low = ctypes.windll.kernel32.GetCompressedFileSizeW(ctypes.c_wchar_p(filePath), ctypes.byref(high))
        if low == 0xFFFFFFFF and ctypes.GetLastError() != 0:
            raise ctypes.WinError()
        reportedSize = (high.value << 32) + low
    except Exception as e:
        LOG(f'Error getting real disk size: {e}', True)
        reportedSize = actualSize  # fallback

    # If size is exactly the same as actualSize, and tiny, treat as MFT-resident (0 disk bytes)
    if reportedSize == actualSize and actualSize < 600:
        return 0

    # Otherwise, round to cluster boundary
    return ((reportedSize + clusterSize - 1) // clusterSize) * clusterSize


def isSelected(item, path=None):
    isFolder = os.path.isdir(path) if path else False

    # If there are no ONLY_* rules, allow everything.
    if not ONLY_FOLDERS and not ONLY_FILES and not ONLY_EXTS:
        return True

    # Allow all folders if no folder restriction is defined.
    if isFolder:
        return True if not ONLY_FOLDERS else item in ONLY_FOLDERS

    # File match (full name or ext).
    if item in ONLY_FILES:
        return True

    if any(item.lower().endswith(ext) for ext in ONLY_EXTS):
        return True

    return False


def isIgnored(item, path=None):
    isFolder = os.path.isdir(path) if path else False

    if isFolder and item in IGNORE_FOLDERS:
        return True

    if not isFolder and item in IGNORE_FILES:
        return True

    if not isFolder and any(item.lower().endswith(ext) for ext in IGNORE_EXTS):
        return True

    return False


def getFolderInfoTrueDiskUsage(path):
    fileCount = 0
    byteSizeSum = 0
    diskSizeSum = 0

    try:
        clusterSize = getClusterSize(path)
        entries = os.listdir(path)
    except Exception as e:
        LOG(f'[ACCESS ERROR] Cannot read {path} - {e}', True)
        return 0, 0, 0

    for entry in entries:
        fullPath = os.path.join(path, entry)

        if os.path.isfile(fullPath) and isSelected(entry, fullPath) and not isIgnored(entry, fullPath):
            try:
                actualBytes = os.path.getsize(fullPath)
                diskBytes = getClusterAwareDiskSize(fullPath, clusterSize)
                byteSizeSum += actualBytes
                diskSizeSum += diskBytes
                fileCount += 1
            except Exception as e:
                LOG(f'[SIZE ERROR] {fullPath} - {e}', True)

    return fileCount, byteSizeSum, diskSizeSum


def writeRoot(f, showRootFolder=False):
    if not showRootFolder:
        return ''

    rootName = os.path.basename(os.path.normpath(f)) + '/'

    return f'└── {rootName}\n'


def walkTree(directory, ignoreList, scanFiles=False):
    # Walks the full directory tree and collects:
    #  - Visual lines (line, realPath, isDir)
    #  - Folder stats (file count + size)
    #  - File size map
    #  - Alignment data

    lines = []
    fileSizeMap = {}
    folderStatsMap = {}
    maxLineLength = 0
    allCounts = []

    def recurse(dirPath, prefix=''):
        nonlocal maxLineLength

        # Filter items based on scanFiles flag.
        try:
            raw = sorted(os.listdir(dirPath))
        except Exception as e:
            LOG(f'[SKIPPED] {dirPath} - {e}', True)
            return  # Skip this folder.

        if scanFiles:
            filtered = [i for i in raw if isSelected(i, os.path.join(dirPath, i)) and not isIgnored(i, os.path.join(dirPath, i))]
            filtered.sort(key=lambda item: (not os.path.isdir(os.path.join(dirPath, item)), item))
            items = filtered
        else:
            items = [i for i in raw if isSelected(i, os.path.join(dirPath, i)) and not isIgnored(i, os.path.join(dirPath, i)) and os.path.isdir(os.path.join(dirPath, i))]

        # Iterate through items to construct the tree structure.
        for index, item in enumerate(items):
            # Define full path.
            path = os.path.join(dirPath, item)

            # Is folder flag.
            isDirFlag = os.path.isdir(path)

            # Determine if this is the last item.
            isLast = (index == len(items) - 1)

            # Set the connector for the item.
            connector = '└── ' if isLast else '├── '
            displaySlash = item + '/' if isDirFlag else item

            # Find lengths.
            line = f'{prefix}{connector}{displaySlash}'
            maxLineLength = max(maxLineLength, len(line))

            if os.path.isfile(path):
                if scanFiles:
                    # Record file size if enabled.
                    clusterSize = getClusterSize(path)
                    actualSize = os.path.getsize(path)
                    diskSize = getClusterAwareDiskSize(path, clusterSize)
                    actualStr = formatFileSize(actualSize)
                    diskStr = formatFileSize(diskSize)
                    fileSizeMap[path] = f'Disk: {diskStr} ({diskSize:,} B) Actual: {actualStr} ({actualSize:,} B)'
                    lines.append((line, path, False))
                continue  # Skip further logic for file.

            # If directory (files skip this logic).
            # Get folder's file count and size.
            fileCount, byteSizeSum, diskSizeSum = getFolderInfoTrueDiskUsage(path)
            folderStatsMap[path] = (fileCount, byteSizeSum, diskSizeSum)
            allCounts.append(f'{fileCount:,}')
            lines.append((line, path, True))

            newPrefix = prefix + ('    ' if isLast else '│   ')
            recurse(path, newPrefix)

    recurse(directory)
    return lines, fileSizeMap, folderStatsMap, maxLineLength, allCounts


def generateTree(directory, ignoreList, scanFiles=False):
    # Builds a fully formatted text representation of the tree, optionally with sizes.

    lines, fileSizeMap, folderStatsMap, maxLen, allCounts = walkTree(directory, ignoreList, scanFiles)

    # Step 1: Determine maximum fileCount length (left-aligned).
    maxCountLen = max((len(c) for c in allCounts), default=0)

    # Step 2: Longest possible label.
    labelLen = len('Files,')

    # Step 3: Compute the total left-padding needed for file sizes.
    sizeAlignCol = (maxCountLen + 1 + labelLen + 1) if allCounts else 0

    # Initialize tree variable.
    treeStructure = ''

    for line, realPath, isDir in lines:
        prefixPadding = ' ' * (maxLen - len(line))  # Align '-' symbols visually.

        if isDir and realPath in folderStatsMap:
            fileCount, actualBytes, diskBytes = folderStatsMap[realPath]
            countStr = f'{fileCount:,}'.ljust(maxCountLen)
            label = 'File, ' if fileCount == 1 else 'Files,'
            diskStr = formatFileSize(diskBytes)
            actualStr = formatFileSize(actualBytes)
            treeStructure += (f'{line}{prefixPadding}  -  {countStr} {label} Disk: {diskStr} ({diskBytes:,} B) Actual: {actualStr} ({actualBytes:,} B)\n')
        elif not isDir and realPath in fileSizeMap:
            sizeStr = fileSizeMap[realPath]
            emptyPrefix = ' ' * sizeAlignCol if allCounts else ''
            treeStructure += f'{line}{prefixPadding}  -  {emptyPrefix}{sizeStr}\n'

    return treeStructure


def buildSimpleTree(path, ignoreList, includeFiles, prefix=''):
    # Sort directories first, then files. Ignore folders/files in ignoreList.

    try:
        entries = os.listdir(path)
    except Exception as e:
        LOG(f'[SKIPPED] {path} - {e}', True)
        return  # Skip this folder completely.

    items = sorted(
        [
            i for i in entries
            if isSelected(i, os.path.join(path, i))
            and not isIgnored(i, os.path.join(path, i))
            and (includeFiles or os.path.isdir(os.path.join(path, i)))
        ],
        key=lambda item: (not os.path.isdir(os.path.join(path, item)), item)
    )

    # Iterate through items to construct the tree structure.
    for index, item in enumerate(items):
        # Define full path.
        subPath = os.path.join(path, item)

        # Is folder flag.
        isDirFlag = os.path.isdir(subPath)

        # Determine if this is the last item.
        isLast = index == len(items) - 1

        # Set the connector for the item.
        connector = '└── ' if isLast else '├── '
        displaySlash = item + '/' if isDirFlag else item

        yield f'{prefix}{connector}{displaySlash}'

        if isDirFlag:
            newPrefix = prefix + ('    ' if isLast else '│   ')
            yield from buildSimpleTree(subPath, ignoreList, includeFiles, newPrefix)


def saveTreeToFile(directory, outputFolder, outputFile, ignoreList, showFileSize=False, scanFiles=False, showRootFolder=False):
    # Saves both output files:
    # 1. Folders only.
    # 2. Folders + Files (if scanFiles=True).

    # Ensure output folder exists.
    if outputFolder:
        outputFolderPath = os.path.abspath(outputFolder)
        os.makedirs(outputFolderPath, exist_ok=True)
    else:
        outputFolderPath = os.path.dirname(os.path.abspath(__file__))

    # Base path for the main output file (folders only).
    basePath = os.path.join(outputFolderPath, outputFile)

    # Set indentation based on showRootFolder toggle.
    indent = '    ' if showRootFolder else ''

    # Write outputFile.txt always.
    with open(basePath, 'w', encoding='utf-8') as f:
        if showRootFolder:
            f.write(writeRoot(directory, showRootFolder))

        # If showFileSize is True, create tree structures.
        if showFileSize:
            tree = generateTree(directory, ignoreList, scanFiles=False)

            for line in tree.splitlines():
                f.write(indent + line + '\n')
        else:
            for line in buildSimpleTree(directory, ignoreList, includeFiles=False):
                f.write(indent + line + '\n')

    LOG(f'Saved tree:\n\t{basePath}', True)

    # If scanFiles is True, also generate & save a second tree structure that includes files.
    if scanFiles:
        name, ext = os.path.splitext(outputFile)
        withFilesPath = os.path.join(outputFolderPath, f'{name}AndFiles{ext}')

        with open(withFilesPath, 'w', encoding='utf-8') as f:
            if showRootFolder:
                f.write(writeRoot(directory, showRootFolder))

            # If showFileSize is True, create tree structures.
            if showFileSize:
                tree = generateTree(directory, ignoreList, scanFiles=True)

                for line in tree.splitlines():
                    f.write(indent + line + '\n')
            else:
                for line in buildSimpleTree(directory, ignoreList, includeFiles=True):
                    f.write(indent + line + '\n')

        LOG(f'Saved (with files):\n\t{withFilesPath}', True)


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)
    LOG = createLogger(logFile)

    try:
        LOG(f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        saveTreeToFile(SELECT_PATH, OUTPUT_PATH, OUTPUT_NAME, IGNORE_LIST, SHOW_FILE_SIZE, SCAN_FILES, SHOW_ROOT_FOLDER)

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

