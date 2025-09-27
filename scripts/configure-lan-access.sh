#!/bin/bash

# Configure AlgoKit LocalNet for LAN Access
# Based on Algorand Developer Portal: https://dev.algorand.co/

set -e

echo "🌐 Configuring AlgoKit LocalNet for LAN Access..."

# Get local IP address
LOCAL_IP=$(ifconfig | grep -E "inet.*broadcast" | awk '{print $2}' | head -1)
echo "📍 Your local IP address: $LOCAL_IP"

# Stop LocalNet to modify configuration
echo "🛑 Stopping LocalNet to modify configuration..."
algokit localnet stop

# Find and backup the docker-compose.yml file
COMPOSE_FILE="$HOME/.config/algokit/sandbox/docker-compose.yml"
BACKUP_FILE="$HOME/.config/algokit/sandbox/docker-compose.yml.backup"

if [ -f "$COMPOSE_FILE" ]; then
    echo "📋 Found AlgoKit configuration at: $COMPOSE_FILE"
    
    # Create backup
    cp "$COMPOSE_FILE" "$BACKUP_FILE"
    echo "💾 Created backup at: $BACKUP_FILE"
    
    # Modify the docker-compose.yml to bind to all interfaces
    echo "🔧 Modifying configuration for LAN access..."
    
    # Use sed to replace localhost/127.0.0.1 bindings with 0.0.0.0
    sed -i.tmp 's/127.0.0.1:\([0-9]*\):\([0-9]*\)/0.0.0.0:\1:\2/g' "$COMPOSE_FILE"
    sed -i.tmp 's/localhost:\([0-9]*\):\([0-9]*\)/0.0.0.0:\1:\2/g' "$COMPOSE_FILE"
    
    # Clean up temporary file
    rm -f "$COMPOSE_FILE.tmp"
    
    echo "✅ Configuration updated for LAN access"
else
    echo "❌ AlgoKit configuration file not found at: $COMPOSE_FILE"
    echo "Please run 'algokit localnet start' first to create the configuration"
    exit 1
fi

# Restart LocalNet with new configuration
echo "🚀 Restarting LocalNet with LAN access..."
algokit localnet start

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Test connectivity
echo "🧪 Testing connectivity..."
if curl -f http://localhost:4001/v2/status > /dev/null 2>&1; then
    echo "✅ Algorand Node API is accessible locally"
else
    echo "❌ Algorand Node API is not responding"
fi

if curl -f http://localhost:8980/health > /dev/null 2>&1; then
    echo "✅ Indexer API is accessible locally"
else
    echo "❌ Indexer API is not responding"
fi

echo ""
echo "🎉 AlgoKit LocalNet is now configured for LAN access!"
echo ""
echo "📋 Connection Information:"
echo "   Your Local IP: $LOCAL_IP"
echo "   Algorand Node: http://$LOCAL_IP:4001"
echo "   KMD API: http://$LOCAL_IP:4002"
echo "   Indexer: http://$LOCAL_IP:8980"
echo ""
echo "👥 For your friend to connect:"
echo "   1. They need to install AlgoKit: pipx install algokit"
echo "   2. Configure their environment:"
echo "      export ALGORAND_NODE_URL=http://$LOCAL_IP:4001"
echo "      export ALGORAND_INDEXER_URL=http://$LOCAL_IP:8980"
echo ""
echo "🔧 To restore original configuration:"
echo "   mv $BACKUP_FILE $COMPOSE_FILE && algokit localnet restart"
echo ""
echo "📚 Documentation: https://dev.algorand.co/"
