# ALGO-HACK Token Specification

## Overview

Configuration for the ALGO-HACK trading pair used in Seltra AMM hackathon demonstration. ALGO serves as the base asset (native Algorand token) paired with HACK, a demonstration token minted specifically for this hackathon.

## Token Specifications

### ALGO (Native Token)
```python
ALGO_SPEC = {
    "id": 0,  # Native Algorand token
    "name": "ALGO",
    "unit_name": "ALGO",
    "decimals": 6,  # 1 ALGO = 1,000,000 microAlgos
    "is_native": True,
    "description": "Native Algorand blockchain token"
}
```

### HACK Token (Demonstration ASA)
```python
HACK_TOKEN_SPEC = {
    "name": "HACK",
    "unit_name": "HACK", 
    "decimals": 6,  # Match ALGO's decimals for easier calculations
    "total_supply": 1_000_000_000_000,  # 1M HACK tokens (in microunits)
    "default_frozen": False,
    "url": "https://seltra-amm.com/hack-token",
    "metadata": {
        "description": "Hackathon demonstration token for Seltra AMM",
        "external_url": "https://github.com/seltra-amm",
        "created_for": "Algorand Hackathon Demo"
    },
    # Management addresses (to be set during minting)
    "manager": "",    # Can modify token properties
    "reserve": "",    # Can mint/burn tokens
    "freeze": "",     # Can freeze accounts  
    "clawback": ""    # Can clawback tokens
}
```

## ALGO-HACK Pool Configuration

### Initial Pool Setup
```python
ALGO_HACK_POOL_CONFIG = {
    "asset_x": 0,  # ALGO (always first)
    "asset_y": None,  # HACK token ID (set after minting)
    "initial_price": 1_000_000,  # 1 HACK = 1 ALGO (fixed point, 1e6 scale)
    "initial_liquidity": {
        "algo_amount": 50_000_000_000,  # 50K ALGO (50M microAlgos)
        "hack_amount": 50_000_000_000,  # 50K HACK (50M microHACK)
    },
    "fee_tier": "medium",  # 0.30% base fee
    "range_configuration": {
        "initial_ranges": 3,
        "price_range_percent": 10,  # ±10% around current price
        "concentration_factor": 1.0
    }
}
```

### Demo-Specific Parameters
```python
DEMO_PARAMETERS = {
    # Price bounds for demo safety
    "min_price": 500_000,   # 0.5 HACK per ALGO (50% down)
    "max_price": 2_000_000, # 2.0 HACK per ALGO (100% up)
    
    # Trading limits
    "max_trade_size_algo": 5_000_000_000,  # 5K ALGO max per trade
    "min_trade_size_algo": 1_000_000,      # 1 ALGO minimum per trade
    
    # Volatility targeting for demo
    "target_volatility": 0.03,  # 3% daily volatility
    "max_volatility": 0.10,     # 10% maximum volatility
    
    # Rebalancing sensitivity
    "rebalance_threshold": 0.02,  # 2% volatility change triggers rebalance
    "min_rebalance_interval": 60  # 1 minute minimum between rebalances
}
```

## Token Distribution Strategy

### Initial Allocation
```python
HACK_DISTRIBUTION = {
    # Pool liquidity
    "amm_pool": {
        "amount": 100_000_000_000,  # 100K HACK tokens
        "percentage": 10.0
    },
    
    # Demo trading wallets
    "demo_wallets": {
        "amount": 500_000_000_000,  # 500K HACK tokens  
        "percentage": 50.0,
        "wallet_allocation": {
            "retail_wallets": 300_000_000_000,  # 300K HACK (15 wallets)
            "whale_wallets": 200_000_000_000     # 200K HACK (5 wallets)
        }
    },
    
    # Reserve for additional demos
    "reserve": {
        "amount": 400_000_000_000,  # 400K HACK tokens
        "percentage": 40.0,
        "purpose": "Additional liquidity and future demos"
    }
}
```

### Wallet Funding Strategy
```python
WALLET_FUNDING = {
    "retail_traders": {
        "count": 15,
        "algo_balance": 1_000_000_000,    # 1K ALGO each
        "hack_balance": 20_000_000_000,   # 20K HACK each
        "trading_style": "frequent_small"
    },
    
    "whale_traders": {
        "count": 5, 
        "algo_balance": 10_000_000_000,   # 10K ALGO each
        "hack_balance": 40_000_000_000,   # 40K HACK each
        "trading_style": "infrequent_large"
    }
}
```

## Integration with Existing Systems

### Market Simulator Integration
- Price movements calibrated for ALGO volatility patterns
- Volume scaling appropriate for ALGO ecosystem
- Scenario targeting realistic crypto market behavior

### Fee Manager Integration  
- Volume thresholds denominated in ALGO
- Fee calculations optimized for crypto trading patterns
- Tier benefits scaled for hackathon demonstration

### Volatility Oracle Integration
- Volatility thresholds adjusted for crypto markets
- Price change limits appropriate for ALGO-HACK pair
- Regime classification tuned for demonstration clarity

## Security Considerations

### Demo Safety Measures
1. **Price Bounds**: Hard limits prevent extreme price movements
2. **Trade Size Limits**: Prevent single trades from dominating pool
3. **Controlled Distribution**: Limited token supply prevents manipulation
4. **Monitoring**: Real-time tracking of all demo activities

### Token Management
1. **Freeze Capability**: Can pause trading if issues arise
2. **Supply Control**: Fixed supply prevents inflation during demo
3. **Clawback Option**: Recovery mechanism for emergency situations
4. **Manager Controls**: Ability to adjust parameters if needed

## Implementation Checklist

### Pre-Demo Setup
- [ ] Mint HACK token with specified parameters
- [ ] Fund demo wallets with ALGO and HACK tokens
- [ ] Initialize ALGO-HACK pool with initial liquidity
- [ ] Configure oracle with ALGO-specific parameters
- [ ] Set up monitoring dashboard

### Demo Execution
- [ ] Validate all price bounds and limits
- [ ] Monitor transaction throughput and success rates
- [ ] Track volatility patterns and rebalancing triggers
- [ ] Record key metrics for presentation

### Post-Demo
- [ ] Archive simulation data
- [ ] Document any parameter adjustments made
- [ ] Prepare lessons learned summary

---

This specification provides the complete framework for implementing ALGO-HACK token pairing in the Seltra AMM hackathon demonstration, ensuring realistic trading conditions while maintaining demo safety and clarity.
