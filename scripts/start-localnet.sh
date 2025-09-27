#!/bin/bash

# Seltra AMM - Start AlgoKit LocalNet with LAN Access
# Based on Algorand Developer Portal: https://dev.algorand.co/

set -e

echo "🚀 Starting Seltra AMM AlgoKit LocalNet with LAN Access..."

# Check if AlgoKit is installed
if ! command -v algokit &> /dev/null; then
    echo "📦 Installing AlgoKit..."
    curl -fsSL https://github.com/algorandfoundation/algokit-cli/releases/latest/download/algokit-linux-amd64.tar.gz | tar -xz -C /usr/local/bin
fi

# Get local IP address
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)
echo "🌐 Your local IP address: $LOCAL_IP"

# Stop any existing LocalNet
echo "🛑 Stopping any existing LocalNet..."
algokit localnet stop || true

# Start AlgoKit LocalNet
echo "🚀 Starting AlgoKit LocalNet..."
algokit localnet start

# Wait for LocalNet to be ready
echo "⏳ Waiting for LocalNet to be ready..."
sleep 10

# Get LocalNet status
echo "📊 LocalNet Status:"
algokit localnet status

echo ""
echo "✅ AlgoKit LocalNet is running!"
echo ""
echo "🌐 Network Access Information:"
echo "   Your Local IP: $LOCAL_IP"
echo "   Algorand Node: http://$LOCAL_IP:4001"
echo "   KMD API: http://$LOCAL_IP:4002"
echo "   Indexer: http://$LOCAL_IP:8980"
echo ""
echo "👥 For your friend to connect:"
echo "   1. They need to install AlgoKit on their machine"
echo "   2. Configure their environment to use:"
echo "      ALGORAND_NODE_URL=http://$LOCAL_IP:4001"
echo "      ALGORAND_INDEXER_URL=http://$LOCAL_IP:8980"
echo ""
echo "🔧 To stop LocalNet: algokit localnet stop"
echo "📚 Documentation: https://dev.algorand.co/"
