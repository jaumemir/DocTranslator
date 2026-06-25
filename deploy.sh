#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================="
echo "🚀 Starting one-click deployment of DocTranslator"
echo "=========================================="

# 1. Check and create Docker network
echo "📡 Checking Docker network..."
if ! docker network ls | grep -q my-network; then
  echo "   -> Creating network my-network..."
  docker network create my-network
else
  echo "   -> Network my-network already exists, skipping creation."
fi

# 2. Create local storage directory
echo "📁 Creating local storage directory..."
mkdir -p ./backend-storage

# 3. Stop and remove old containers (if they exist, to avoid conflicts)
echo "🧹 Cleaning up old containers..."
docker stop backend-container 2>/dev/null || true
docker rm backend-container 2>/dev/null || true
docker stop nginx-container 2>/dev/null || true
docker rm nginx-container 2>/dev/null || true

# 4. Build backend image
echo "🔨 Building backend Docker image..."
docker build -t doctranslator ./backend

# 5. Start backend container
echo "🌐 Starting backend container..."
docker run -d \
  --name backend-container \
  --network my-network \
  -p 5000:5000 \
  -p 5001:5001 \
  -v ./backend-storage:/app/storage \
  doctranslator

# 6. Start Nginx container
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
echo "✅ Deployment complete!"
echo "=========================================="
echo "Frontend URL: http://localhost:1475"
echo "Admin URL: http://localhost:8081"
echo "Backend API: http://localhost:5000"
echo "=========================================="
echo ""
echo "📌 Tips:"
echo "   - Use this script for initial deployment."
echo "   - Use './update.sh' script for daily updates."
