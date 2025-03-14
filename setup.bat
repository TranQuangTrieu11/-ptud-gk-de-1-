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
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Khong tim thay file requirements.txt, dang cai dat thu vien thay the...
    pip install flask flask-sqlalchemy flask-login flask-wtf wtforms email-validator
)

rem Tao thu muc instance
echo Dang tao thu muc instance...
mkdir instance 2>nul

rem Khoi tao database
echo Dang khoi tao co so du lieu...
python -c "from app import app, db; from models import User; from werkzeug.security import generate_password_hash; with app.app_context(): db.create_all(); admin = User.query.filter_by(username='admin').first(); print('Admin da ton tai' if admin else 'Tao admin moi'); admin = User(username='admin', email='admin@example.com', password_hash=generate_password_hash('admin123'), is_admin=True) if not admin else admin; db.session.add(admin) if not User.query.filter_by(username='admin').first() else None; db.session.commit()"

echo ======================================================
echo Cai dat hoan tat!
echo De chay ung dung:
echo 1. Kich hoat moi truong ao: venv\Scripts\activate
echo 2. Khoi dong may chu: python app.py
echo 3. Truy cap: http://127.0.0.1:5000
echo ======================================================

pause