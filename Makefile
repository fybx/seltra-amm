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
	@chmod +x scripts/*.sh
	@./scripts/setup.sh

# Docker operations
start:
	@echo "🚀 Starting development environment..."
	@./scripts/dev.sh start

stop:
	@echo "🛑 Stopping development environment..."
	@./scripts/dev.sh stop

restart:
	@echo "🔄 Restarting development environment..."
	@./scripts/dev.sh restart

status:
	@./scripts/dev.sh status

clean:
	@echo "🧹 Cleaning up..."
	@./scripts/dev.sh clean

# Development
shell:
	@./scripts/dev.sh shell

logs:
	@./scripts/dev.sh logs

build:
	@echo "🔨 Building development Docker image..."
	@docker-compose build algokit-dev

# Code quality
lint:
	@echo "🔍 Running code linting..."
	@docker-compose exec algokit-dev flake8 contracts/ simulation/ scripts/
	@docker-compose exec algokit-dev mypy contracts/ simulation/

format:
	@echo "🎨 Formatting code..."
	@docker-compose exec algokit-dev black contracts/ simulation/ scripts/

# Testing and deployment
test:
	@echo "🧪 Running tests..."
	@./scripts/dev.sh test

deploy:
	@echo "🚀 Deploying contracts..."
	@./scripts/dev.sh deploy

# Quick development cycle
dev: start shell

# Full setup for new developers
init: setup start
	@echo "✅ Development environment ready!"
	@echo "Run 'make shell' to enter the development container"

# Production deployment
prod-deploy:
	@echo "🚀 Deploying to production..."
	@docker-compose exec algokit-dev python scripts/deploy.py --network mainnet
