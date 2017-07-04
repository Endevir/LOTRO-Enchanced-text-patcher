echo Сборка файлов. Требует python 2.7, WxPython, Pyinstaller
echo Сборка Enchanced.exe
pyinstaller --onefile main.spec
echo Сборка healer.exe
pyinstaller --onefile HEALER.spec
pause