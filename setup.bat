@echo off
echo ======================================================
echo Ung dung Blog Flask - Script cai dat
echo ======================================================

rem Kiem tra Python
python --version
if %errorlevel% neq 0 (
    echo Python chua duoc cai dat hoac khong co trong PATH
    pause
    exit /b 1
)

rem Tao moi truong ao
echo Dang tao moi truong ao...
python -m venv venv
call venv\Scripts\activate.bat

rem Nang cap pip
echo Dang nang cap pip...
python -m pip install --upgrade pip

rem Cai dat cac thu vien
echo Dang cai dat cac thu vien phu thuoc...
pip install flask flask-sqlalchemy flask-login flask-wtf wtforms email-validator

rem Khoi tao database
echo Dang khoi tao co so du lieu...
python -c "from app import app, db; from models import User; from werkzeug.security import generate_password_hash; with app.app_context(): db.create_all()"

echo ======================================================
echo Cai dat hoan tat!
echo De chay ung dung:
echo 1. Kich hoat moi truong ao: venv\Scripts\activate
echo 2. Khoi dong may chu: python app.py
echo 3. Truy cap: http://127.0.0.1:5000
echo ======================================================

pause