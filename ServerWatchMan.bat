@echo off
cd /d %~dp0

REM ---------------------------------------------------------------------
REM ストレージ系
set SMART_FOLDER=Smart
set CRYSTALDISKINFO_PATH=C:\Program Files\CrystalDiskInfo
set CDI_SMART_FOLDER=%CRYSTALDISKINFO_PATH%\%SMART_FOLDER%
set CDI_EXE=%CRYSTALDISKINFO_PATH%\DiskInfo32.exe
set CDI_OPT=/CopyExit
set CDI_DISKINFO=DiskInfo.txt
REM 出力
set OUTPUT_FOLDER=output
set STORAGE_INFO=StorageInfo.csv
set GOOGLE_DRIVE=G:\マイドライブ\サーバー監視君用スクショ置き場
REM 環境
set ENV=

REM ---------------------------------------------------------------------
REM ストレージのSmart情報を取得
call "%CDI_EXE%" %CDI_OPT%

REM ---------------------------------------------------------------------
REM Smart情報をコピー
robocopy "%CDI_SMART_FOLDER%" ".\%SMART_FOLDER%" /R:3 /W:5 /DCOPY:DAT /NP /MIR
copy /y "%CRYSTALDISKINFO_PATH%\%CDI_DISKINFO%" ".\%SMART_FOLDER%\%CDI_DISKINFO%"

REM ---------------------------------------------------------------------
REM ストレージの空き情報を取得
if not exist "%OUTPUT_FOLDER%" (
 md "%OUTPUT_FOLDER%"
)
@powershell -NoProfile -ExecutionPolicy RemoteSigned ".\Collect-StorageInfo.ps1 '%OUTPUT_FOLDER%\%STORAGE_INFO%'" 

REM ---------------------------------------------------------------------
REM 収集した情報をもとにグラフなどを作成する
call venv\Scripts\activate.bat & python CreateServerStatus.py "%OUTPUT_FOLDER%" "%OUTPUT_FOLDER%\%STORAGE_INFO%" "%SMART_FOLDER%" "%CDI_DISKINFO%" "%ENV%"

REM ---------------------------------------------------------------------
REM 作成した情報をGoogle Driveにコピー
copy /y %OUTPUT_FOLDER%\%ENV%StorageInfo.png %GOOGLE_DRIVE%
copy /y %OUTPUT_FOLDER%\%ENV%report_*.png %GOOGLE_DRIVE%

REM ---------------------------------------------------------------------
REM LINEに画像を送信
@powershell -NoProfile -ExecutionPolicy RemoteSigned ".\Send-LineMessage.ps1"
