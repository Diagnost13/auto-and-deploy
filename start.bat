@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo Запуск генерации данных...
echo ========================================
call venv\Scripts\python.exe Upload_generation.py --shops 5 --max-cash 3
if errorlevel 1 (
    echo Ошибка при генерации! Завершение работы.
    exit /b 1
)

echo.
echo ========================================
echo Запуск загрузчика (run.py)...
echo ========================================
call venv\Scripts\python.exe run.py
if errorlevel 1 (
    echo Ошибка при загрузке!
    exit /b 1
)

echo.
echo ========================================
echo Все операции выполнены успешно.
echo ========================================
timeout /t 5