# Run by:  python generateColorGradientCsv.py
# Generates a CSV with multiple columns of color gradients.
# Each column is built from a base color and sorted from darkest to brightest shade (base color centered).
# Useful for creating visually balanced color palettes for use in spreadsheets, UI themes, or data viz.

# Imports
import colorsys
import csv
import os
import traceback
from datetime import datetime


#! ==========<  CONFIG  >==========
# Number of gradient steps from base color toward white.
BRIGHTEN_NUM = 25

# Number of gradient steps from base color toward black.
DARKEN_NUM = 12

# Set base colors.
BASE_COLORS = [
    '#FF0000',  # Red
    '#FF7F00',  # Orange
    '#FFFF00',  # Yellow
    '#7FFF00',  # Chartreuse
    '#00FF00',  # Green
    '#00FF7F',  # Spring Green
    '#00FFFF',  # Cyan
    '#007FFF',  # Azure
    '#0000FF',  # Blue
    '#7F00FF',  # Violet
    '#FF00FF',  # Magenta
    '#FF007F',  # Rose
]

# NOTE: BASE_COLORS and CSV_HEADERS must have matching lengths.
# Each header corresponds to one color column.
CSV_HEADERS = [
    'Red',
    'Orange',
    'Yellow',
    'Chartreuse',
    'Green',
    'Spring Green',
    'Cyan',
    'Azure',
    'Blue',
    'Violet',
    'Magenta',
    'Rose',
]

# Set the output path.
OUTPUT_PATH = r"./Output/"

# Set the CSV Name.
CSV_NAME = 'generateColorGradientCsv.csv'

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
LOG_PATH = 'Logs'
LOG_NAME = 'generateColorGradientCsv.txt'

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


def getNextCsvFilePath(csvFolder, csvFileName):
    if csvFolder:
        csvPath = os.path.abspath(csvFolder)
    else:
        csvPath = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(csvPath, exist_ok=True)
    baseName, ext = os.path.splitext(csvFileName)
    csvNumber = 1

    while True:
        fileName = f'{baseName}_{csvNumber}{ext}'
        fullCsvPath = os.path.join(csvPath, fileName)

        if not os.path.exists(fullCsvPath):
            return fullCsvPath

        csvNumber += 1


def hexToRgb(hexCode):
    hexCode = hexCode.lstrip('#')

    return tuple(int(hexCode[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def rgbToHex(r, g, b):
    return '#{:02X}{:02X}{:02X}'.format(int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def generateGradient(hexColor, brightenSteps, darkenSteps):
    r, g, b = hexToRgb(hexColor)
    h, l, s = colorsys.rgb_to_hls(r, g, b)

    gradient = []

    # Darken steps: lightness from l -> 0.
    for i in range(1, darkenSteps + 1):
        lightnessDarken = l * (1 - i / (darkenSteps + 1))
        rDarken, gDarken, bDarken = colorsys.hls_to_rgb(h, lightnessDarken, s)
        gradient.append(rgbToHex(rDarken, gDarken, bDarken))

    # Middle base color.
    gradient.append(hexColor.upper())

    # Brighten steps: lightness from l -> 1.
    for i in range(1, brightenSteps + 1):
        lightnessBrighten = l + (1 - l) * (i / (brightenSteps + 1))
        rBrighten, gBrighten, bBrighten = colorsys.hls_to_rgb(h, lightnessBrighten, s)
        gradient.append(rgbToHex(rBrighten, gBrighten, bBrighten))

    return gradient


def generateColorGradientCsv(logFile, outPath, brightenSteps, darkenSteps, baseColors, csvHeaders, csvName):
    allColumns = []

    for base in baseColors:
        gradient = generateGradient(base, brightenSteps, darkenSteps)

        # Split into parts.
        dark = gradient[:darkenSteps]
        base_hex = gradient[darkenSteps]
        bright = gradient[darkenSteps + 1:]

        # Flip the dark section to go darkest → base.
        dark.reverse()

        # Final vertical stack: [darkest → base → brightest].
        ordered_column = dark + [base_hex] + bright
        allColumns.append(ordered_column)

    # Transpose the list so each row contains one brightness level across all colors.
    csvRows = list(zip(*allColumns))

    # Create output file path.
    csvFilePath = getNextCsvFilePath(outPath, csvName)

    # Write to CSV.
    try:
        with open(csvFilePath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Use headers.
            writer.writerow(csvHeaders)

            # Write all color rows.
            for row in csvRows:
                writer.writerow(row)

        logMsg(logFile, f'[SUCCESS] CSV file written to "{csvFilePath}".', True)
    except Exception as e:
        logMsg(logFile, f'[ERROR] Failed to write CSV: {str(e)}', True)


if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)

    try:
        logMsg(logFile, f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        generateColorGradientCsv(logFile, OUTPUT_PATH, BRIGHTEN_NUM, DARKEN_NUM, BASE_COLORS, CSV_HEADERS, CSV_NAME)

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

