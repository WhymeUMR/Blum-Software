@echo off

:: Установка необходимых библиотек
pip install pyautogui
pip install pynput
pip install pygetwindow
pip install keyboard

:: Проверка установки библиотек
pip list pyautogui pynput pygetwindow keyboard > nul 2>&1
if %errorlevel% equ 0 (
    echo Все библиотеки установлены успешно.
    :: Запуск файла Blum.py
    start "" python Blum.py
    exit
) else (
    echo Ошибка установки библиотек.
    pause
    exit
)