#!/bin/bash

# Manual Algorand LocalNet Setup with LAN Access
# Alternative to AlgoKit LocalNet when Docker has issues

set -e

echo "🚀 Starting Manual Algorand LocalNet with LAN Access..."

# Get local IP address
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)
echo "📍 Your local IP address: $LOCAL_IP"

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker compose -f docker-compose-localnet.yml down || true

# Start the LocalNet
echo "🚀 Starting Algorand LocalNet..."
docker compose -f docker-compose-localnet.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 20

# Test connectivity
echo "🧪 Testing connectivity..."
echo "Testing local connectivity..."
if curl -f http://localhost:4001/v2/status > /dev/null 2>&1; then
    echo "✅ Algorand Node API is accessible locally"
else
    echo "❌ Algorand Node API is not responding locally"
fi

if curl -f http://localhost:8980/health > /dev/null 2>&1; then
    echo "✅ Indexer API is accessible locally"
else
    echo "❌ Indexer API is not responding locally"
fi

echo ""
echo "Testing LAN connectivity..."
if curl -f http://$LOCAL_IP:4001/v2/status > /dev/null 2>&1; then
    echo "✅ Algorand Node API is accessible via LAN"
else
    echo "❌ Algorand Node API is not responding via LAN"
fi

if curl -f http://$LOCAL_IP:8980/health > /dev/null 2>&1; then
    echo "✅ Indexer API is accessible via LAN"
else
    echo "❌ Indexer API is not responding via LAN"
fi

echo ""
echo "🎉 Algorand LocalNet is running!"
echo ""
echo "📋 Connection Information:"
echo "   Your Local IP: $LOCAL_IP"
echo "   Algorand Node: http://$LOCAL_IP:4001"
echo "   KMD API: http://$LOCAL_IP:4002"
echo "   Indexer: http://$LOCAL_IP:8980"
echo ""
echo "👥 For your friend to connect:"
echo "   1. They need to configure their environment:"
echo "      export ALGORAND_NODE_URL=http://$LOCAL_IP:4001"
echo "      export ALGORAND_INDEXER_URL=http://$LOCAL_IP:8980"
echo ""
echo "🔧 To stop LocalNet:"
echo "   docker compose -f docker-compose-localnet.yml down"
echo ""
echo "📚 Documentation: https://dev.algorand.co/"
