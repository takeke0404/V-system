@echo off

cd /d %~dp0

python .\editor_manager.py

if %errorlevel% neq 0 (
    pause
)
