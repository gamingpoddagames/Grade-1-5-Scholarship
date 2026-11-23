@echo off
setlocal EnableExtensions
title Punchi Nena Maga - Secure YouTube Setup
cd /d "%~dp0\.."

echo.
echo ==========================================
echo Punchi Nena Maga YouTube Shorts Setup
echo Channel: UCQ2EM8DjUfg3WgzB8r6hYDQ
echo ==========================================
echo.
echo This setup asks Google to authorize the YouTube channel in your browser.
echo OAuth tokens go directly to your private GitHub Actions Secrets.
echo Never send OAuth JSON files or tokens through Facebook, Telegram or chat.
echo.
where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Install Python first.
  pause
  exit /b 1
)
where gh >nul 2>nul
if errorlevel 1 (
  echo ERROR: Install GitHub CLI from https://cli.github.com/
  echo Then run: gh auth login
  pause
  exit /b 1
)
set "CLIENT_JSON=%~1"
if not defined CLIENT_JSON (
  echo In Google Cloud create an OAuth client of type Desktop App.
  echo Save the downloaded client_secret JSON on your PC.
  set /p "CLIENT_JSON=Enter the full path to that downloaded JSON file: "
)
if not exist "%CLIENT_JSON%" (
  echo ERROR: Cannot find OAuth client JSON at the supplied path.
  pause
  exit /b 1
)
python -m pip install --disable-pip-version-check "google-api-python-client>=2.150,<3" "google-auth-oauthlib>=1.2,<2"
if errorlevel 1 (
  echo ERROR: Could not install Google OAuth dependencies.
  pause
  exit /b 1
)
python "school\youtube_oauth_setup.py" --client-secrets "%CLIENT_JSON%" --enable-private-test
if errorlevel 1 (
  echo ERROR: Setup failed. Check the message above; no public video was uploaded.
  pause
  exit /b 1
)
echo.
echo YouTube private-upload credentials configured!
echo Next open the GitHub Actions YouTube Shorts workflow for a private test.
echo https://github.com/gamingpoddagames/Grade-1-5-Scholarship/actions/workflows/youtube-shorts.yml
pause
