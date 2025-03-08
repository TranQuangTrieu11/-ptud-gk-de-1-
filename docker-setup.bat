@echo off
echo ===== Khoi tao Docker Container cho Flask Blog =====

where docker >nul 2>nul
if %errorlevel% neq 0 (
  echo Docker chua duoc cai dat! Vui long cai dat Docker truoc.
  pause
  exit /b 1
)

echo Building Docker image...
docker-compose build

echo Khoi dong container...
docker-compose up -d

echo ===== Hoan tat! =====
echo Ung dung da duoc khoi chay tai: http://localhost:5000
echo De dung ung dung, hay chay: docker-compose down
pause