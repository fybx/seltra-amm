#!/bin/bash

# Seltra Dev Console Quick Start Script

set -e

echo "🚀 Starting Seltra Development Console..."
echo

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

echo "📦 Starting required services..."
echo

# Start the simulation services first
echo "Starting Algorand node..."
docker-compose up -d postgres algod indexer

echo "Waiting for Algorand node to initialize..."
sleep 10

echo "Starting market simulator..."
docker-compose up -d market-simulator

echo "Starting dev frontend..."
docker-compose up -d dev-frontend

echo
echo "🎯 Services started successfully!"
echo
echo "📊 Dev Console: http://localhost:3001"
echo "🔗 API Health:  http://localhost:8001/health"
echo "📖 API Docs:    http://localhost:8001/docs"
echo

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service health
echo "🔍 Checking service health..."
echo

if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Simulation API is healthy"
else
    echo "⚠️  Simulation API might still be starting..."
fi

if curl -s http://localhost:3001 > /dev/null; then
    echo "✅ Dev Console is accessible"
else
    echo "⚠️  Dev Console might still be starting..."
fi

echo
echo "🎉 Development environment is ready!"
echo
echo "Available commands:"
echo "  docker-compose logs dev-frontend     # View frontend logs"
echo "  docker-compose logs market-simulator # View simulation logs"
echo "  docker-compose stop                  # Stop all services"
echo "  docker-compose down                  # Stop and remove containers"
echo
echo "Happy developing! 🛠️"
