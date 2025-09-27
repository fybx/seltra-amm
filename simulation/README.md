# Seltra Market & Blockchain Simulation

A comprehensive simulation system for testing and demonstrating the Seltra AMM's dynamic liquidity management capabilities on Algorand blockchain.

## Overview

The simulation consists of two integrated components:

1. **Market Simulator**: Generates realistic price movements and volatility patterns
2. **Blockchain Transaction Simulator**: Simulates real trading activity on Algorand blockchain

## Key Features

### Market Simulation
- **Realistic Price Models**: GBM, mean-reverting, jump-diffusion, volatile regimes
- **Volatility Regimes**: Low, medium, high volatility classifications  
- **Market Scenarios**: Normal, volatile, calm, trending, flash crash
- **Real-time Updates**: Continuous price and volatility updates

### Blockchain Simulation
- **Multi-Wallet System**: 20+ simulated trader wallets with different profiles
- **Trading Patterns**: Normal vs volatile market behavior
- **Wallet Types**: Retail traders and whale accounts
- **Transaction Types**: Swaps, liquidity provision/removal
- **Volatility Integration**: Trading frequency adapts to market conditions

## Quick Start

### 1. Start the Simulation Services

```bash
# Start all services (Algorand + Simulation)
docker-compose up -d

# Check service status
curl http://localhost:8001/health
```

### 2. API Endpoints

#### Market Simulation
```bash
# Get current price and volatility
curl http://localhost:8001/api/v1/price

# Get price history
curl http://localhost:8001/api/v1/history?window=50

# Set market scenario
curl -X POST http://localhost:8001/api/v1/scenario \
  -H "Content-Type: application/json" \
  -d '{"scenario": "volatile"}'

# Set volatility regime  
curl -X POST http://localhost:8001/api/v1/volatility \
  -H "Content-Type: application/json" \
  -d '{"regime": "high"}'
```

#### Blockchain Simulation
```bash
# Get wallet information
curl http://localhost:8001/api/v1/blockchain/wallets

# Get blockchain metrics
curl http://localhost:8001/api/v1/blockchain/metrics

# Set trading pattern
curl -X POST http://localhost:8001/api/v1/blockchain/pattern \
  -H "Content-Type: application/json" \
  -d '{"pattern": "volatile"}'

# Get pending transactions
curl http://localhost:8001/api/v1/blockchain/transactions/pending
```

#### Demo Scenarios
```bash
# Trigger predefined demo scenarios
curl -X POST http://localhost:8001/api/v1/demo/scenario?scenario_name=calm_market
curl -X POST http://localhost:8001/api/v1/demo/scenario?scenario_name=volatile_spike
curl -X POST http://localhost:8001/api/v1/demo/scenario?scenario_name=flash_crash
curl -X POST http://localhost:8001/api/v1/demo/scenario?scenario_name=whale_activity
```

### 3. Monitor Simulation

```bash
# Get comprehensive status
curl http://localhost:8001/api/v1/status

# Example response:
{
  "market_simulation": {
    "running": true,
    "current_price": 102.34,
    "current_volatility": 0.025,
    "scenario": "normal",
    "regime": "medium",
    "uptime": 1845,
    "total_trades": 89
  },
  "blockchain_simulation": {
    "running": true,
    "total_transactions": 156,
    "success_rate": 95.5,
    "transactions_per_minute": 5.2,
    "current_pattern": "normal",
    "active_wallets": 20,
    "pending_transactions": 8
  }
}
```

## Configuration

### Wallet Configuration
- **Default Wallets**: 20 (15 retail + 5 whales in normal mode)
- **Whale Ratio**: 5% (normal) to 25% (volatile)
- **Average Sizes**: Retail (10-100 ALGO), Whales (1000+ ALGO)
- **Trading Frequency**: 0.5-2.0 transactions per minute per wallet

### Market Parameters
```python
VOLATILITY_THRESHOLDS = {
    "low": 0.01,    # < 1% daily volatility
    "medium": 0.05, # < 5% daily volatility  
    "high": 0.05    # > 5% daily volatility
}

TRADING_PATTERNS = {
    "normal": {
        "base_frequency": 0.5,    # tx/min/wallet
        "size_variance": 0.3,     # 30% size variation
        "burst_probability": 0.1, # 10% burst chance
        "whale_ratio": 0.05      # 5% whales
    },
    "volatile": {
        "base_frequency": 2.0,    # tx/min/wallet
        "size_variance": 0.8,     # 80% size variation
        "burst_probability": 0.3, # 30% burst chance
        "whale_ratio": 0.15      # 15% whales
    }
}
```

## Demo Scenarios

### Available Scenarios

1. **calm_market**: Stable conditions, tight liquidity concentration
2. **volatile_spike**: High volatility, range expansion
3. **flash_crash**: Extreme events, maximum protection
4. **whale_activity**: Large trades, market impact demonstration

### Scenario Configuration Example

```python
"volatile_spike": {
    "name": "Volatility Spike - Dynamic Range Expansion",
    "duration_seconds": 180,
    "market_config": {
        "scenario": "volatile",
        "volatility_regime": "high",
        "initial_volatility": 0.08
    },
    "blockchain_config": {
        "pattern": "volatile", 
        "num_wallets": 25,
        "whale_ratio": 0.15
    }
}
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Market          │    │ Blockchain      │    │ Algorand        │
│ Simulator       │◄──►│ Simulator       │◄──►│ Network         │
│                 │    │                 │    │ (Docker)        │
│ - Price Gen     │    │ - 20+ Wallets   │    │ - Algod         │
│ - Volatility    │    │ - Tx Generation │    │ - Indexer       │ 
│ - Scenarios     │    │ - Pattern Logic │    │ - PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ FastAPI Server  │
                    │ (Port 8001)     │
                    │                 │
                    │ - REST API      │
                    │ - WebSocket     │
                    │ - CORS Enabled  │
                    └─────────────────┘
```

## Development

### Local Development
```bash
# Install dependencies
pip install -r simulation/requirements.txt

# Run simulation service
cd simulation
python -m simulation.main

# Access API docs
open http://localhost:8000/docs
```

### Testing
```bash
# Test market simulation
python -c "
from simulation.market_simulator import MarketSimulator
sim = MarketSimulator()
print(f'Price: {sim.current_price}')
"

# Test blockchain simulation  
python -c "
from simulation.blockchain_simulator import AlgorandTransactionSimulator
sim = AlgorandTransactionSimulator()
print(f'Wallets: {len(sim.wallets)}')
"
```

### Environment Variables
```bash
# .env file
ALGORAND_ALGOD_ADDRESS=http://algod:8080
ALGORAND_ALGOD_TOKEN=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
SIMULATION_LOG_LEVEL=INFO
SIMULATION_NUM_WALLETS=20
```

## Performance Metrics

### Expected Performance
- **Transaction Rate**: 5-10 tx/min in normal mode, 15-25 tx/min in volatile mode
- **Success Rate**: >95% (includes simulated network failures)
- **Response Time**: <100ms for API calls
- **Memory Usage**: ~50MB for full simulation

### Monitoring
```bash
# Real-time metrics
watch -n 5 'curl -s http://localhost:8001/api/v1/status | jq'

# Transaction monitoring
curl http://localhost:8001/api/v1/blockchain/transactions/pending | jq
```

## Troubleshooting

### Common Issues

1. **Algorand Connection Failed**
   ```bash
   # Check if Algorand services are running
   docker-compose ps
   
   # Restart services
   docker-compose restart algod
   ```

2. **No Transactions Generated**
   ```bash
   # Check wallet creation
   curl http://localhost:8001/api/v1/blockchain/wallets
   
   # Reset simulation
   curl -X POST http://localhost:8001/api/v1/blockchain/reset
   ```

3. **High Memory Usage**
   ```bash
   # Clear price history
   curl -X POST http://localhost:8001/api/v1/reset
   ```

### Logs
```bash
# View simulation logs
docker-compose logs -f market-simulator

# Filter for specific events
docker-compose logs market-simulator | grep "Transaction"
```

## Integration with Seltra AMM

The simulation provides realistic trading data for testing:

1. **Price Feeds**: Real-time price updates for AMM calculations
2. **Volatility Data**: Triggers dynamic liquidity concentration
3. **Trading Patterns**: Realistic user behavior for testing
4. **Market Scenarios**: Edge cases and stress testing

This simulation framework enables comprehensive testing of the Seltra AMM's dynamic features before mainnet deployment.
