@echo off
REM Setup script for Lustra Chatbot

echo =========================================
echo Lustra Chatbot Setup
echo =========================================

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo Next steps:
echo 1. Make sure Ollama is running: ollama serve
echo 2. Run the chatbot: python chatbot.py
echo.
pause
