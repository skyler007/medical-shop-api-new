@echo off
echo ========================================
echo Medical Shop Management System
echo ========================================
echo.

echo [1/4] Activating virtual environment...
call venv\Scripts\activate

echo [2/4] Checking database...
python -c "from app.database import engine; from app import models; models.Base.metadata.create_all(bind=engine); print('Database tables created/verified')"

echo [3/4] Starting server...
echo.
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py
