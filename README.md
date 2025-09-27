# Seltra AMM - Intelligent Dynamic Liquidity AMM

A next-generation Automated Market Maker (AMM) built on Algorand that automatically adjusts liquidity concentration based on market volatility and trading patterns.

**Built with the latest AlgoKit and Algorand development tools from [dev.algorand.co](https://dev.algorand.co/getting-started/introduction/)**

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Setup Development Environment

1. **Clone and setup:**

   ```bash
   git clone <your-repo>
   cd seltra-amm
   make setup
   ```

2. **Start development environment:**

   ```bash
   make start
   ```

3. **Generate your first contract:**

   ```bash
   algokit generate contract seltra_pool
   ```

4. **View available commands:**
   ```bash
   make help
   ```

## 🔧 Latest AlgoKit Features

This project uses the newest Algorand development tools:

- **AlgoKit LocalNet**: Instant local development environment
- **Latest AlgoKit CLI**: Modern contract development workflow
- **AlgoKit Utils 2.0+**: Enhanced Python SDK
- **Algorand Python SDK 2.8+**: Latest blockchain integration

## 🏗️ Architecture

### Core Components

- **Dynamic Liquidity Engine**: Adjusts liquidity ranges based on volatility
- **Volatility Oracle**: Calculates market volatility using EWMA
- **Rebalancing System**: Automatically redistributes liquidity
- **Market Simulator**: Realistic market simulation for testing

### Technology Stack

- **Blockchain**: Algorand (Python smart contracts)
- **Development**: AlgoKit (latest), AlgoKit Utils 2.0+, Python SDK 2.8+
- **Simulation**: NumPy, Pandas, Matplotlib
- **Frontend**: HTML/CSS/JavaScript with Canvas visualization
- **Local Development**: AlgoKit LocalNet (instant setup)

## 📁 Project Structure

```
seltra-amm/
├── contracts/          # Smart contracts
├── simulation/         # Market simulation code
├── frontend/          # Web interface
├── scripts/           # Development scripts
├── tests/             # Test suites
├── docker-compose.yml # Docker configuration
├── Makefile          # Development commands
└── README.md         # This file
```

## 🛠️ Development Workflow

### Daily Development

```bash
# Start environment
make start

# Enter development container
make shell

# Run tests
make test

# Format code
make format

# Deploy contracts
make deploy
```

### Creating Smart Contracts

```bash
# Enter development container
make shell

# Create new contract with AlgoKit
algokit generate contract my_contract

# Deploy to testnet
python scripts/deploy.py
```

### Running Simulations

```bash
# Enter development container
make shell

# Run market simulation
python simulation/market_simulator.py

# Run full AMM simulation
python simulation/seltra_simulation.py
```

## 🎯 Core Features

### 1. Dynamic Liquidity Concentration

- **Calm Markets**: Tight liquidity ranges for better execution
- **Volatile Markets**: Wide ranges for protection
- **Automatic Adjustment**: Real-time rebalancing based on volatility

### 2. Volatility-Responsive System

- **EWMA Calculation**: Smooth volatility measurement
- **Regime Detection**: Low/Medium/High volatility classification
- **Decision Tree Logic**: Simple, efficient rebalancing decisions

### 3. Market Simulation

- **Realistic Price Movements**: Random walk with configurable volatility
- **Multiple Scenarios**: Bull, bear, sideways markets
- **Performance Metrics**: APY, slippage, capital efficiency

## 📊 Demo Scenarios

### Scenario 1: Calm Market

- Show tight liquidity concentration around current price
- Demonstrate low slippage for standard trades
- Highlight capital efficiency gains

### Scenario 2: Volatility Spike

- Watch liquidity ranges automatically widen
- Show protection against large price movements
- Demonstrate system adaptation in real-time

### Scenario 3: Recovery

- Observe ranges tightening as volatility decreases
- Show return to optimal capital efficiency
- Highlight automatic rebalancing

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

```bash
# Algorand Network
ALGORAND_NETWORK=testnet
ALGORAND_NODE_URL=http://localhost:8080

# Simulation Parameters
SIMULATION_INITIAL_PRICE=2000.0
SIMULATION_VOLATILITY=0.02
SIMULATION_WINDOW_SIZE=10

# Wallet Configuration
TEST_WALLET_ADDRESS=your_address_here
TEST_WALLET_MNEMONIC=your_mnemonic_here
```

### AlgoKit Configuration

Located in `.algokit/config.json`:

- Local development network
- Testnet configuration
- Explorer links

## 🧪 Testing

### Run All Tests

```bash
make test
```

### Contract Testing

```bash
# Enter development container
make shell

# Run contract tests
python -m pytest tests/contracts/ -v
```

### Simulation Testing

```bash
# Run simulation tests
python -m pytest tests/simulation/ -v
```

## 🚀 Deployment

### Testnet Deployment

```bash
make deploy
```

### Production Deployment

```bash
make prod-deploy
```

## 📈 Performance Metrics

### Target Metrics

- **Capital Efficiency**: 3x improvement over traditional AMMs
- **LP Returns**: 15%+ APY
- **Trader Satisfaction**: <0.1% slippage for standard trades
- **System Reliability**: 99.9% uptime

### Monitoring

- Real-time liquidity distribution
- Volatility tracking
- Rebalancing frequency
- Performance analytics

## 🤝 Contributing

### Development Guidelines

1. Use `make format` before committing
2. Run `make test` to ensure all tests pass
3. Follow Algorand best practices
4. Document new features

### Code Style

- Python: Black formatting, type hints
- Smart Contracts: Algorand Python syntax
- Frontend: Clean, responsive design

## 📚 Resources

### Documentation

- [Algorand Developer Portal (NEW)](https://dev.algorand.co/)
- [Getting Started Tutorial](https://dev.algorand.co/getting-started/introduction/)
- [AlgoKit Documentation](https://github.com/algorandfoundation/algokit)
- [Algorand Python SDK](https://github.com/algorand/py-algorand-sdk)

### Community

- [Algorand Discord](https://discord.gg/algorand)
- [Algorand Forum](https://forum.algorand.org/)

## 🏆 Hackathon Goals

### Core Innovation

- First AMM with real-time volatility-responsive liquidity
- Automatic rebalancing based on market conditions
- Superior capital efficiency through dynamic concentration

### Demo Highlights

- Live liquidity rebalancing visualization
- Real-time volatility adaptation
- Performance comparison with static AMMs
- Professional blockchain deployment

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ on Algorand** | **Powered by Latest AlgoKit** | **Documentation: https://dev.algorand.co/getting-started/introduction/**
