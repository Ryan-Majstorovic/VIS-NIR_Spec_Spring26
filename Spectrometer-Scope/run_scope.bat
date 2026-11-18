@echo off
cd /d "%~dp0"
"..\PythonGUI\.venv\Scripts\python.exe" scope.py gui %*
