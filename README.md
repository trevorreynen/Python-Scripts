# Python-Scripts

This repository contains a growing collection of Python scripts for small tools, experiments, and automation workflows. Many of these scripts were written independently which had previously led to inconsistent formatting and file locations. This repository was created to centralize everything in one place, clean up structure, and provide clarity for future development.

There are no strict plans for this repo, but various features and tooling may be added over time. Some ideas are noted internally.



## 📑 Table of Contents
- [Python Formatting & Structure Standards](#python-formatting-and-structure-standards)
- [Guideline Philosophy](#guideline-philosophy)
- [Template Structure Overview](#template-structure-overview)
- [Variable Naming Clear Definitions (Python + Filesystem Context)](#variable-naming-definitions)
- [Naming Categories for File/Directory Contexts](#naming-categories)
- [Predefined Ordered Naming Lists](#predefined-ordered-naming-list)



## 1⃣ Python Formatting & Structure Standards <a name="python-formatting-and-structure-standards"></a>
These guidelines define the preferred formatting and structure for all scripts in this repository.

### 1. General Rules
- Global variables use `UPPERCASE_SNAKE_CASE`.
- Use single quotes (`'`) for all strings unless double quotes are required (e.g. to avoid escaping single quotes or within format strings).
- Use `camelCase` for all variables, parameters, arguments, function names, method names, attributes, and instances.
  - Dictionary keys, list comprehensions, loop counters, and exception aliases may also use camelCase for consistency.
  - This excludes the global variables rule.
  - `snake_case` is reserved only for external compatibility or when clarity is improved.
- Use `PascalCase` for class names.
- Encapsulate all executable logic within functions. Avoid top-level statements like `for`, `if`, or `try` outside functions.
- Prefer `Path` over `Dir` or `Directory` in variable names, unless clarity requires otherwise.

### 2. Commenting Rules
- Comments should provide context, even if not full sentences.
- Begin with one leading space and a capital letter.
- End with a period for consistency.
- For commented-out code lines, **omit the space** after the hash symbol to improve scannability. For example:
  ```python
  # Set input paths:
  #INPUT_PATH = r"C:/Path/To/Folder/Or/File"
  INPUT_PATH = r"C:/Path/To/Folder/Or/File"
  ```
- Inline comments should have two spaces between the end of the statement and the comment.
- Use Triple double quotes (`"""`) for docstrings. Multi-line comments not used as docstrings may use single quotes.

### 3. Path Handling
- Paths can be:
  - `'C:/Path/To/File'` (Requires doubled backslashes or forward slashes).
  - `r"C:\Path\To\File"` (Preferred on Windows for raw copy-paste).
- Normalize all paths at the start of the script using either `Path.resolve()` or `os.path.abspath()` to ensure consistent behavior across relative and absolute input.
  <br>**Example References:**
    - `./Templates/useOSExample.py` (using `os.path`)
    - `./Templates/usePathExample.py` (using `pathlib`)

### 4. Spacing & Formatting Conventions
- Prefer multi-line blocks for if/else and for statements to improve readability.
  - Single-line versions are permitted when the logic is trivial and inline readability outweighs structure.
  - This is a situational judgment based on the surrounding code.
- Spacing Before Key Blocks:
  - **For each line starting with `class` or `def`:**
    - If the line directly before it is a comment (`# Comment...`, assuming you aren't using docstrings and commenting a different way), insert **two empty lines above** the comment.
    - Otherwise, insert **two empty lines directly above** the `class` or `def`.
  - **Control Statements (`while`, `with`, `for`, `if`, `try`):**
    - If the line immediately before is **not**:
      - Another control statement (`while`, `with`, `for`, `if`, `try`), or
      - A comment (`# Comment...`),
    - Then insert **one empty line above**.
      > [!IMPORTANT]
      > If the line before is a comment (# ), check whether the line before that is also a control statement. If not, insert one empty line before the comment.
  - **`return` Statements**
    - Insert a **single empty line above** any return, unless the line directly before it is a:
      - `class`, `def`, `while`, `with`, `for`, `if`, `try`
- Additional formatting rules are noted in the [Template Structure Overview](#template-structure-overview)



## 2⃣ 📌 Guideline Philosophy <a name="guideline-philosophy"></a>
> [!NOTE]
> These are intentionally flexible and reflect current habits, not strict enforcement. Inconsistencies may appear across scripts due to evolving preferences, situational decisions, or legacy code left untouched.



## 3⃣ Template Structure Overview <a name="template-structure-overview"></a>
Templates for script structure are provided in:
- `./Templates/templateUsingOS.py` (main template)
- `./Templates/templateUsingPath.py`

These templates are baseline mental scaffolding, usable as-is or modifiable.


### 1. Script Header
Start each script with:
- A run command comment
- An optional single or multi-line comment explaining the script
- A comment block above imports (with one empty line above it):
```python
# Run by:  python <fileName>.py
# Optional explanation of the script.

# Imports
import os
```

### 2. Config Section
- Leave two empty lines before the config section.
- All config variables are uppercase and snake case.
- Comments should clarify the expected type or purpose of each variable (file vs. folder, relative vs. absolute, etc)
- Leave two empty lines below the config section:
```python
import os


#! ==========<  CONFIG  >==========
# Set the path to scan.
INPUT_PATH = r""

# Set the output path.
OUTPUT_PATH = r""

# Set the log file config.
# LOG_PATH: Folder to save logs. Supports both absolute and relative paths — e.g. 'Logs', './Logs', '../Logs', or 'D:/Logs/'.
#           Set to None or '' to save the log in the same directory as this script.
# LOG_NAME: File name for the log. Automatically increments to avoid overwriting existing files.
LOG_PATH = 'Logs'
LOG_NAME = 'LogFile.txt'

# Clear the console every time you run the script?
CLEAR_CONSOLE = True
if CLEAR_CONSOLE: os.system('cls' if os.name == 'nt' else 'clear')
#! ================================


def main():
    # ...
```

### 3. Main Script Block
- Use `if __name__ == '__main__':`
- Always create a log file first.
- Example call with `logMsg()`:
```python
import traceback
from datetime import datetime

if __name__ == '__main__':
    # Create log file first so we can log even if any script functions fail early.
    logFile = getNextLogFilePath(LOG_PATH, LOG_NAME)

    try:
        logMsg(logFile, f'[START] Script started at {datetime.now().strftime("%m/%d/%y %I:%M:%S %p")}.\n', True)

        # Run the main script function.
        mainExample(logFile, INPUT_PATH, OUTPUT_PATH)

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
```

### 4. Log Helpers
Typically placed after the config block:
```python
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
```

### 5. VS-Code: Better Comments (Optional)
Example setup for highlighting structured comments:
```python
{
  "better-comments.tags": [
    {
      "tag": "!",
      "color": "#f00",
      "bold": true
    }
  ]
}
```
This enables headers like `#! ==========< CONFIG >==========` to visually stand out.



## 4⃣ Variable Naming Clear Definitions (Python + Filesystem Context) <a name="variable-naming-definitions"></a>

| **Term**                      | **Definition** |
| ----------------------------- | -------------- |
| `directory`                   | A container for organizing files and other directories, also known as a **folder**. The terms *directory* (technical) and *folder* (GUI-friendly) are interchangeable. |
| `path`                        | A string that represents the location of a file or directory in the file system. It can be **absolute** (from root) or **relative** (from the current directory). |
| `file path`                   | A path that points to a file, typically ending with a **filename** and optionally an extension (e.g. `'report.txt'`). It may be relative or absolute. It refers to the location **of a file**, though the file may or may not exist. |
| `directory path`              | A path that points to a directory (folder), such as `'./data/exports'` or `'C:/Users/Trevor/Documents'`. Like file paths, directory paths may be absolute or relative. |
| `filename`                    | The name of a file **without any directory path** (e.g. `'output.json'`). In programming, this is often referred to as the **basename** of a file. |
| `absolute path` / `full path` | A path that specifies a location from the root of the file system (e.g. `'C:/Users/Trevor'` on Windows or `'/home/trevor'` on Unix/Linux). It does not depend on the current working directory. |
| `relative path`               | A path that is defined **in relation to the current working directory** (e.g. `'./output'`, `'../assets/image.png'`). It does not begin with a root (`/`) or drive letter (`C:`). |



## 5⃣ Naming Categories for File/Directory Contexts <a name="naming-categories"></a>

### 📥 **Input (Generic)**

Use for incoming data, files, or user-provided sources. Prefer `inputFile`, `inputPath`, etc., to make the role clear.
- `input`, `inputPath`, `inputFile`, `inputDir`, `inputFolder`, `inputFilename`, `inputDirectoryPath`, `inPath`, `sourcePath`, `sourceFile`

> [!TIP]
> `source` is useful as a synonym when "input" starts to feel repetitive.

> [!TIP]
> Reserve `inputFile`, `inputPath`, or `inPath` for values used *only for reading*. Avoid overloading them later for derived or output-related paths.

> **Debugging Tip:** Prefixing with `in*` makes it easy to know the direction of data.

> **Naming Strategy:** If it's raw, user-facing, or CLI-based input → `inputFile`; if internal derivation or secondary input → `inFile`, `inputPath2`, etc.

<br />

### 📤 **Output (Generic)**

Use for processed results, files to be saved, etc.
- `output`, `outputPath`, `outputFile`, `outputDir`, `outputFolder`, `outputFilename`, `outPath`, `savePath`, `exportPath`, `resultFile`

> [!TIP]
> `exportPath` or `savePath` work well in UIs or CLI tools when output is user-defined.

> [!TIP]
> Start generic like `outputPath`, but allow variation (`outPath`, `savePath`, `exportPath`) for clarity in deeper functions.

> **Debugging Tip:** A naming ladder (`outputPath → savePath → writePath`) helps track file evolution.

> **Naming Strategy:** Use `out*` or `save*` when writing to disk is happening. Use `result*` or `final*` when output is transformed.

<br />

### 🗂️ **Folders / Directories**

Use when dealing explicitly with directories (rather than files).
- `folderPath`, `dirPath`, `outputDir`, `inputDir`, `workingDir`, `targetDir`, `tempDir`, `logDir`, `rootDir`, `baseDir`

> [!TIP]
> prefer `Dir` or `Folder` consistently. In most codebases, `Dir` is preferred for brevity.

> [!TIP]
> Use `dir`, `folder`, and `directory` consistently across the script.

> **Debugging Tip:** Consider prefixes like `tempDir`, `cacheDir`, `logDir` to imply purpose.

> **Naming Strategy:** Always append `Dir` or `Folder` to avoid confusing with file paths.

<br />

### 📄 **Files**

Use when the value is clearly a file path or name.
- `filePath`, `inputFile`, `outputFile`, `targetFile`, `configFile`, `logFile`, `fileName`, `fileStem`, `fileExt`, `dataFile`

> [!TIP]
> `fileStem` = name without extension, `fileExt` = extension (e.g. `.txt`).

> [!TIP]
> Reserve `fileName` or `fileStem` for filename-only (no path). Use `filePath` when including path.

> **Debugging Tip:** Tracking file extensions separately (`fileExt`) can simplify validation.

> **Naming Strategy:** For intermediate formats, use `tempFile`, `rawFile`, or `parsedFile`.

<br />

### 🎯 **Target**

Use when aiming to copy/move/save to a new location.
- `targetPath`, `targetFile`, `targetDir`, `targetFolder`, `targetName`, `targetDest`, `targetFilename`, `finalTarget`, `writeTarget`

> [!TIP]
> Think of "target" as a final destination or intended override.

> **Debugging Tip:** `target*` variables are helpful when copying or moving things, especially in CLI utilities.

> **Naming Strategy:** Use `targetPath`, `targetFile`, `targetName` when passing in an "end goal" (what should exist after the script finishes).

<br />

### 📌 **Destination**

A bit more generic or abstract than "target" — use for user-selected destinations or post-processing output.
- `destination`, `destinationPath`, `destinationFile`, `destinationDir`, `destPath`, `destFile`, `destFolder`, `saveDestination`, `finalPath`, `writePath`

> [!TIP]
> More abstract than "target". Use when user picks a location or default is configured.

> **Debugging Tip:** `dest*` is good for file saving or packaging operations.

> **Naming Strategy:** `destinationDir`, `destPath`, `finalDest` are good post-processing names.

<br />

### 🧱 **Base**

Use for deriving filenames or directory components, e.g., `os.path.splitext`.
- `baseName`, `fileStem`, `baseFileName`, `baseOutput`, `baseDir`, `basePath`, `outputBaseName`, `targetBaseName`

> [!TIP]
> `baseName` often refers to the filename without path (e.g. `os.path.basename`) while `fileStem` usually refers to the name without the extension.

> [!TIP]
> Use only for components (like when splitting files, not full paths).

> **Debugging Tip:** Don't overuse `base*`; keep it tied to *derivation* (stem, name, directory).

> **Naming Strategy:** Reserve `baseName`, `fileStem`, and `baseDir` for string manipulations and path building.

<br />

### 🧾 **Special Purpose (Optional Additions)**
Useful for more descriptive or advanced cases.
- `fullPath` - full absolute path
- `relativePath` - path from working dir
- `tempFile` - temporary file
- `cacheFile` - cached result
- `logFileName` - log file name only
- `workingPath` - current working file path
- `backupFile` - used for rollback or backup
- `finalFilePath` - resolved path after all steps
- `saveAsName` - name chosen for saving (UI-style)


### 📘 **Naming Best Practices**
- Try to always **hint at the type** (`Path`, `Dir`, `File`, `Name`) in variable names if ambiguity is possible.
- Avoid overloading terms like `base` or `target` without context (`baseFileName` vs. `baseDir` is clearer).



## 6⃣ Predefined Ordered Naming Lists <a name="predefined-ordered-naming-list"></a>
These ladders provide a consistent naming sequence for similar variables passed through multiple layers of a script.
They exist to reduce decision fatigue, improve searchability, and establish a clear naming path when uniformity is preferred.

> [!NOTE]
> These are optional conventions — not enforced rules. They may not be used in every script, including this one, but are available for reference when naming consistency is desired.

### 📥📤 **File Ladders**
| Order | Input Ladder        | Output Ladder        |
| ----- | ------------------- | -------------------- |
| 1.    | `inputFilePathName` | `outputFilePathName` |
| 2.    | `inputFilePath`     | `outputFilePath`     |
| 3.    | `inputPath`         | `outputPath`         |
| 4.    | `inputFile`         | `outputFile`         |
| 5.    | `inFilePath`        | `outFilePath`        |
| 6.    | `inFile`            | `outFile`            |

<br />

### 📥📤🗂️ **Folder Ladder**
| Order | Input Ladder         | Output Ladder         |
| ----- | -------------------- | --------------------- |
| 1.    | `inputDirectoryPath` | `outputDirectoryPath` |
| 2.    | `inputDirPath`       | `outputDirPath`       |
| 3.    | `inputDir`           | `outputDir`           |
| 4.    | `inDir`              | `outDir`              |

<br />

### 📥📤📄 **File Name Component Ladder**
| Order | Input Ladder    | Output Ladder    |
| ----- | --------------- | ---------------- |
| 1.    | `inputFileName` | `outputFileName` |
| 2.    | `inputBaseName` | `outputBaseName` |
| 3.    | `inputFileStem` | `outputFileStem` |
| 4.    | `inName`        | `outName`        |

<br />

### 🧱 **Base Ladder (post-split or derived)**
1. `baseFileName`
2. `baseName`
3. `fileStem`
4. `nameStem`
5. `nameOnly`

<br />

### 🎯 **Target Ladder**
1. `targetFilePath`
2. `targetPath`
3. `targetFile`
4. `targetName`
5. `targetOut`
6. `writeTarget`

<br />

### 📌 **Destination Ladder**
1. `destinationFilePath`
2. `destinationPath`
3. `destPath`
4. `destFile`
5. `finalDest`
6. `savePath`

<br />

### 🛠️ Generic Reusable Extras (for internal function logic)
- `tempFile`, `logFile`, `finalFile`, `configPath`, `resourceFile`, `cacheDir`


