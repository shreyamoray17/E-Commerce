#!/bin/bash

echo "🚀 Starting E-commerce Platform Setup..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

echo "📦 Building Docker containers..."
docker-compose build

echo ""
echo "🚀 Starting containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for MySQL to be ready..."
sleep 10

echo ""
echo "🔄 Running database migrations..."
docker-compose exec web python manage.py migrate

echo ""
echo "👤 Creating superuser..."
echo "Email: admin@example.com"
echo "Password: admin123"
docker-compose exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print('Superuser created successfully!')
else:
    print('Superuser already exists!')
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Access points:"
echo "   - API Root: http://localhost:8000/"
echo "   - Swagger UI: http://localhost:8000/swagger/"
echo "   - Admin Panel: http://localhost:8000/admin/"
echo ""
echo "🔐 Admin credentials:"
echo "   Email: admin@example.com"
echo "   Password: admin123"
echo ""
echo "📝 To stop: docker-compose down"
echo "📝 To view logs: docker-compose logs -f"
