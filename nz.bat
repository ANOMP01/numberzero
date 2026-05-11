@echo off
REM numberzero shortcut for Windows.
REM Usage:
REM   nz                     (interactive mode)
REM   nz -t "Halo" -m img    (flag mode, same flags as `python -m src.cli`)

setlocal
cd /d "%~dp0"

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    python -m src.cli %*
) else (
    where py >nul 2>nul
    if %ERRORLEVEL%==0 (
        py -3 -m src.cli %*
    ) else (
        echo Error: Python tidak ditemukan. Install Python 3 dulu.
        exit /b 1
    )
)
endlocal
