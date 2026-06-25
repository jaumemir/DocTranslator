#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================="
echo "🔄 Starting one-click update of DocTranslator"
echo "=========================================="

# 1. Pull latest code
echo "📥 Pulling latest code from GitHub..."
# If you have local modifications, this may fail. You need to handle your changes first (e.g., git stash).
git pull origin main

# 2. Stop and remove old containers (to start with new image)
echo "🧹 Cleaning up old containers..."
docker stop backend-container 2>/dev/null || true
docker rm backend-container 2>/dev/null || true
docker stop nginx-container 2>/dev/null || true
docker rm nginx-container 2>/dev/null || true

# 3. Rebuild backend image with new code
echo "🔨 Rebuilding backend Docker image..."
docker build -t doctranslator ./backend

# 4. Start backend container
echo "🌐 Starting backend container..."
docker run -d \
  --name backend-container \
  --network my-network \
  -p 5000:5000 \
  -p 5001:5001 \
  -v ./backend-storage:/app/storage \
  doctranslator

# 5. Start Nginx container
echo "🌍 Starting Nginx container..."
docker run -d \
  --name nginx-container \
  -p 1475:80 \
  -p 8081:8081 \
  -v $(pwd)/nginx/nginx.conf:/etc/nginx/conf.d/default.conf \
  -v $(pwd)/frontend/dist:/usr/share/nginx/html/frontend \
  -v $(pwd)/admin/dist:/usr/share/nginx/html/admin \
  --network my-network \
  nginx:stable-alpine

echo ""
echo "=========================================="
echo "✅ Update and redeployment complete!"
echo "=========================================="
echo "Frontend URL: http://localhost:1475"
echo "Admin URL: http://localhost:8081"
echo "Backend API: http://localhost:5000"
echo "=========================================="
