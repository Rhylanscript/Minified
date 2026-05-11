@echo off
title Build Project

echo =============================
echo      Cleaning old builds
echo =============================

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo =============================
echo   Building with PyInstaller
echo =============================

pyinstaller --clean __main__.spec

echo.

if %errorlevel% neq 0 (
   echo Build failed.
   pause
   exit /b
)

echo =============================
echo        Build Complete
echo =============================

echo Executable located in:
echo dist\minified.exe

pause