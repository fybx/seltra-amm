# Seltra AMM - Intelligent Dynamic Liquidity AMM

A next-generation AMM built on Algorand that automatically adjusts liquidity concentration based on market volatility.

## Quick Start

**Prerequisites:**
- Docker and Docker Compose
- Git

**Start everything:**
```bash
git clone <repository>
cd seltra-monorepo
docker-compose up --build
```

**Access services:**
- **Main Trading Interface**: http://localhost:3000 (Next.js with Pera Wallet)
- **Dev Console**: http://localhost:3001 (Real-time simulation visualization)
- **Market Simulator API**: http://localhost:8001
- **Algorand Node**: http://localhost:4001
- **Indexer**: http://localhost:8980

**Stop everything:**
```bash
docker-compose down
```

## What's Included

- **Next.js Trading Interface**: Complete frontend with Pera Wallet integration (NEW!)
- **Algorand Smart Contracts**: SeltraPoolContract, VolatilityOracle, RebalancingEngine
- **Market Simulator**: Realistic price/volatility simulation with blockchain transaction sim
- **Dev Console**: Real-time visualization and control interface
- **Algorand Network**: TestNet integration for real trading
- **PostgreSQL**: Database for blockchain indexing

## 🚀 Complete System Deployment

Deploy the complete Seltra AMM system with contracts and UI:

```bash
# Deploy contracts to testnet and start complete system
./scripts/deploy-complete-system.sh
```

This will:
- **Deploy smart contracts to Algorand TestNet**
- **Start the complete Next.js trading interface**
- **Launch real-time market simulation**
- **Provide Pera Wallet integration**

## 🎯 Quick Development Start

For development console only:

```bash
# Quick start script for dev console
./scripts/start-dev-console.sh
```

## API Token

All Algorand services use this development token:
```
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

## Core Features

- **Dynamic Liquidity Concentration**: Adjusts ranges based on volatility
- **Market Simulation**: Multiple scenarios (normal, volatile, calm, trending)
- **Real-time Updates**: Live price feeds and rebalancing
- **Web Interface**: Monitor and interact with the AMM

## Development

View logs:
```bash
docker-compose logs -f [service_name]
```

Restart service:
```bash
docker-compose restart [service_name]
```

That's it. Simple and reliable.