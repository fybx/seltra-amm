#!/bin/bash

# Seltra AMM Complete System Deployment Script
# Deploys contracts to testnet and starts the complete UI system

set -e

echo "🚀 Seltra AMM Complete System Deployment"
echo "========================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed"
    exit 1
fi

if ! command -v algokit &> /dev/null; then
    echo "❌ AlgoKit is required but not installed"
    echo "Install with: pipx install algokit"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Set up environment
echo "🔧 Setting up environment..."

if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Deploy contracts to testnet
echo "🚀 Deploying contracts to testnet..."

# Check if contracts are already deployed
if [ -f "deployment_info.json" ]; then
    echo "📄 Found existing deployment info"
    read -p "Do you want to redeploy contracts? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Redeploying contracts..."
        python scripts/deploy.py --network testnet
    else
        echo "📋 Using existing deployment"
    fi
else
    echo "🆕 First time deployment"
    python scripts/deploy.py --network testnet
fi

# Update environment with deployment info
if [ -f "deployment_info.json" ]; then
    echo "📝 Updating environment with deployment info..."
    
    # Extract contract IDs from deployment info
    POOL_APP_ID=$(python -c "import json; data=json.load(open('deployment_info.json')); print(data.get('contracts', [{}])[0].get('app_id', '1000'))")
    
    # Update .env file
    sed -i.bak "s/SELTRA_POOL_APP_ID=.*/SELTRA_POOL_APP_ID=$POOL_APP_ID/" .env
    
    echo "✅ Environment updated with contract addresses"
fi

# Build and start the complete system
echo "🐳 Building and starting the complete system..."

# Build all containers
echo "📦 Building containers..."
docker-compose build

# Start the system
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check service health
echo "🔍 Checking service health..."

# Check market simulator
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ Market Simulator is running"
else
    echo "⚠️  Market Simulator might still be starting..."
fi

# Check Next.js frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Next.js Frontend is running"
else
    echo "⚠️  Next.js Frontend might still be starting..."
fi

# Check dev console
if curl -s http://localhost:3001 > /dev/null; then
    echo "✅ Dev Console is running"
else
    echo "⚠️  Dev Console might still be starting..."
fi

echo ""
echo "🎉 Seltra AMM System Deployment Complete!"
echo "========================================"
echo ""
echo "🌐 Access Points:"
echo "  • Main Trading Interface: http://localhost:3000"
echo "  • Development Console:    http://localhost:3001"
echo "  • Market Simulator API:   http://localhost:8001"
echo ""
echo "📋 System Information:"
echo "  • Network: TestNet"
echo "  • Pool App ID: $POOL_APP_ID"
echo "  • Asset X (ALGO): 0"
echo "  • Asset Y (HACK): 1008"
echo ""
echo "🔧 Management Commands:"
echo "  • View logs:        docker-compose logs -f [service]"
echo "  • Restart service:  docker-compose restart [service]"
echo "  • Stop system:      docker-compose down"
echo "  • Update system:    docker-compose pull && docker-compose up -d"
echo ""
echo "📱 Wallet Setup:"
echo "  1. Install Pera Wallet on your device"
echo "  2. Create or import a wallet"
echo "  3. Switch to TestNet in wallet settings"
echo "  4. Get TestNet ALGO from: https://testnet.algoexplorer.io/dispenser"
echo "  5. Connect wallet in the frontend"
echo ""
echo "🎯 Next Steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Connect your Pera Wallet"
echo "  3. Start trading and providing liquidity!"
echo ""
echo "Happy trading! 🚀"
