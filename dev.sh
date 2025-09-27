#!/bin/bash

# Seltra AMM Development Helper

case "$1" in
    "start")
        echo "🚀 Starting AlgoKit LocalNet..."
        algokit localnet start
        ;;
    "stop")
        echo "🛑 Stopping AlgoKit LocalNet..."
        algokit localnet stop
        ;;
    "status")
        echo "📊 LocalNet Status:"
        algokit localnet status
        ;;
    "explore")
        echo "🌐 Opening AlgoKit Explorer..."
        algokit explore
        ;;
    "contract")
        echo "📝 Generating new contract..."
        algokit generate contract seltra_pool
        ;;
    "test")
        echo "🧪 Running tests..."
        python -m pytest tests/ -v
        ;;
    "deploy")
        echo "🚀 Deploying contracts..."
        python scripts/deploy.py
        ;;
    *)
        echo "Seltra AMM Development Helper"
        echo ""
        echo "Usage: $0 {start|stop|status|explore|contract|test|deploy}"
        echo ""
        echo "Commands:"
        echo "  start     - Start AlgoKit LocalNet"
        echo "  stop      - Stop AlgoKit LocalNet"
        echo "  status    - Show LocalNet status"
        echo "  explore   - Open AlgoKit Explorer"
        echo "  contract  - Generate new contract"
        echo "  test      - Run tests"
        echo "  deploy    - Deploy contracts"
        ;;
esac
