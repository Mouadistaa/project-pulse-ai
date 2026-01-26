# Init Script for Project Pulse AI

Write-Host "Starting Docker Compose..."
docker-compose up -d --build

Write-Host "Waiting for services to be ready..."
Start-Sleep -Seconds 10

Write-Host "Running Database Migrations..."
docker-compose exec backend alembic upgrade head

Write-Host "Seeding Data..."
docker-compose exec backend python scripts/seed.py

Write-Host "Initialization Complete! Access Frontend at http://localhost:3000"
