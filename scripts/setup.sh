#!/bin/bash

# Seltra AMM Development Environment Setup Script
# Based on NEW Algorand Developer Portal: https://dev.algorand.co/

set -e

echo "🚀 Setting up Seltra AMM Development Environment with Latest AlgoKit..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your wallet details before proceeding."
fi

# Create AlgoKit configuration for latest version
echo "🔧 Setting up AlgoKit configuration (latest from dev.algorand.co)..."
mkdir -p .algokit

cat > .algokit/config.json << EOF
{
  "environments": {
    "localnet": {
      "algod": {
        "url": "http://localhost:8080",
        "token": ""
      },
      "indexer": {
        "url": "http://localhost:8980",
        "token": ""
      },
      "explorer": {
        "url": "https://app.dappflow.org/explorer/application"
      }
    },
    "testnet": {
      "algod": {
        "url": "https://testnet-api.algonode.cloud",
        "token": ""
      },
      "indexer": {
        "url": "https://testnet-idx.algonode.cloud",
        "token": ""
      },
      "explorer": {
        "url": "https://testnet.algoexplorer.io"
      }
    }
  }
}
EOF

# Start Docker services with AlgoKit LocalNet
echo "🐳 Starting AlgoKit LocalNet and development environment..."
docker-compose up -d

# Wait for AlgoKit LocalNet to be ready
echo "⏳ Waiting for AlgoKit LocalNet to be ready..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:8080/v2/status > /dev/null 2>&1; then
        echo "✅ AlgoKit LocalNet is ready!"
        break
    fi
    echo "Waiting for LocalNet... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo "❌ Timeout waiting for AlgoKit LocalNet to start"
    exit 1
fi

# Initialize AlgoKit in the development container
echo "🔧 Initializing AlgoKit..."
docker-compose exec algokit-dev algokit init --template python

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your wallet details"
echo "2. Run: docker-compose exec algokit-dev bash"
echo "3. Start developing your contracts with: algokit generate contract"
echo ""
echo "🌐 Services available:"
echo "- AlgoKit LocalNet API: http://localhost:8080"
echo "- AlgoKit Indexer: http://localhost:8980"
echo "- Development container: docker-compose exec algokit-dev bash"
echo ""
echo "📚 Latest Documentation: https://dev.algorand.co/"
echo "🎯 AlgoKit Tutorials: https://dev.algorand.co/getting-started/introduction/"
