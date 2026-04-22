#!/bin/bash

# 🚀 E-commerce Server Startup Script
# Run this to start your Django server

echo "🚀 Starting E-commerce Server..."
echo ""

# Navigate to project directory
cd /Users/vilas/Documents/Project/E-commerce

# Activate virtual environment
source venv/bin/activate

# Run Django server
python manage.py runserver 8000

# Server will start at http://localhost:8000
