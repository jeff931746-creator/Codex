@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  set "PYTHON_CMD=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 goto no_python
  set "PYTHON_CMD=python"
)

%PYTHON_CMD% -c "import certifi" >nul 2>nul
if errorlevel 1 (
  echo First run: installing required Python package...
  %PYTHON_CMD% -m pip install -r requirements.txt
  if errorlevel 1 goto install_failed
)

echo Starting CBG valuation workbench at http://127.0.0.1:8765/
start "CBG Valuation Server" %PYTHON_CMD% server.py
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/"
goto end

:no_python
echo Python 3 was not found. Install it from https://www.python.org/downloads/windows/
echo During installation, enable "Add Python to PATH".
pause
goto end

:install_failed
echo Dependency installation failed. Check the network and run this file again.
pause

:end
endlocal
