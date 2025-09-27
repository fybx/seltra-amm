# SeltraPoolContract Specification

## Overview

The main AMM contract implementing concentrated liquidity with dynamic range management. Handles all trading operations, liquidity management, and coordinates with oracle and rebalancing systems.

## Contract Interface

### External Methods

#### Trading Operations

```python
@external
def swap(
    asset_in: Asset,
    asset_out: Asset,
    amount_in: int,
    min_amount_out: int,
    deadline: int
) -> int:
    """
    Execute a token swap with slippage protection.
    
    Args:
        asset_in: Input asset ID
        asset_out: Output asset ID  
        amount_in: Amount of input asset
        min_amount_out: Minimum acceptable output amount
        deadline: Transaction deadline timestamp
        
    Returns:
        Actual amount of output asset transferred
        
    Requires:
        - Valid asset pair
        - Sufficient input balance
        - Amount within slippage tolerance
        - Before deadline
    """
```

#### Liquidity Management

```python
@external
def add_liquidity(
    asset_x: Asset,
    asset_y: Asset,
    amount_x_desired: int,
    amount_y_desired: int,
    amount_x_min: int,
    amount_y_min: int,
    range_lower: int,
    range_upper: int,
    deadline: int
) -> tuple[int, int, int]:
    """
    Add liquidity to a specific price range.
    
    Args:
        asset_x: First asset in pair
        asset_y: Second asset in pair
        amount_x_desired: Desired amount of asset X
        amount_y_desired: Desired amount of asset Y
        amount_x_min: Minimum amount of asset X
        amount_y_min: Minimum amount of asset Y
        range_lower: Lower bound of price range (fixed point)
        range_upper: Upper bound of price range (fixed point)
        deadline: Transaction deadline timestamp
        
    Returns:
        (actual_amount_x, actual_amount_y, lp_tokens_minted)
        
    Requires:
        - Valid price range (lower < upper)
        - Sufficient asset balances
        - Range within acceptable bounds
        - Before deadline
    """

@external
def remove_liquidity(
    lp_token_amount: int,
    amount_x_min: int,
    amount_y_min: int,
    deadline: int
) -> tuple[int, int]:
    """
    Remove liquidity and claim underlying assets.
    
    Args:
        lp_token_amount: Amount of LP tokens to burn
        amount_x_min: Minimum amount of asset X to receive
        amount_y_min: Minimum amount of asset Y to receive
        deadline: Transaction deadline timestamp
        
    Returns:
        (amount_x_received, amount_y_received)
        
    Requires:
        - Sufficient LP token balance
        - Minimum amounts achievable
        - Before deadline
    """
```

#### Administrative Operations

```python
@external
def initialize_pool(
    asset_x: Asset,
    asset_y: Asset,
    initial_price: int,
    volatility_oracle: bytes,
    rebalancing_engine: bytes,
    fee_manager: bytes
) -> None:
    """
    Initialize a new liquidity pool.
    
    Args:
        asset_x: First asset in the pair
        asset_y: Second asset in the pair
        initial_price: Starting price (asset_y per asset_x, fixed point)
        volatility_oracle: Address of volatility oracle contract
        rebalancing_engine: Address of rebalancing engine contract
        fee_manager: Address of fee manager contract
        
    Requires:
        - Called by creator only
        - Assets not already paired
        - Valid contract addresses
    """

@external
def trigger_rebalance() -> None:
    """
    Trigger liquidity range rebalancing based on current volatility.
    
    Requires:
        - Called by authorized rebalancing engine
        - Sufficient time since last rebalance
        - Volatility change exceeds threshold
    """
```

### Read-Only Methods

```python
@external(readonly=True)
def get_pool_info() -> tuple[int, int, int, int, int]:
    """
    Get current pool state information.
    
    Returns:
        (asset_x_id, asset_y_id, current_price, total_liquidity, current_fee_rate)
    """

@external(readonly=True)
def get_liquidity_ranges() -> list[tuple[int, int, int, int, bool]]:
    """
    Get all current liquidity ranges.
    
    Returns:
        List of (range_id, price_lower, price_upper, liquidity_amount, is_active)
    """

@external(readonly=True)
def calculate_swap_output(
    asset_in: Asset,
    asset_out: Asset,
    amount_in: int
) -> tuple[int, int]:
    """
    Calculate expected output for a swap without executing.
    
    Returns:
        (amount_out, price_impact_bps)
    """

@external(readonly=True)
def get_user_positions(user: bytes) -> list[tuple[int, int, int]]:
    """
    Get user's liquidity positions.
    
    Returns:
        List of (range_id, lp_tokens, unclaimed_fees)
    """
```

## State Management

### Global State Variables

```python
# Pool Configuration (64 bytes total)
asset_x_id: int              # 8 bytes - Asset X identifier
asset_y_id: int              # 8 bytes - Asset Y identifier
current_price: int           # 8 bytes - Current price (fixed point, 1e18)
total_liquidity: int         # 8 bytes - Total liquidity value
current_fee_rate: int        # 8 bytes - Current fee rate (basis points)
last_rebalance_time: int     # 8 bytes - Last rebalance timestamp
protocol_fees_x: int        # 8 bytes - Accumulated protocol fees for asset X
protocol_fees_y: int        # 8 bytes - Accumulated protocol fees for asset Y

# Contract Addresses (96 bytes total)
volatility_oracle: bytes    # 32 bytes - VolatilityOracle contract address
rebalancing_engine: bytes   # 32 bytes - RebalancingEngine contract address
fee_manager: bytes          # 32 bytes - FeeManager contract address

# Liquidity Ranges (variable, up to 7 ranges * 40 bytes = 280 bytes)
num_active_ranges: int      # 8 bytes - Number of active ranges
ranges: list[LiquidityRange] # Variable - Active liquidity ranges
```

### Local State (Per User)

```python
# User Positions (24 bytes per user)
lp_token_balance: int       # 8 bytes - Total LP tokens owned
active_ranges_bitmap: int   # 8 bytes - Bitmap of ranges user has positions in
last_fee_claim: int         # 8 bytes - Last fee claim timestamp
```

### Box Storage (For Large Data)

```python
# Range Details (40 bytes per range, stored in boxes)
box_key = f"range_{range_id}"
class LiquidityRangeBox:
    range_id: int           # 8 bytes
    price_lower: int        # 8 bytes - Lower price bound (fixed point)
    price_upper: int        # 8 bytes - Upper price bound (fixed point)
    liquidity_amount: int   # 8 bytes - Total liquidity in range
    fees_collected_x: int   # 4 bytes - Fees collected for asset X
    fees_collected_y: int   # 4 bytes - Fees collected for asset Y

# User Range Positions (24 bytes per user per range)
box_key = f"position_{user_address}_{range_id}"
class UserPositionBox:
    lp_tokens: int          # 8 bytes - LP tokens in this range
    fee_growth_x_last: int  # 8 bytes - Last recorded fee growth X
    fee_growth_y_last: int  # 8 bytes - Last recorded fee growth Y
```

## Mathematical Formulas

### Price Calculation

```python
def calculate_price_from_reserves(reserve_x: int, reserve_y: int) -> int:
    """Calculate current price as reserve_y / reserve_x in fixed point."""
    return (reserve_y * FIXED_POINT_SCALE) // reserve_x

def get_price_at_tick(tick: int) -> int:
    """Convert tick to price using: price = 1.0001^tick"""
    return int(1.0001 ** tick * FIXED_POINT_SCALE)
```

### Swap Calculation (Concentrated Liquidity)

```python
def calculate_swap_amount_out(
    amount_in: int,
    liquidity: int,
    price_current: int,
    price_lower: int,
    price_upper: int,
    fee_rate: int
) -> int:
    """
    Calculate output amount for concentrated liquidity swap.
    Uses Uniswap V3 formula adapted for Algorand.
    """
    # Apply fee
    amount_in_after_fee = amount_in * (10000 - fee_rate) // 10000
    
    # Calculate based on current price position within range
    if price_current <= price_lower:
        # Price below range - no liquidity available
        return 0
    elif price_current >= price_upper:
        # Price above range - swap at upper bound
        sqrt_price_upper = int_sqrt(price_upper)
        amount_out = (amount_in_after_fee * liquidity) // sqrt_price_upper
    else:
        # Price within range - use current price
        sqrt_price_current = int_sqrt(price_current)
        amount_out = (amount_in_after_fee * liquidity) // sqrt_price_current
    
    return amount_out
```

### Liquidity Calculation

```python
def calculate_liquidity_for_amounts(
    amount_x: int,
    amount_y: int,
    price_lower: int,
    price_upper: int,
    price_current: int
) -> int:
    """Calculate liquidity that can be provided with given amounts."""
    sqrt_price_lower = int_sqrt(price_lower)
    sqrt_price_upper = int_sqrt(price_upper)
    sqrt_price_current = int_sqrt(price_current)
    
    if price_current <= price_lower:
        # All in asset X
        liquidity = (amount_x * sqrt_price_lower * sqrt_price_upper) // (sqrt_price_upper - sqrt_price_lower)
    elif price_current >= price_upper:
        # All in asset Y  
        liquidity = amount_y // (sqrt_price_upper - sqrt_price_lower)
    else:
        # Mixed assets
        liquidity_x = (amount_x * sqrt_price_current * sqrt_price_upper) // (sqrt_price_upper - sqrt_price_current)
        liquidity_y = amount_y // (sqrt_price_current - sqrt_price_lower)
        liquidity = min(liquidity_x, liquidity_y)
    
    return liquidity
```

## Events

```python
class SwapEvent:
    """Emitted on each swap transaction."""
    user: bytes
    asset_in: int
    asset_out: int
    amount_in: int
    amount_out: int
    fee_paid: int
    new_price: int
    timestamp: int

class LiquidityEvent:
    """Emitted on liquidity changes."""
    user: bytes
    action: str  # "add" or "remove"
    range_id: int
    amount_x: int
    amount_y: int
    lp_tokens: int
    timestamp: int

class RebalanceEvent:
    """Emitted on range rebalancing."""
    old_ranges: list[tuple[int, int, int]]  # (id, lower, upper)
    new_ranges: list[tuple[int, int, int]]  # (id, lower, upper)
    trigger_volatility: int
    gas_used: int
    timestamp: int
```

## Error Codes

```python
class SeltraPoolErrors:
    INVALID_ASSET_PAIR = 1001
    INSUFFICIENT_LIQUIDITY = 1002
    SLIPPAGE_EXCEEDED = 1003
    INVALID_RANGE = 1004
    DEADLINE_EXCEEDED = 1005
    UNAUTHORIZED_REBALANCE = 1006
    MINIMUM_LIQUIDITY_NOT_MET = 1007
    INVALID_FEE_RATE = 1008
    POOL_NOT_INITIALIZED = 1009
    REBALANCE_TOO_FREQUENT = 1010
```

## Gas Optimization

### Techniques Used

1. **Batch Operations**: Group multiple range updates in single transaction
2. **State Minimization**: Use bitmaps for range membership
3. **Box Storage**: Store large data structures in boxes instead of global state
4. **Lazy Updates**: Defer expensive calculations until needed
5. **Fixed Point Math**: Use integer arithmetic to avoid floating point

### Gas Budget Allocation

- **Swap Operation**: ~400 opcodes
- **Add Liquidity**: ~500 opcodes  
- **Remove Liquidity**: ~450 opcodes
- **Rebalance**: ~600 opcodes
- **Oracle Update**: ~200 opcodes

## Security Considerations

### Input Validation

- All price ranges must satisfy: `0 < price_lower < price_upper < MAX_PRICE`
- Amounts must be non-zero and within reasonable bounds
- Deadlines must be in the future but not too far
- Asset IDs must be valid and match pool configuration

### Reentrancy Protection

- Use atomic transaction groups for complex operations
- State changes before external calls
- Validate sender and receiver addresses

### Oracle Dependency

- Graceful degradation if oracle fails
- Maximum staleness checks for price data
- Fallback to time-weighted average price

---

This specification defines the complete interface and behavior of the SeltraPoolContract, serving as the definitive reference for implementation.
