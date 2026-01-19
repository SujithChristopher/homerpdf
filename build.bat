@echo off
REM Hospital PDF Manager - Windows Build Script
REM Usage: build.bat [clean|rebuild|help]

setlocal enabledelayedexpansion

REM Color codes for output
set "HEADER=[Build]"
set "SUCCESS=[OK]"
set "ERROR=[ERROR]"

:parse_args
if "%~1"=="" goto main
if /i "%~1"=="clean" (
    set "CLEAN_BUILD=1"
    shift
    goto parse_args
)
if /i "%~1"=="rebuild" (
    set "CLEAN_BUILD=1"
    set "BUILD=1"
    shift
    goto parse_args
)
if /i "%~1"=="help" (
    goto show_help
)
shift
goto parse_args

:show_help
echo.
echo Hospital PDF Manager - Windows Build Script
echo.
echo Usage:
echo   build.bat              - Build executable
echo   build.bat clean        - Remove build artifacts
echo   build.bat rebuild      - Clean and rebuild
echo   build.bat help         - Show this help
echo.
exit /b 0

:main
cls
echo.
echo ========================================================================
echo   Hospital PDF Manager - Windows Build
echo ========================================================================
echo.

REM Check Python installation
echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Python is not installed or not in PATH
    echo Visit: https://www.python.org/downloads/
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo %SUCCESS% Found !PYTHON_VERSION!
echo.

REM Check dependencies
echo [*] Checking dependencies...
python -m pip list 2>nul | findstr /i "pyinstaller" >nul
if errorlevel 1 (
    echo %ERROR% PyInstaller not installed
    echo Installing build dependencies...
    call python -m pip install -e ".[build]" || goto error
)
echo %SUCCESS% Dependencies are installed
echo.

REM Clean if requested
if "%CLEAN_BUILD%"=="1" (
    echo [*] Cleaning build artifacts...
    if exist dist\ (
        rmdir /s /q dist >nul 2>&1
        echo %SUCCESS% Removed dist/ directory
    )
    if exist build\ (
        rmdir /s /q build >nul 2>&1
        echo %SUCCESS% Removed build/ directory
    )
    if exist "Hospital PDF Manager"\ (
        rmdir /s /q "Hospital PDF Manager" >nul 2>&1
        echo %SUCCESS% Removed Hospital PDF Manager/ directory
    )
    echo.
)

REM Build executable
echo [*] Building executable with PyInstaller...
python -m PyInstaller --onedir homerpdf.spec
if errorlevel 1 (
    echo %ERROR% PyInstaller failed
    goto error
)
echo %SUCCESS% Build completed
echo.

REM Verify build
echo [*] Verifying build...
if exist "dist\Hospital PDF Manager\Hospital PDF Manager.exe" (
    echo %SUCCESS% Executable created: dist\Hospital PDF Manager\Hospital PDF Manager.exe
    for /f %%A in ('dir /b /s "dist\Hospital PDF Manager\Hospital PDF Manager.exe"') do (
        for /F "usebackq" %%B in ('%%A') do set /A EXE_SIZE=%%~zB/1024
        echo %SUCCESS% Executable size: !EXE_SIZE! KB
    )
    echo.
) else (
    echo %ERROR% Executable not found
    goto error
)

REM Show build info
echo ========================================================================
echo   Build Complete
echo ========================================================================
echo.
echo Build location: %cd%\dist
echo.
echo Files created:
dir /s /b dist\
echo.
echo To run the application:
echo   dist\Hospital PDF Manager\Hospital PDF Manager.exe
echo.
goto end

:error
echo.
echo ========================================================================
echo   Build Failed
echo ========================================================================
echo.
exit /b 1

:end
endlocal
exit /b 0
