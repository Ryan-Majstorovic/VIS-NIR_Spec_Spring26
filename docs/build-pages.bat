@echo off
setlocal

for %%I in ("%~dp0.") do set "ROOT_DIR=%%~fI"
set "SOURCE_DIR=%ROOT_DIR%\source"
set "BUILD_DIR=%ROOT_DIR%\build\html"
set "PYTHON_EXE="
set "EXIT_DELAY_SECONDS=20"

python -V >nul 2>&1
if not errorlevel 1 set "PYTHON_EXE=python"

if not defined PYTHON_EXE (
    py -V >nul 2>&1
    if not errorlevel 1 set "PYTHON_EXE=py"
)

if not defined PYTHON_EXE (
    echo [ERROR] Python was not found on PATH. Install Python and rerun this script.
    goto :fail
)

if not exist "%ROOT_DIR%\conf.py" (
    echo [ERROR] Sphinx config not found at "%ROOT_DIR%\conf.py".
    goto :fail
)

if not exist "%SOURCE_DIR%\index.rst" (
    echo [ERROR] Sphinx source not found at "%SOURCE_DIR%\index.rst".
    goto :fail
)

echo [1/2] Installing documentation dependencies...
%PYTHON_EXE% -m pip install --disable-pip-version-check --no-warn-script-location -r "%ROOT_DIR%\requirements.txt"
if errorlevel 1 (
    echo [ERROR] Dependency install failed.
    goto :fail
)

echo [2/2] Building HTML documentation to "%BUILD_DIR%"...
if exist "%BUILD_DIR%" (
    echo Removing existing HTML build directory...
    rmdir /s /q "%BUILD_DIR%"
)
mkdir "%BUILD_DIR%"
%PYTHON_EXE% -m sphinx -b html -c "%ROOT_DIR%" "%SOURCE_DIR%" "%BUILD_DIR%"
if errorlevel 1 (
    echo [ERROR] Sphinx build failed.
    goto :fail
)

echo Build complete.
echo Open "%BUILD_DIR%\index.html" in your browser.
echo Closing in %EXIT_DELAY_SECONDS% seconds...
timeout /t %EXIT_DELAY_SECONDS% /nobreak >nul

endlocal
exit /b 0

:fail
echo Closing in %EXIT_DELAY_SECONDS% seconds so you can review the errors...
timeout /t %EXIT_DELAY_SECONDS% /nobreak >nul
endlocal
exit /b 1

