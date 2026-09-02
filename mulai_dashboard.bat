@echo off
setlocal
cd /d "%~dp0"

set "METEROPS_PYTHON=py"
where py >nul 2>nul
if errorlevel 1 set "METEROPS_PYTHON=python"

%METEROPS_PYTHON% --version >nul 2>nul
if errorlevel 1 (
    echo Python belum ditemukan. Instal Python 3.11 atau lebih baru terlebih dahulu.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Membuat virtual environment...
    %METEROPS_PYTHON% -m venv .venv
    if errorlevel 1 goto :error
)

call ".venv\Scripts\activate.bat"
echo Memeriksa dependensi...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Menjalankan Dashboard Monitoring Gangguan...
python -m streamlit run app.py
goto :end

:error
echo Proses gagal. Periksa pesan kesalahan di atas.
pause
exit /b 1

:end
endlocal
