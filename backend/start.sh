#!/bin/bash

# SSME Backend Startup Script

echo "🚀 Starting SSME Backend Setup..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✏️  Please edit .env file with your configuration"
fi

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Seed the database
echo "🌱 Seeding database with sample data..."
python seed.py

# Start the server
echo "🌟 Starting Django development server..."
echo "📊 API will be available at: http://localhost:8000/api/"
echo "🔧 Admin panel: http://localhost:8000/admin/"
echo "📚 API documentation: http://localhost:8000/api/docs/"
echo ""
echo "🔑 Sample credentials:"
echo "   Admin: admin@ssme.com / admin123"
echo "   Business: business1@ssme.com / business123"
echo "   Customer: customer1@ssme.com / customer123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python manage.py runserver
