@echo off
cd /d %~dp0

REM ---------------------------------------------------------------------
REM �X�g���[�W�n
set SMART_FOLDER=Smart
set CRYSTALDISKINFO_PATH=C:\Program Files\CrystalDiskInfo
set CDI_SMART_FOLDER=%CRYSTALDISKINFO_PATH%\%SMART_FOLDER%
set CDI_EXE=%CRYSTALDISKINFO_PATH%\DiskInfo32.exe
set CDI_OPT=/CopyExit
set CDI_DISKINFO=DiskInfo.txt
REM �o��
set OUTPUT_FOLDER=output
set STORAGE_INFO=StorageInfo.csv
set GOOGLE_DRIVE=G:\�}�C�h���C�u\�T�[�o�[�Ď��N�p�X�N�V���u����
REM ��
set ENV=

REM ---------------------------------------------------------------------
REM �X�g���[�W��Smart�����擾
call "%CDI_EXE%" %CDI_OPT%

REM ---------------------------------------------------------------------
REM Smart�����R�s�[
robocopy "%CDI_SMART_FOLDER%" ".\%SMART_FOLDER%" /R:3 /W:5 /DCOPY:DAT /NP /MIR
copy /y "%CRYSTALDISKINFO_PATH%\%CDI_DISKINFO%" ".\%SMART_FOLDER%\%CDI_DISKINFO%"

REM ---------------------------------------------------------------------
REM �X�g���[�W�̋󂫏����擾
if not exist "%OUTPUT_FOLDER%" (
 md "%OUTPUT_FOLDER%"
)
@powershell -NoProfile -ExecutionPolicy RemoteSigned ".\Collect-StorageInfo.ps1 '%OUTPUT_FOLDER%\%STORAGE_INFO%'" 

REM ---------------------------------------------------------------------
REM ���W�����������ƂɃO���t�Ȃǂ��쐬����
call venv\Scripts\activate.bat & python CreateServerStatus.py "%OUTPUT_FOLDER%" "%OUTPUT_FOLDER%\%STORAGE_INFO%" "%SMART_FOLDER%" "%CDI_DISKINFO%" "%ENV%"

REM ---------------------------------------------------------------------
REM �쐬��������Google Drive�ɃR�s�[
copy /y %OUTPUT_FOLDER%\%ENV%StorageInfo.png %GOOGLE_DRIVE%
copy /y %OUTPUT_FOLDER%\%ENV%report_*.png %GOOGLE_DRIVE%

REM ---------------------------------------------------------------------
REM LINE�ɉ摜�𑗐M
@powershell -NoProfile -ExecutionPolicy RemoteSigned ".\Send-LineMessage.ps1"
