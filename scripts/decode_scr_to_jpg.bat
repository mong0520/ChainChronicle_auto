cd ..\bin
ChainChronicleDecode.exe

del *.scr
move *.jpg ..\img

cd ..\scripts
python resize_image.py ..\img
pause
