mode 100,30
echo ""
echo "BRS AUTOMATION ANIM-PRODUCTION"
echo %~dp0main.py
timeout /t 1
"%~dp0src\python-3.7.0-embed-amd64\python.exe" "%~dp0main.py"
#timeout /t 30
pause
