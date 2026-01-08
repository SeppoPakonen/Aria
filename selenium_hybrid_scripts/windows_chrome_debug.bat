@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo WARNING: This script uses a HEURISTIC to guess the most active Chrome profile (by last-modified timestamps).
echo WARNING: Heuristics can be wrong. Double-check the chosen profile before relying on it.
echo.

if "%PORT%"=="" set "PORT=9222"

set "USERDATA=%LOCALAPPDATA%\Google\Chrome\User Data"

if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
  set "CHROME_EXE=%ProgramFiles%\Google\Chrome\Application\chrome.exe"
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
  set "CHROME_EXE=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"
) else (
  echo ERROR: chrome.exe not found in Program Files.
  echo        Set CHROME_EXE manually or install Google Chrome.
  exit /b 1
)

if not exist "%USERDATA%" (
  echo ERROR: Chrome user-data dir not found: "%USERDATA%"
  exit /b 1
)

for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command ^
  "$base = $env:LOCALAPPDATA + '\Google\Chrome\User Data';" ^
  "$cands = Get-ChildItem -Directory $base -ErrorAction SilentlyContinue |" ^
  "  Where-Object { $_.Name -eq 'Default' -or $_.Name -like 'Profile *' } |" ^
  "  Where-Object { Test-Path (Join-Path $_.FullName 'Preferences') };" ^
  "if(-not $cands){ exit 2 }" ^
  "$latest = $cands | Sort-Object { (Get-Item (Join-Path $_.FullName 'Preferences')).LastWriteTime } -Descending | Select-Object -First 1;" ^
  "Write-Output $latest.Name"`) do (
  set "PROFILE=%%P"
)

if "%PROFILE%"=="" (
  echo ERROR: Could not determine a Chrome profile folder heuristically.
  exit /b 2
)

echo Selected (heuristic^):
echo   Chrome exe     : "%CHROME_EXE%"
echo   User data dir  : "%USERDATA%"
echo   Profile dir    : "%PROFILE%"
echo   Debug port     : %PORT%
echo.
echo NOTE: Close other Chrome instances using this same profile to avoid profile lock conflicts.
echo.

start "" "%CHROME_EXE%" ^
  --remote-debugging-port=%PORT% ^
  --user-data-dir="%USERDATA%" ^
  --profile-directory="%PROFILE%" ^
  --no-first-run ^
  --no-default-browser-check