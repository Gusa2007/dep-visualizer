@echo off
rem Запуск визуализатора в Windows. Аргументы передаются приложению.
cd /d "%~dp0"
python src\main.py %*
