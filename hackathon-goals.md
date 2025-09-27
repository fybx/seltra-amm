# the vocal part

## what are we building
Seltra AMM - An intelligent, self-adapting liquidity pool system that thinks and responds to market conditions in real-time. Unlike traditional "dumb" AMMs that sit static with fixed parameters, Seltra gives liquidity pools a brain that continuously optimizes for better trader execution and higher LP returns. Built on Algorand for 4.5-second finality and atomic transaction capabilities.

## what does it solve
Current AMMs are capital inefficient and hurt both traders and liquidity providers. Traders face high slippage on large trades and unpredictable execution. LPs earn poor returns (often <5% APY) while suffering impermanent loss from static positioning. The market wastes billions in locked capital that could be deployed more efficiently. Seltra solves this by making liquidity pools intelligent - they automatically concentrate capital where trading actually happens, adjust fees based on market volatility, and rebalance to capture value instead of losing it.

## how does it work
Three core innovations working together:
1. **Dynamic Liquidity Concentration**: When markets are calm, liquidity concentrates tightly around current price for better execution (achieving <0.1% slippage target); when volatile, it spreads wider for protection. This is our primary slippage minimization mechanism.
2. **Smart Rebalancing**: The system watches where trading actually happens and moves liquidity there proactively, using predictive algorithms to pre-position capital.
3. **Adaptive Fee Structure**: Fees automatically adjust from 0.05% in quiet markets to 0.30% during volatility, with volume discounts for large traders. A volatility oracle continuously measures market conditions and triggers these adaptations in real-time.

## key promises
- **Slippage Minimization**: <0.1% average slippage achieved through dynamic concentration (NOT just routing)
- **Capital Efficiency**: 3-5x better than traditional AMMs
- **Better LP Returns**: 15%+ APY through intelligent positioning

# the real part

- [ ] non-web3 part
    - [ ] simulations (volatile, normal) with "real" wallets
    - [ ] dockerization for deployment of algorand network and our servers
    - [ ] base for frontend
- [ ] web3