# Seltra AMM - System Architecture Specification

## Overview

Seltra AMM is a dynamic automated market maker that adapts liquidity concentration and fee structures based on real-time market volatility analysis. The system consists of interconnected Algorand smart contracts and supporting infrastructure.

## Core Innovation

**Dynamic Liquidity Management**: Unlike static AMMs, Seltra automatically adjusts liquidity concentration ranges based on market volatility, optimizing capital efficiency and providing better execution for traders.

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Seltra AMM System                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐    ┌─────────────────────────────┐   │
│  │   Frontend UI    │◄───┤      MarketSimulator       │   │
│  │   - Trading      │    │   - Price generation       │   │
│  │   - Visualization│    │   - Scenario testing       │   │
│  │   - LP Dashboard │    │   - Historical data        │   │
│  └─────────┬────────┘    └─────────────────────────────┘   │
│            │                                               │
│            ▼                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                SeltraPoolContract                       │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │ │
│  │  │   Liquidity │  │    Swap     │  │   LP Token      │ │ │
│  │  │  Management │  │   Engine    │  │   Management    │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘ │ │
│  └─────────────────────┬───────────────────────────────────┘ │
│                        │                                     │
│  ┌─────────────────────▼───────────────────────────────────┐ │
│  │               RebalancingEngine                         │ │
│  │   - Range calculation    - Safety validation           │ │
│  │   - Liquidity redistribution                           │ │
│  └─────────────────────┬───────────────────────────────────┘ │
│                        │                                     │
│  ┌─────────────────────▼───────────────────────────────────┐ │
│  │                VolatilityOracle                         │ │
│  │   - EWMA calculation     - Regime detection             │ │
│  │   - Price history        - Rebalance triggers          │ │
│  └─────────────────────┬───────────────────────────────────┘ │
│                        │                                     │
│  ┌─────────────────────▼───────────────────────────────────┐ │
│  │                 FeeManager                              │ │
│  │   - Dynamic fee calculation                             │ │
│  │   - Volatility-based adjustments                       │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Interactions

### Data Flow

1. **Price Updates** → VolatilityOracle → RebalancingEngine → SeltraPoolContract
2. **Volatility Analysis** → FeeManager → Dynamic Fee Adjustment
3. **Trade Execution** → SeltraPoolContract → VolatilityOracle (price update)
4. **Rebalancing Triggers** → RebalancingEngine → SeltraPoolContract (liquidity redistribution)

### Interface Contracts

| Interface | From Component | To Component | Purpose |
|-----------|---------------|--------------|---------|
| `IPriceOracle` | SeltraPoolContract | VolatilityOracle | Price updates and volatility queries |
| `IRebalancer` | VolatilityOracle | RebalancingEngine | Trigger rebalancing events |
| `IFeeCalculator` | SeltraPoolContract | FeeManager | Dynamic fee calculation |
| `ILiquidityManager` | RebalancingEngine | SeltraPoolContract | Liquidity range updates |

## Key Data Structures

### LiquidityRange
```python
@dataclass
class LiquidityRange:
    range_id: int
    price_lower: int  # Fixed point representation
    price_upper: int  # Fixed point representation  
    liquidity_amount: int
    is_active: bool
```

### VolatilityData
```python
@dataclass
class VolatilityData:
    current_volatility: int  # Fixed point (basis points)
    regime: int  # 0=low, 1=medium, 2=high
    last_update: int  # timestamp
    price_history: bytes  # Compressed recent prices
```

### RebalanceParams
```python
@dataclass
class RebalanceParams:
    target_ranges: list[LiquidityRange]
    concentration_factor: int  # Fixed point
    num_ranges: int
    min_liquidity_per_range: int
```

## Contract State Management

### Global State (SeltraPoolContract)
- `asset_x_id`: Asset X ID (8 bytes)
- `asset_y_id`: Asset Y ID (8 bytes) 
- `total_liquidity`: Total liquidity value (8 bytes)
- `current_price`: Current market price (8 bytes)
- `fee_rate`: Current fee rate in basis points (8 bytes)
- `last_rebalance`: Last rebalance timestamp (8 bytes)
- `volatility_oracle`: Oracle contract address (32 bytes)
- `rebalancer`: Rebalancing engine address (32 bytes)

### Local State (Per LP)
- `lp_token_balance`: LP token amount (8 bytes)
- `range_positions`: Bitmap of active ranges (8 bytes)
- `last_claim`: Last reward claim timestamp (8 bytes)

## Transaction Patterns

### Atomic Transaction Groups

1. **Swap Transaction**
   ```
   [Asset Transfer In] → [Contract Call: swap] → [Asset Transfer Out]
   ```

2. **Add Liquidity Transaction**
   ```
   [Asset X Transfer] → [Asset Y Transfer] → [Contract Call: add_liquidity] → [LP Token Mint]
   ```

3. **Rebalance Transaction**
   ```
   [Contract Call: calculate_ranges] → [Contract Call: redistribute_liquidity] → [Event Log]
   ```

## Safety Mechanisms

### Slippage Protection
- Maximum slippage tolerance per trade
- Price impact calculation before execution
- Minimum output amount validation

### Liquidity Protection
- Minimum liquidity requirement per range
- Maximum concentration limits
- Emergency pause functionality

### MEV Protection
- Commit-reveal scheme for large trades
- Time-based trade ordering
- Sandwich attack detection

## Performance Requirements

### Algorand Constraints
- **Transaction Cost**: Target <1000 micro-Algos per swap
- **State Usage**: <128KB total contract state
- **Computation**: <700 opcode budget per transaction
- **Latency**: 4.5 second finality target

### Scalability Targets
- **Throughput**: Handle 100+ TPS during high volatility
- **Liquidity**: Support pools up to $1M TVL
- **Ranges**: Support 3-7 dynamic liquidity ranges
- **History**: Maintain 100 price points for volatility calculation

## Upgrade Strategy

### Immutable Core
- Mathematical formulas (volatility calculation, range optimization)
- Core safety mechanisms
- Asset management logic

### Upgradeable Components
- Fee calculation parameters
- Volatility thresholds
- Rebalancing frequency limits
- UI interfaces

## Integration Points

### External Dependencies
- **Algorand SDK**: For blockchain interaction
- **Price Feeds**: For price oracle data (simulation mode)
- **Frontend**: React-based trading interface
- **Analytics**: Data export for performance tracking

### Internal APIs
- **Contract Interfaces**: Standardized ABI for all contracts
- **Event System**: Comprehensive logging for frontend updates
- **State Queries**: Read-only methods for UI data fetching

## Risk Management

### Circuit Breakers
- Maximum volatility threshold (pause rebalancing)
- Minimum liquidity threshold (prevent total drain)
- Maximum price movement per block

### Emergency Controls
- Pause functionality for critical bugs
- Admin override for stuck positions
- Recovery mechanisms for failed rebalances

---

This architecture is designed for hackathon development with clear separation of concerns, well-defined interfaces, and realistic constraints for the 12-hour timeline.
