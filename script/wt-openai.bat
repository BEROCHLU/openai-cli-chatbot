@echo off
set PWSH_CMD=cd ..; python chatbot-openai.py
wt -d . --title "chatbot-openai" pwsh -NoExit -Command "Invoke-Expression $env:PWSH_CMD"