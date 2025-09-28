# HACK Token Contract

This directory contains the deployment infrastructure for the HACK ASA token used in the Seltra AMM hackathon demonstration.

## Overview

The HACK token is an Algorand Standard Asset (ASA) that pairs with ALGO in our demonstration AMM pools. It serves as the demonstration token for showcasing Seltra's intelligent AMM features.

## Token Specifications

- **Name**: HACK
- **Unit Name**: HACK  
- **Decimals**: 6 (matching ALGO)
- **Total Supply**: 1,000,000,000,000 microHACK (1M HACK tokens)
- **Type**: ASA (Algorand Standard Asset)

## Files

### `token_config.py`
Contains all configuration constants and parameters:
- `HACK_TOKEN_SPEC`: Core token specifications
- `ALGO_HACK_POOL_CONFIG`: Pool configuration for ALGO-HACK pair
- `DEMO_PARAMETERS`: Demo-specific safety parameters
- `HACK_DISTRIBUTION`: Token distribution strategy  
- `WALLET_FUNDING`: Wallet funding configuration

### `deploy_config.py`
Contains the deployment logic:
- `HACKTokenDeployer`: Main deployment class
- ASA creation with proper metadata
- Deployment verification
- Error handling and logging

### `__init__.py` 
Package initialization with exports for easy importing.

## Usage

### Quick Deployment

Deploy just the HACK token:

```bash
python scripts/deploy_hack_token.py
```

### Complete System Deployment

Deploy HACK token and prepare ALGO-HACK pool:

```bash
python scripts/deploy_algo_hack_pool.py
```

### Programmatic Usage

```python
from contracts.hack_token import HACKTokenDeployer, get_hack_token_config

# Get configuration
config = get_hack_token_config()

# Deploy token
deployer = HACKTokenDeployer(algod_client, indexer_client)
asset_id, txn_id = await deployer.deploy_hack_token(creator_account)
```

## Integration with Pool Contracts

The HACK token integrates with Seltra pool contracts as follows:

1. **Token Creation**: HACK ASA is created with management addresses
2. **Pool Configuration**: Asset ID is added to pool configuration
3. **Initial Liquidity**: Pool is funded with ALGO and HACK tokens
4. **Demo Wallets**: Wallets are funded with both tokens for simulation

## Distribution Strategy

Based on `specs/algo-hack-token-spec.md`:

- **Pool Liquidity**: 100K HACK (10%)
- **Demo Wallets**: 500K HACK (50%)  
  - Retail wallets: 300K HACK (15 wallets)
  - Whale wallets: 200K HACK (5 wallets)
- **Reserve**: 400K HACK (40%)

## Network Support

- **LocalNet**: Automatic using AlgoKit default account
- **TestNet**: Requires `HACK_TOKEN_DEPLOYER_PRIVATE_KEY` environment variable
- **MainNet**: Not recommended for demo tokens

## Safety Features

- **Price Bounds**: 0.5 - 2.0 HACK per ALGO
- **Trade Limits**: 1 ALGO minimum, 5K ALGO maximum per trade
- **Supply Control**: Fixed supply prevents inflation
- **Management Rights**: Creator retains freeze/clawback capabilities

## Output Files

- `hack_token_deployment.json`: Single token deployment info
- `algo_hack_system_deployment.json`: Complete system deployment info

## Next Steps

After deploying the HACK token:

1. Deploy Seltra pool contract with ALGO-HACK configuration
2. Initialize pool with initial liquidity (50K ALGO + 50K HACK)
3. Fund demo wallets according to distribution strategy
4. Start simulation with real blockchain backend

## Troubleshooting

### Common Issues

**Insufficient Balance**: Deployer needs at least 1 ALGO for token creation

**Network Connection**: Ensure Algorand node is running and accessible

**Account Configuration**: For TestNet, set `HACK_TOKEN_DEPLOYER_PRIVATE_KEY`

### Validation

The deployment scripts include validation against specifications:

```bash
python scripts/deploy_algo_hack_pool.py
# Runs specification validation before deployment
```

## Development

To modify token parameters, update `token_config.py` and ensure changes align with `specs/algo-hack-token-spec.md`.

Remember: ASAs are immutable after creation. Parameter changes require new token deployment.
