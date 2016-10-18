REM This script is only executed on Windows environment
copy  ..\bin\ChainChronicleDecode.exe resource\
cd resource
ChainChronicleDecode.exe

del *.scr
del *.exe
copy *.jpg ..\..\img\

cd ..\
python resize_image.py ..\img
pause
