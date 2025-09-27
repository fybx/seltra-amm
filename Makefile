# Seltra AMM Development Makefile
# Based on Algorand Developer Portal: https://dev.algorand.co/

.PHONY: help setup start stop restart logs shell status clean test deploy build lint format

# Default target
help:
	@echo "Seltra AMM Development Commands"
	@echo "================================"
	@echo ""
	@echo "Environment Management:"
	@echo "  setup     - Initial setup of development environment"
	@echo "  start     - Start Docker development environment"
	@echo "  stop      - Stop Docker development environment"
	@echo "  restart   - Restart Docker development environment"
	@echo "  status    - Show status of all services"
	@echo "  clean     - Clean up containers and volumes"
	@echo ""
	@echo "Development:"
	@echo "  shell     - Enter development container"
	@echo "  logs      - Show logs from all services"
	@echo "  build     - Build development Docker image"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint      - Run code linting"
	@echo "  format    - Format code with black"
	@echo ""
	@echo "Testing & Deployment:"
	@echo "  test      - Run tests"
	@echo "  deploy    - Deploy contracts to testnet"
	@echo ""
	@echo "Documentation: https://dev.algorand.co/"

# Environment setup
setup:
	@echo "🚀 Setting up Seltra AMM development environment..."
	@./setup.sh

# LocalNet operations
start:
	@echo "🚀 Starting AlgoKit LocalNet..."
	@algokit localnet start

stop:
	@echo "🛑 Stopping AlgoKit LocalNet..."
	@algokit localnet stop

status:
	@echo "📊 LocalNet Status:"
	@algokit localnet status

clean:
	@echo "🧹 Cleaning up..."
	@algokit localnet stop

# Development
explore:
	@echo "🌐 Opening AlgoKit Explorer..."
	@algokit explore

# Code quality
lint:
	@echo "🔍 Running code linting..."
	@flake8 contracts/ simulation/ scripts/
	@mypy contracts/ simulation/

format:
	@echo "🎨 Formatting code..."
	@black contracts/ simulation/ scripts/

# Testing and deployment
test:
	@echo "🧪 Running tests..."
	@python -m pytest tests/ -v

deploy:
	@echo "🚀 Deploying contracts..."
	@python scripts/deploy.py

# Quick development cycle
dev: start explore

# Full setup for new developers
init: setup
	@echo "✅ Development environment ready!"
	@echo "Run 'algokit generate contract' to create your first contract"

# Production deployment
prod-deploy:
	@echo "🚀 Deploying to production..."
	@python scripts/deploy.py --network mainnet
