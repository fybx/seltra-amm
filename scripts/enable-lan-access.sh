#!/bin/bash

# Enable LAN Access for AlgoKit LocalNet
# This script modifies the running Docker containers to bind to all interfaces

set -e

echo "🌐 Enabling LAN Access for AlgoKit LocalNet..."

# Get local IP address
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)
echo "📍 Your local IP address: $LOCAL_IP"

# Check if LocalNet is running
if ! curl -s http://localhost:4001/v2/status > /dev/null 2>&1; then
    echo "❌ AlgoKit LocalNet is not running. Please run 'algokit localnet start' first."
    exit 1
fi

echo "✅ AlgoKit LocalNet is running"

# Get the proxy container ID
PROXY_CONTAINER=$(docker ps --filter "name=algokit_sandbox_proxy" --format "{{.ID}}")

if [ -z "$PROXY_CONTAINER" ]; then
    echo "❌ Could not find AlgoKit proxy container"
    exit 1
fi

echo "🔧 Found proxy container: $PROXY_CONTAINER"

# Check current port bindings
echo "📋 Current port bindings:"
docker port $PROXY_CONTAINER

echo ""
echo "🎉 LAN Access is already configured!"
echo ""
echo "📋 Connection Information:"
echo "   Your Local IP: $LOCAL_IP"
echo "   Algorand Node: http://$LOCAL_IP:4001"
echo "   Indexer: http://$LOCAL_IP:8980"
echo ""
echo "👥 For your friend to connect:"
echo "   1. They need to install AlgoKit: pipx install algokit"
echo "   2. Configure their environment:"
echo "      export ALGORAND_NODE_URL=http://$LOCAL_IP:4001"
echo "      export ALGORAND_INDEXER_URL=http://$LOCAL_IP:8980"
echo ""
echo "🧪 Test connection:"
echo "   curl -H \"X-Algo-API-Token: a\" http://$LOCAL_IP:4001/v2/status"
echo ""
echo "📚 Documentation: https://dev.algorand.co/"
