#!/bin/bash

# Development helper script for Seltra AMM

set -e

case "$1" in
    "start")
        echo "🚀 Starting Seltra AMM development environment..."
        docker-compose up -d
        echo "✅ Environment started!"
        echo "Run 'docker-compose exec algokit-dev bash' to enter development container"
        ;;
    "stop")
        echo "🛑 Stopping development environment..."
        docker-compose down
        echo "✅ Environment stopped!"
        ;;
    "restart")
        echo "🔄 Restarting development environment..."
        docker-compose down
        docker-compose up -d
        echo "✅ Environment restarted!"
        ;;
    "logs")
        echo "📋 Showing logs..."
        docker-compose logs -f
        ;;
    "shell")
        echo "🐚 Entering development container..."
        docker-compose exec algokit-dev bash
        ;;
    "status")
        echo "📊 Environment status:"
        docker-compose ps
        echo ""
        echo "🔍 Algorand node status:"
        docker-compose exec algorand-node goal node status -d /opt/algorand/node/data || echo "Node not ready"
        ;;
    "clean")
        echo "🧹 Cleaning up..."
        docker-compose down -v
        docker system prune -f
        echo "✅ Cleanup complete!"
        ;;
    "test")
        echo "🧪 Running tests..."
        docker-compose exec algokit-dev python -m pytest tests/ -v
        ;;
    "deploy")
        echo "🚀 Deploying contracts..."
        docker-compose exec algokit-dev python scripts/deploy.py
        ;;
    *)
        echo "Seltra AMM Development Helper"
        echo ""
        echo "Usage: $0 {start|stop|restart|logs|shell|status|clean|test|deploy}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the development environment"
        echo "  stop     - Stop the development environment"
        echo "  restart  - Restart the development environment"
        echo "  logs     - Show logs from all services"
        echo "  shell    - Enter the development container"
        echo "  status   - Show status of all services"
        echo "  clean    - Clean up containers and volumes"
        echo "  test     - Run tests"
        echo "  deploy   - Deploy contracts to testnet"
        ;;
esac
