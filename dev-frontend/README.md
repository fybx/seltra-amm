# Seltra Dev Console

A real-time development console for monitoring and controlling the Seltra market simulation system.

## Overview

The Dev Console provides comprehensive visualization and control over both market simulation and blockchain transaction simulation, allowing developers to:

- **Control Market Scenarios**: Trigger different market conditions (calm, volatile, flash crash, whale activity)
- **Monitor Real-Time Data**: View live price, volatility, volume, and transaction activity
- **Analyze Wallet Behavior**: Track simulated wallets and their trading patterns
- **Test System Responses**: Add price shocks and observe dynamic liquidity adjustments

## Features

### 🎯 Simulation Controls
- **Demo Scenarios**: Pre-configured market conditions for testing
- **Volatility Regimes**: Low, Medium, High volatility settings
- **Trading Patterns**: Normal vs Volatile blockchain activity
- **Manual Shocks**: Custom price shocks with configurable magnitude and duration

### 📊 Real-Time Visualizations
- **Price Chart**: Live price movements with trend indicators
- **Volatility Monitor**: Current volatility with regime classification
- **Volume Chart**: Trading volume with intensity heat-mapping
- **Transaction Activity**: Pending and executing blockchain transactions

### 🔍 System Monitoring
- **Live Metrics**: Key performance indicators and system health
- **Wallet Status**: Detailed view of simulated trader wallets
- **Connection Status**: Market and blockchain simulation connectivity
- **Performance Stats**: Transaction rates, success rates, and system uptime

## Quick Start

### Using Docker (Recommended)

```bash
# Start all services including dev-frontend
docker-compose up -d

# Access the dev console
open http://localhost:3001
```

### Local Development

```bash
# Install dependencies
cd dev-frontend
npm install

# Start development server
npm run dev

# Access dev console
open http://localhost:3001
```

## Interface Guide

### Header Bar
- **Connection Status**: Shows live status of market and blockchain simulators
- **Service Health**: Real-time indicators for system availability

### Simulation Controls Panel
- **Demo Scenarios**: Click buttons to trigger predefined market conditions
- **Current Status**: Shows active scenario and volatility regime
- **Manual Controls**: 
  - Volatility regime buttons (Low/Medium/High)
  - Trading pattern selector
  - Price shock controls with magnitude slider

### Chart Panels

#### Price Chart
- Real-time price movements with smooth animations
- Trend indicators (green for up, red for down)
- Percentage change display
- Time-based X-axis with automatic scaling

#### Volatility Chart
- Current volatility percentage with color-coded levels
- Progress bar showing relative volatility intensity
- Regime classification (Low/Medium/High/Extreme)
- Market impact descriptions for each level

#### Volume Chart
- Trading volume bars with intensity-based coloring
- Average and total volume statistics
- Time-based volume patterns

#### Transaction Activity
- Real-time pending transaction list
- Transaction type indicators (swap, add/remove liquidity)
- Execution countdown timers
- Progress bars for transaction queuing

### Live Metrics Dashboard
- **Market Status**: Current price, volatility, and scenario
- **Blockchain Status**: Transaction rates, success rates, active wallets
- **System Health**: Network load, pending transactions, uptime

### Wallet Status Panel
- **Filter Options**: View all wallets or filter by type (Whales, Retail, Bots)
- **Summary Statistics**: Wallet counts and average balances
- **Detailed Table**: Individual wallet information including:
  - Wallet addresses (truncated)
  - Trader types with color coding
  - ALGO balances
  - Trading frequencies
  - Average trade sizes
  - Volatility sensitivity factors

## API Integration

The dev console communicates with the simulation backend via REST API:

```javascript
// Example API calls
const API_BASE = 'http://localhost:8001'

// Get current status
const status = await fetch(`${API_BASE}/api/v1/status`)

// Trigger scenario
await fetch(`${API_BASE}/api/v1/demo/scenario?scenario_name=volatile_spike`, {
  method: 'POST'
})

// Set volatility regime
await fetch(`${API_BASE}/api/v1/volatility`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ regime: 'high' })
})
```

## Demo Scenarios

### Calm Trading
- **Duration**: 2 minutes
- **Behavior**: Low volatility, tight liquidity ranges
- **Use Case**: Testing optimal conditions and capital efficiency

### Volatility Spike  
- **Duration**: 3 minutes
- **Behavior**: High volatility, range expansion, increased trading
- **Use Case**: Dynamic liquidity adjustment demonstration

### Flash Crash
- **Duration**: 90 seconds  
- **Behavior**: Extreme market stress, emergency protection
- **Use Case**: System resilience and risk management testing

### Whale Activity
- **Duration**: 2.5 minutes
- **Behavior**: Large transactions, temporary price impact
- **Use Case**: Large trade handling and liquidity provision

## Development

### Technologies Used
- **React 18** with hooks for state management
- **Material-UI** for modern, accessible UI components
- **Chart.js** for smooth, animated real-time charts
- **Vite** for fast development and building
- **Axios** for API communication

### Project Structure
```
dev-frontend/
├── src/
│   ├── components/        # React components
│   │   ├── PriceChart.jsx
│   │   ├── VolatilityChart.jsx
│   │   ├── VolumeChart.jsx
│   │   ├── TransactionActivity.jsx
│   │   ├── WalletStatus.jsx
│   │   ├── LiveMetrics.jsx
│   │   └── SimulationControls.jsx
│   ├── hooks/             # Custom React hooks
│   │   └── useSimulationData.js
│   ├── services/          # API communication
│   │   └── api.js
│   ├── App.jsx           # Main application component
│   └── main.jsx          # Entry point
├── package.json
├── vite.config.js
└── Dockerfile
```

### Adding New Features

1. **New Chart Types**: Create components in `src/components/`
2. **Additional API Endpoints**: Update `src/services/api.js`
3. **Custom Hooks**: Add to `src/hooks/` for reusable logic
4. **Styling**: Extend Material-UI theme in `src/main.jsx`

## Troubleshooting

### Common Issues

**1. "No response from simulation server"**
- Ensure market-simulator service is running
- Check `docker-compose ps` for service status
- Verify port 8001 is accessible

**2. "Waiting for price data..."**
- Market simulator may still be initializing
- Check simulator logs: `docker-compose logs market-simulator`
- Allow 10-15 seconds for initial data

**3. "No wallets available"**
- Blockchain simulator initialization in progress
- Check Algorand node connectivity
- Verify algod service is running and accessible

**4. Charts not updating**
- Check browser developer console for JavaScript errors
- Verify WebSocket/polling connections
- Refresh page to reset connection state

### Performance Optimization

- Charts automatically limit data points to prevent memory issues
- Polling intervals are optimized for real-time feel vs. performance
- Component rendering is optimized with React.memo where appropriate

## Contributing

When adding new features or fixing bugs:

1. Ensure all components are responsive and accessible
2. Use Material-UI components for consistency
3. Add proper error handling for API calls
4. Update this README for new features
5. Test with different screen sizes and data scenarios

The dev console is designed to be the primary tool for developing and demonstrating the Seltra AMM's dynamic capabilities.
