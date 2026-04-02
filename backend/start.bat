@echo off
REM SSME Backend Startup Script for Windows

echo 🚀 Starting SSME Backend Setup...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚙️  Creating .env file from template...
    copy .env.example .env
    echo ✏️  Please edit .env file with your configuration
)

REM Run migrations
echo 🗄️  Running database migrations...
python manage.py makemigrations
python manage.py migrate

REM Seed the database
echo 🌱 Seeding database with sample data...
python seed.py

REM Start the server
echo 🌟 Starting Django development server...
echo 📊 API will be available at: http://localhost:8000/api/
echo 🔧 Admin panel: http://localhost:8000/admin/
echo 📚 API documentation: http://localhost:8000/api/docs/
echo.
echo 🔑 Sample credentials:
echo    Admin: admin@ssme.com / admin123
echo    Business: business1@ssme.com / business123
echo    Customer: customer1@ssme.com / customer123
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver

pause
