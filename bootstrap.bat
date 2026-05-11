@echo off
title Project Setup

echo =========================
echo Installing Python Modules
echo =========================
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo Failed to install python dependencies
    pause
    exit /b
)

echo.
where esbuild >nul 2>nul

if %errorlevel% neq 0 (
    echo =========================
    echo    Installing esbuild
    echo =========================

    npm install -g esbuild

    if %errorlevel% neq 0 (
        echo.
        echo Failed to install esbuild
        echo Make sure Node.js is installed:
        echo https://nodejs.org/
        pause
        exit /b
    )
) else (
    echo esbuild already installed.
)

echo.
echo =========================
echo      Setup Complete!
echo =========================

pause