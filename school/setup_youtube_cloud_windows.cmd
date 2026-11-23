@echo off
setlocal EnableExtensions
chcp 65001 >nul
title Punchi Nena Maga - Complete Google Cloud and YouTube Setup
cd /d "%~dp0\.."

echo.
echo ==================================================
echo  PUNCHI NENA MAGA - YOUTUBE AUTO UPLOAD SETUP
echo  Verified YouTube channel:
echo  UCQ2EM8DjUfg3WgzB8r6hYDQ
echo ==================================================
echo.
echo This program will:
echo  - Sign in to Google Cloud using your own browser
echo  - Create/reuse the dedicated mfk110 YouTube Upload Project
echo  - Enable YouTube Data API v3
echo  - Open Google Auth Platform for a Desktop OAuth client
echo  - Save verified OAuth secrets directly into GitHub Actions
echo  - Enable PRIVATE test upload only; never PUBLIC by default
echo.
echo Do NOT share passwords, verification codes or OAuth JSON files.
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python and reopen Command Prompt.
  pause
  exit /b 1
)

call :find_gcloud
if not defined GCLOUD_BIN (
  echo Google Cloud CLI is not installed.
  where winget >nul 2>nul
  if errorlevel 1 (
    echo Please install Google Cloud CLI from:
    echo https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
  )
  choice /C YN /M "Install official Google Cloud CLI via winget now"
  if errorlevel 2 (
    echo Installation declined; nothing changed.
    pause
    exit /b 1
  )
  winget install --id Google.CloudSDK -e --accept-package-agreements --accept-source-agreements
  if errorlevel 1 (
    echo Google Cloud CLI installation did not complete.
    pause
    exit /b 1
  )
  call :find_gcloud
  if not defined GCLOUD_BIN (
    echo Google Cloud CLI installed but this terminal has not refreshed its PATH.
    echo Close this terminal, open Command Prompt again and rerun this file.
    pause
    exit /b 1
  )
)

where gh >nul 2>nul
if errorlevel 1 (
  echo GitHub CLI is missing; it is needed to store OAuth secrets securely.
  where winget >nul 2>nul
  if errorlevel 1 (
    echo Install GitHub CLI from https://cli.github.com/ and reopen this file.
    pause
    exit /b 1
  )
  choice /C YN /M "Install official GitHub CLI via winget now"
  if errorlevel 2 (
    echo Installation declined. No GitHub secrets were changed.
    pause
    exit /b 1
  )
  winget install --id GitHub.cli -e --accept-package-agreements --accept-source-agreements
  if errorlevel 1 (
    echo GitHub CLI installation failed. No credentials were saved.
    pause
    exit /b 1
  )
  if exist "%ProgramFiles%\GitHub CLI\gh.exe" set "PATH=%ProgramFiles%\GitHub CLI;%PATH%"
  where gh >nul 2>nul
  if errorlevel 1 (
    echo Reopen Command Prompt and run this script again after installation.
    pause
    exit /b 1
  )
)
gh auth status >nul 2>nul
if errorlevel 1 (
  echo Opening GitHub CLI authentication (browser approval may be required)...
  gh auth login
  if errorlevel 1 (
    echo GitHub login did not complete. No OAuth secrets were written.
    pause
    exit /b 1
  )
)

echo Verifying free Python Google API libraries...
python -m pip install --disable-pip-version-check "google-api-python-client>=2.150,<3" "google-auth-oauthlib>=1.2,<2"
if errorlevel 1 (
  echo Failed to install required Python libraries.
  pause
  exit /b 1
)

echo.
echo Starting Google Cloud setup...
python "school\youtube_cloud_bootstrap.py" %*
if errorlevel 1 (
  echo.
  echo Setup stopped. Review the error above.
  echo No public YouTube video was uploaded by this script.
  pause
  exit /b 1
)

echo.
echo Google Cloud setup completed.
echo If you skipped OAuth JSON selection, reopen this file after creating
echo the Google Auth Platform Desktop OAuth client. Project ID is saved locally.
echo.
pause
exit /b 0

:find_gcloud
set "GCLOUD_BIN="
for %%G in (gcloud.cmd gcloud.exe) do (
  if not defined GCLOUD_BIN (
    for /F "delims=" %%P in ('where %%G 2^>nul') do if not defined GCLOUD_BIN set "GCLOUD_BIN=%%P"
  )
)
if defined GCLOUD_BIN exit /b 0
if exist "%LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" (
  set "PATH=%LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin;%PATH%"
  set "GCLOUD_BIN=%LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
)
if exist "%ProgramFiles(x86)%\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" (
  set "PATH=%ProgramFiles(x86)%\Google\Cloud SDK\google-cloud-sdk\bin;%PATH%"
  set "GCLOUD_BIN=%ProgramFiles(x86)%\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
)
if exist "%ProgramFiles%\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd" (
  set "PATH=%ProgramFiles%\Google\Cloud SDK\google-cloud-sdk\bin;%PATH%"
  set "GCLOUD_BIN=%ProgramFiles%\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
)
exit /b 0
