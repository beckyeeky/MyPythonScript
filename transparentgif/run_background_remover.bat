@echo off
setlocal enabledelayedexpansion

REM Get the directory of this batch file
set "BATCH_DIR=%~dp0"

REM Get the directory of the dropped file
set "FILE_DIR=%~dp1"

REM Change to the directory of the dropped file
cd /d "%FILE_DIR%"

REM Path to your Python script (in the same directory as the batch file)
set "SCRIPT_PATH=%BATCH_DIR%background_remover.py"

REM Check if Python is installed and in PATH
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python and make sure it's added to your system PATH.
    pause
    exit /b 1
)

REM Check if the Python script exists
if not exist "%SCRIPT_PATH%" (
    echo Cannot find background_remover.py in the same directory as this batch file.
    echo Please make sure the Python script is in the same folder as this batch file.
    pause
    exit /b 1
)

REM Process dropped file
if "%~1"=="" (
    echo Drag and drop an image file onto this batch file to process it.
    pause
    exit /b 0
) else (
    echo Processing: %~nx1
    for /f "delims=" %%i in ('python "%SCRIPT_PATH%" "%~nx1"') do set "RESULT=%%i"
    if "!RESULT:~0,5!"=="Error" (
        echo An error occurred: !RESULT!
    ) else (
        echo Processing complete.
        echo Output saved as: !RESULT!
    )
    pause
)