# Seltra AMM Deployment Guide

## 🎯 Overview

This guide covers the complete deployment process for the Seltra AMM system, including smart contracts, backend services, and frontend applications. The system consists of modular components designed to work together on the Algorand blockchain.

## 📋 System Architecture

### Core Components

1. **Smart Contracts** (On-Chain)

   - `SeltraPoolCore` - Main AMM functionality
   - `VolatilityOracleState` - Price and volatility tracking
   - `RebalancingState` - Liquidity range management
   - `HackToken` - Demo token for testing

2. **Backend Services** (Off-Chain)

   - Market simulation engine
   - Volatility calculations
   - Rebalancing logic
   - API endpoints

3. **Frontend Applications**
   - Development frontend (React + Vite)
   - Production frontend (React)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Node.js 18+
- AlgoKit CLI

### 1. Environment Setup

```bash
# Clone and navigate to project
git clone <repository-url>
cd seltra-amm

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
cd dev-frontend && npm install
cd ../frontend && npm install
cd ..
```

### 2. Start Local Development Environment

```bash
# Start all services with Docker Compose
docker compose up -d

# Or start individual services
make start-localnet    # Start Algorand LocalNet
make start-backend     # Start simulation backend
make start-frontend    # Start development frontend
```

### 3. Deploy Contracts

```bash
# Deploy all contracts to LocalNet
python scripts/orchestrate_localnet_deployment.py

# Or deploy individually
cd contracts/hack_token && algokit deploy --network localnet
cd ../seltra_pool && algokit deploy --network localnet
```

## 📦 Deployment Options

### LocalNet Development

**Use Case**: Development, testing, and demos

```bash
# Start LocalNet
algokit localnet start

# Deploy contracts
python scripts/orchestrate_localnet_deployment.py

# Start simulation
docker compose up market-simulator
```

**Access Points**:

- Frontend: http://localhost:3001
- API: http://localhost:8001
- Algorand Node: http://localhost:4001
- Indexer: http://localhost:8980

### TestNet Deployment

**Use Case**: Public testing and validation

```bash
# Configure TestNet
export ALGOD_TOKEN="your-testnet-token"
export ALGOD_SERVER="https://testnet-api.algonode.cloud"
export INDEXER_TOKEN="your-indexer-token"
export INDEXER_SERVER="https://testnet-idx.algonode.cloud"

# Deploy contracts
cd contracts/hack_token
algokit deploy --network testnet

cd ../seltra_pool
algokit deploy --network testnet
```

### MainNet Deployment

**Use Case**: Production deployment

```bash
# Configure MainNet (use production credentials)
export ALGOD_TOKEN="your-mainnet-token"
export ALGOD_SERVER="https://mainnet-api.algonode.cloud"
export INDEXER_TOKEN="your-indexer-token"
export INDEXER_SERVER="https://mainnet-idx.algonode.cloud"

# Deploy with production settings
cd contracts/hack_token
algokit deploy --network mainnet --update-config

cd ../seltra_pool
algokit deploy --network mainnet --update-config
```

## 🔧 Contract Deployment

### Individual Contract Deployment

#### 1. HACK Token

```bash
cd contracts/hack_token

# Compile contract
algokit compile py

# Deploy to network
algokit deploy --network localnet
# or
algokit deploy --network testnet
# or
algokit deploy --network mainnet
```

#### 2. Seltra Pool Core

```bash
cd contracts/seltra_pool

# Compile contract
algokit compile py

# Deploy to network
algokit deploy --network localnet
```

#### 3. Volatility Oracle State

```bash
cd contracts/refactored/volatility_oracle_state

# Compile contract
algokit compile py

# Deploy to network
algokit deploy --network localnet
```

#### 4. Rebalancing State

```bash
cd contracts/refactored/rebalancing_state

# Compile contract
algokit compile py

# Deploy to network
algokit deploy --network localnet
```

### Contract Initialization

After deployment, initialize contracts with proper parameters:

```python
# Initialize Seltra Pool
pool_core.initialize_pool(
    asset_x=0,  # ALGO
    asset_y=hack_asset_id,  # HACK token
    initial_price=1000000  # 1.0 in fixed point
)

# Initialize Volatility Oracle
oracle_state.initialize_oracle(
    initial_price=1000000
)

# Initialize Rebalancing Engine
rebalancing_state.initialize_engine(
    authorized_pool_id=pool_core_app_id,
    cooldown_seconds=300
)
```

## 🖥️ Backend Services

### Market Simulation Service

```bash
# Start simulation service
cd simulation
python main.py

# Or with Docker
docker compose up market-simulator
```

### Backend API Service

```bash
# Start backend service
cd contracts/refactored
python backend_service.py

# Or with uvicorn
uvicorn backend_service:app --host 0.0.0.0 --port 8000
```

## 🌐 Frontend Deployment

### Development Frontend

```bash
cd dev-frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Production Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Serve with static server
npx serve -s build -l 3000
```

## 📊 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Network Configuration
ALGOD_TOKEN=your-algod-token
ALGOD_SERVER=your-algod-server
INDEXER_TOKEN=your-indexer-token
INDEXER_SERVER=your-indexer-server

# Contract Addresses
SELTRA_POOL_APP_ID=your-pool-app-id
HACK_TOKEN_ASSET_ID=your-hack-asset-id
ORACLE_STATE_APP_ID=your-oracle-app-id
REBALANCING_STATE_APP_ID=your-rebalancing-app-id

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
SIMULATION_HOST=0.0.0.0
SIMULATION_PORT=8001

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8001
REACT_APP_ALGOD_SERVER=http://localhost:4001
```

### Contract Configuration

#### Pool Configuration

```python
POOL_CONFIG = {
    "asset_x_id": 0,  # ALGO
    "asset_y_id": None,  # HACK token ID (set after deployment)
    "initial_price": 1000000,  # 1.0 in fixed point
    "fee_rate": 30,  # 0.30% in basis points
}
```

#### Oracle Configuration

```python
ORACLE_CONFIG = {
    "initial_price": 1000000,
    "default_volatility": 30000,  # 3% in scaled format
    "default_regime": "medium"
}
```

#### Rebalancing Configuration

```python
REBALANCING_CONFIG = {
    "cooldown_seconds": 300,  # 5 minutes
    "authorized_pool_id": None,  # Set after pool deployment
}
```

## 🔍 Verification

### Contract Verification

```bash
# Verify contract deployment
algokit inspect --network localnet <app-id>

# Check contract state
algokit inspect --network localnet <app-id> --global-state
```

### API Health Check

```bash
# Check simulation API
curl http://localhost:8001/health

# Check backend API
curl http://localhost:8000/health
```

### Frontend Access

```bash
# Development frontend
curl http://localhost:3001

# Production frontend
curl http://localhost:3000
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Contract Deployment Fails

**Problem**: Contract size exceeds limit
**Solution**: Use refactored contracts in `contracts/refactored/`

#### 2. Backend Service Won't Start

**Problem**: Missing dependencies
**Solution**:

```bash
pip install -r requirements.txt
pip install fastapi uvicorn algosdk
```

#### 3. Frontend Build Fails

**Problem**: Node.js version mismatch
**Solution**:

```bash
nvm use 18
npm install
npm run build
```

#### 4. Docker Containers Won't Start

**Problem**: Port conflicts
**Solution**:

```bash
docker compose down
docker system prune -f
docker compose up -d
```

### Logs and Debugging

```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs market-simulator
docker compose logs dev-frontend

# View backend logs
tail -f simulation/logs/simulation.log
```

## 📈 Monitoring

### Health Checks

```bash
# Check all services
curl http://localhost:8001/health
curl http://localhost:8000/health
curl http://localhost:3001

# Check blockchain connection
curl http://localhost:4001/v2/status
```

### Metrics

- **Contract Metrics**: App IDs, transaction counts, gas usage
- **API Metrics**: Request rates, response times, error rates
- **Frontend Metrics**: Page load times, user interactions
- **Simulation Metrics**: Trade volume, price movements, volatility

## 🔄 Updates and Maintenance

### Contract Updates

```bash
# Update contract
algokit deploy --network localnet --update-config

# Migrate state (if needed)
python scripts/migrate_contract_state.py
```

### Backend Updates

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
docker compose restart market-simulator
```

### Frontend Updates

```bash
# Update dependencies
npm update

# Rebuild
npm run build
```

## 📞 Support

### Getting Help

1. **Documentation**: Check this guide and README files
2. **Logs**: Review service logs for error details
3. **Community**: Join Algorand developer community
4. **Issues**: Report bugs in the project repository

### Useful Commands

```bash
# Quick status check
make status

# Reset everything
make clean && make setup

# View deployment info
cat deployment.json

# Check network status
algokit localnet status
```

## 🎯 Next Steps

After successful deployment:

1. **Test Core Functionality**: Verify all contracts work correctly
2. **Run Simulations**: Test with various market conditions
3. **Monitor Performance**: Track metrics and optimize
4. **Scale Up**: Deploy to TestNet for broader testing
5. **Go Live**: Deploy to MainNet for production use

---

**Note**: This deployment guide covers the complete Seltra AMM system. For specific component details, refer to individual README files in each directory.
