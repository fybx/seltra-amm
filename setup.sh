#!/bin/bash

# Seltra AMM - Development Environment Setup
# Based on Algorand Developer Portal: https://dev.algorand.co/

set -e

echo "🚀 Setting up Seltra AMM Development Environment..."

# Check if AlgoKit is installed
if ! command -v algokit &> /dev/null; then
    echo "📦 Installing AlgoKit..."
    if ! command -v pipx &> /dev/null; then
        echo "Installing pipx..."
        pip install pipx
    fi
    pipx install algokit
    pipx ensurepath
    echo "✅ AlgoKit installed successfully"
else
    echo "✅ AlgoKit is already installed"
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your preferences"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Start AlgoKit LocalNet
echo "🐳 Starting AlgoKit LocalNet..."
algokit localnet start

# Wait for LocalNet to be ready
echo "⏳ Waiting for LocalNet to be ready..."
sleep 10

# Get local IP address
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Development Environment:"
echo "   Local Algorand Node: http://localhost:4001"
echo "   Local Indexer: http://localhost:8980"
echo "   Your LAN IP: $LOCAL_IP"
echo ""
echo "👥 For your friend to connect:"
echo "   Algorand Node: http://$LOCAL_IP:4001"
echo "   Indexer: http://$LOCAL_IP:8980"
echo ""
echo "🔧 Next steps:"
echo "   1. Run: algokit generate contract seltra_pool"
echo "   2. Start developing your AMM contracts!"
echo ""
echo "📚 Documentation: https://dev.algorand.co/"
