@echo off
setlocal EnableExtensions EnableDelayedExpansion

echo WARNING: This script uses a HEURISTIC to guess the most active Firefox profile (by last-modified timestamps).
echo WARNING: Heuristics can be wrong. Double-check the chosen profile before relying on it.
echo.

set "PROFILES=%APPDATA%\Mozilla\Firefox\Profiles"

if exist "%ProgramFiles%\Mozilla Firefox\firefox.exe" (
  set "FIREFOX_EXE=%ProgramFiles%\Mozilla Firefox\firefox.exe"
) else if exist "%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe" (
  set "FIREFOX_EXE=%ProgramFiles(x86)%\Mozilla Firefox\firefox.exe"
) else (
  echo ERROR: firefox.exe not found in Program Files.
  echo        Set FIREFOX_EXE manually or install Mozilla Firefox.
  exit /b 1
)

if not exist "%PROFILES%" (
  echo ERROR: Firefox profiles dir not found: "%PROFILES%"
  exit /b 1
)

for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command ^
  "$base = $env:APPDATA + '\Mozilla\Firefox\Profiles';" ^
  "$cands = Get-ChildItem -Directory $base -ErrorAction SilentlyContinue |" ^
  "  Where-Object { Test-Path (Join-Path $_.FullName 'prefs.js') };" ^
  "if(-not $cands){ exit 2 }" ^
  "$latest = $cands | Sort-Object { (Get-Item (Join-Path $_.FullName 'prefs.js')).LastWriteTime } -Descending | Select-Object -First 1;" ^
  "Write-Output $latest.FullName"`) do (
  set "PROFILEPATH=%%P"
)

if "%PROFILEPATH%"=="" (
  echo ERROR: Could not determine a Firefox profile folder heuristically.
  exit /b 2
)

echo Selected (heuristic^):
echo   Firefox exe   : "%FIREFOX_EXE%"
echo   Profile path  : "%PROFILEPATH%"
echo.
echo NOTE: This launches Firefox with --marionette for Selenium/geckodriver 'connect existing' workflows.
echo NOTE: Close other Firefox instances if you hit profile lock conflicts.
echo.

start "" "%FIREFOX_EXE%" -no-remote -profile "%PROFILEPATH%" --marionette
