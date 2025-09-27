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
- Dev Console: http://localhost:3001 (Real-time simulation visualization)
- Frontend: http://localhost:3000 (Trading interface)
- Market Simulator: http://localhost:8001
- Algorand Node: http://localhost:4001
- Indexer: http://localhost:8980

**Stop everything:**
```bash
docker-compose down
```

## What's Included

- **Algorand Network**: Local development blockchain (algod + indexer)
- **Market Simulator**: Realistic price/volatility simulation with blockchain transaction sim
- **Dev Console**: Real-time visualization and control interface (NEW!)
- **React Frontend**: Trading interface with real-time data
- **PostgreSQL**: Database for blockchain indexing

## 🚀 Quick Development Start

For immediate access to the development console:

```bash
# Quick start script
./scripts/start-dev-console.sh
```

This will start all required services and give you access to:
- **Real-time price and volatility charts**
- **Interactive simulation controls** 
- **Live blockchain transaction monitoring**
- **Wallet activity visualization**

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