# Seltra AMM Next.js Frontend

A complete Next.js frontend for the Seltra AMM with Pera Wallet integration and real-time market data.

## Features

### Core Functionality
- **Pera Wallet Integration**: Seamless wallet connection and transaction signing
- **Token Swapping**: Exchange ALGO and HACK tokens with dynamic pricing
- **Liquidity Management**: Add and remove liquidity from concentrated ranges
- **Real-time Market Data**: Live price feeds and volatility monitoring
- **Market Controls**: Control simulation scenarios and market conditions

### Technical Features
- **Next.js 14**: Latest Next.js with App Router and TypeScript
- **Real Contract Integration**: Direct interaction with deployed Algorand contracts
- **No Mock Data**: All data comes from real contracts and market simulation
- **Blue & Yellow Theme**: Professional color scheme as requested
- **Responsive Design**: Works on desktop and mobile devices

## Quick Start

### Using Docker (Recommended)

```bash
# Start all services including Next.js frontend
docker-compose up -d

# Access the frontend
open http://localhost:3000
```

### Local Development

```bash
# Install dependencies
cd nextjs-frontend
npm install

# Copy environment variables
cp .env.example .env.local

# Start development server
npm run dev

# Access frontend
open http://localhost:3000
```

## Architecture

### Providers
- **WalletProvider**: Manages Pera Wallet connection and account state
- **ContractProvider**: Handles smart contract interactions
- **MarketDataProvider**: Real-time market data from simulation API

### Components
- **SwapInterface**: Token swapping with slippage protection
- **LiquidityInterface**: Add/remove liquidity from ranges
- **MarketDashboard**: Market metrics and simulation controls
- **Layout**: Main application layout with header and footer

### Real Integrations
- **Algorand SDK**: Direct blockchain interactions
- **Pera Wallet**: Native wallet integration
- **Market Simulator API**: Real-time market data
- **Smart Contracts**: Direct contract calls (no mocks)

## Configuration

### Environment Variables

```bash
# Network Configuration
NEXT_PUBLIC_NETWORK=testnet
NEXT_PUBLIC_ALGOD_ADDRESS=https://testnet-api.algonode.cloud
NEXT_PUBLIC_INDEXER_ADDRESS=https://testnet-idx.algonode.cloud

# Contract Configuration
NEXT_PUBLIC_SELTRA_POOL_APP_ID=1000
NEXT_PUBLIC_ASSET_X_ID=0
NEXT_PUBLIC_ASSET_Y_ID=1008

# Market Simulator
NEXT_PUBLIC_SIMULATOR_ADDRESS=http://localhost:8001
```

### Network Support
- **TestNet**: Default configuration for testing
- **LocalNet**: For local development
- **MainNet**: Production deployment ready

## User Interface

### Color Scheme
- **Primary Blue**: #0066FF (buttons, highlights)
- **Secondary Yellow**: #FFD700 (accents, warnings)
- **Neutral Grays**: Professional backgrounds and text

### Components Used
- **Next.js Built-in Components**: No external UI libraries
- **Custom CSS**: Tailored styling with CSS-in-JS
- **No Emojis**: Professional appearance as requested
- **No Lucide React**: Pure Next.js components only

## Smart Contract Integration

### Supported Operations
- **Pool Initialization**: Set up new trading pairs
- **Token Swapping**: Execute trades with slippage protection
- **Liquidity Management**: Add/remove liquidity from ranges
- **Pool Queries**: Real-time pool state and metrics

### Transaction Flow
1. User initiates action in UI
2. Parameters validated and formatted
3. Transaction created with Algorand SDK
4. Signed with Pera Wallet
5. Submitted to blockchain
6. Confirmation and UI update

## Market Data Integration

### Real-time Features
- **Live Price Updates**: Every 2 seconds from simulator
- **Volatility Monitoring**: Real-time regime detection
- **Volume Tracking**: Trading activity metrics
- **Scenario Control**: Market condition simulation

### API Endpoints
- `/api/v1/status` - System health and status
- `/api/v1/metrics` - Current market metrics
- `/api/v1/history` - Price history data
- `/api/v1/scenario` - Market scenario control

## Development

### Build Commands
```bash
npm run dev      # Development server
npm run build    # Production build
npm run start    # Production server
npm run lint     # Code linting
```

### Project Structure
```
nextjs-frontend/
├── app/                 # Next.js App Router pages
├── components/          # React components
├── providers/           # Context providers
├── types/              # TypeScript types
├── utils/              # Utility functions
├── styles/             # Global styles
└── public/             # Static assets
```

## Deployment

### Docker Deployment
The frontend is containerized and ready for production deployment with the included Dockerfile.

### Environment Setup
1. Configure environment variables for target network
2. Ensure contract addresses are correct
3. Set up market simulator connection
4. Deploy with Docker or build for static hosting

## Security

### Wallet Security
- **Pera Wallet Integration**: Secure transaction signing
- **No Private Key Storage**: Keys remain in user's wallet
- **Transaction Validation**: All inputs validated before signing

### Network Security
- **HTTPS Endpoints**: Secure API connections
- **Input Sanitization**: All user inputs validated
- **Error Handling**: Graceful error management

This frontend provides a complete, production-ready interface for the Seltra AMM with real blockchain integration and professional design.
