@echo off
set PWSH_CMD=cd ..; python clichatbot.py
wt -d . --title "clichatbot" pwsh -NoExit -Command "Invoke-Expression $env:PWSH_CMD"