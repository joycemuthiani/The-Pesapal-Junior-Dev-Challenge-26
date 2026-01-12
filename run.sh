#!/bin/bash
# Simple run script for PyRelDB

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║         Pesapal Challenge '26               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose not found. Please install docker-compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "Docker detected"
echo ""
echo "🔨 Building and starting application..."
echo ""

# Build and start
docker-compose up --build -d

# Wait for health check
echo ""
echo "⏳ Waiting for application to be ready..."
sleep 5

# Check if running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║              🎉 SUCCESS! Application is running        ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 Dashboard:     http://localhost:8080"
    echo "🔍 SQL Console:   http://localhost:8080 (then click SQL Console tab)"
    echo "📡 API Health:    http://localhost:8080/api/health"
    echo ""
    echo "View logs:     docker-compose logs -f"
    echo "Stop app:      docker-compose down"
    echo ""
    echo "Happy testing!"
else
    echo ""
    echo "Application failed to start. Check logs:"
    echo "   docker-compose logs"
    exit 1
fi

