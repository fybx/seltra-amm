# FeeManager Specification

## Overview

The FeeManager dynamically adjusts trading fees based on market volatility, trading volume, and liquidity provider risk exposure. Higher volatility and lower liquidity result in higher fees to compensate LPs for increased risk.

## Contract Interface

### External Methods

#### Fee Calculation

```python
@external
def calculate_dynamic_fee(
    volatility: int,
    volume_24h: int,
    current_liquidity: int,
    trade_size: int
) -> tuple[int, int]:
    """
    Calculate dynamic trading fee for current market conditions.
    
    Args:
        volatility: Current volatility (basis points)
        volume_24h: 24-hour trading volume
        current_liquidity: Available liquidity for trade
        trade_size: Size of the trade
        
    Returns:
        (fee_rate, protocol_fee_rate)
        - fee_rate: Total fee rate in basis points
        - protocol_fee_rate: Protocol portion of fee in basis points
        
    Requires:
        - Called by authorized pool contract
        - Valid volatility and volume data
        - Positive trade size
    """

@external
def update_fee_parameters(
    base_fee: int,
    volatility_multiplier: int,
    volume_discount_factor: int,
    max_fee: int,
    protocol_fee_share: int
) -> None:
    """
    Update fee calculation parameters.
    
    Args:
        base_fee: Base fee rate in basis points (e.g., 30 = 0.3%)
        volatility_multiplier: Multiplier for volatility impact (fixed point)
        volume_discount_factor: Volume discount factor (fixed point)
        max_fee: Maximum allowed fee rate (basis points)
        protocol_fee_share: Protocol's share of fees (basis points)
        
    Requires:
        - Called by administrator
        - Parameters within valid ranges
    """
```

#### Volume Tracking

```python
@external
def record_trade(
    trade_size: int,
    fee_paid: int,
    asset_pair: tuple[int, int]
) -> None:
    """
    Record trading activity for fee calculation.
    
    Args:
        trade_size: Size of executed trade
        fee_paid: Fee amount collected
        asset_pair: (asset_x_id, asset_y_id) tuple
        
    Requires:
        - Called by authorized pool contract
        - Valid trade data
        
    Effects:
        - Updates volume statistics
        - Tracks fee collection
        - Updates trader fee tier if applicable
    """

@external
def get_trader_fee_tier(trader: bytes) -> tuple[int, int]:
    """
    Get fee tier and discount for specific trader.
    
    Args:
        trader: Trader address
        
    Returns:
        (fee_tier, discount_bps)
        - fee_tier: Trader's tier level (0-5)
        - discount_bps: Fee discount in basis points
        
    Requires:
        - Valid trader address
    """
```

### Read-Only Methods

```python
@external(readonly=True)
def simulate_fee_calculation(
    volatility: int,
    volume_24h: int,
    liquidity: int,
    trade_size: int,
    trader: bytes = None
) -> tuple[int, int, int]:
    """
    Simulate fee calculation without recording trade.
    
    Args:
        volatility: Market volatility
        volume_24h: Recent trading volume
        liquidity: Available liquidity
        trade_size: Proposed trade size
        trader: Optional trader address for tier calculation
        
    Returns:
        (base_fee, adjusted_fee, trader_discount)
    """

@external(readonly=True)
def get_current_fee_structure() -> tuple[int, int, int, int, int]:
    """
    Get current fee parameters.
    
    Returns:
        (base_fee, volatility_multiplier, max_fee, protocol_share, volume_factor)
    """

@external(readonly=True)
def get_volume_statistics() -> tuple[int, int, int, int]:
    """
    Get trading volume statistics.
    
    Returns:
        (volume_24h, volume_7d, average_trade_size, unique_traders_24h)
    """

@external(readonly=True)
def estimate_lp_yield(
    liquidity_amount: int,
    range_width: int,
    expected_volume: int
) -> int:
    """
    Estimate expected yield for LP position.
    
    Args:
        liquidity_amount: Amount of liquidity to provide
        range_width: Width of price range (basis points)
        expected_volume: Expected trading volume
        
    Returns:
        Estimated APY in basis points
    """
```

## State Management

### Global State Variables

```python
# Fee Configuration (48 bytes)
base_fee_rate: int              # 8 bytes - Base fee in basis points (default: 30)
volatility_multiplier: int      # 8 bytes - Volatility impact factor (fixed point)
volume_discount_factor: int     # 8 bytes - Volume discount factor (fixed point)
max_fee_rate: int              # 8 bytes - Maximum fee cap (basis points)
protocol_fee_share: int        # 8 bytes - Protocol's share (basis points, default: 1000 = 10%)
min_fee_rate: int              # 8 bytes - Minimum fee floor (basis points)

# Volume Tracking (64 bytes)
total_volume_24h: int          # 8 bytes - 24-hour trading volume
total_volume_7d: int           # 8 bytes - 7-day trading volume
total_fees_collected: int      # 8 bytes - Total fees collected
total_trades: int              # 8 bytes - Total number of trades
average_trade_size: int        # 8 bytes - Moving average trade size
unique_traders_24h: int        # 8 bytes - Number of unique traders (24h)
last_volume_update: int        # 8 bytes - Last volume update timestamp
volume_decay_rate: int         # 8 bytes - Rate for volume decay calculation

# Fee Tier Configuration (40 bytes)
tier_thresholds: list[int]     # 32 bytes - Volume thresholds for each tier (4 tiers)
tier_discounts: list[int]      # 32 bytes - Discount rates for each tier (basis points)

# Authorization (32 bytes)
admin_address: bytes           # 32 bytes - Administrator address
```

### Box Storage (Trader Data)

```python
# Trader Volume History
box_key = f"trader_{trader_address}"
class TraderDataBox:
    total_volume_30d: int       # 8 bytes - 30-day volume for tier calculation
    last_trade_time: int        # 8 bytes - Last trade timestamp
    trade_count: int            # 8 bytes - Total trades by this trader
    current_tier: int           # 8 bytes - Current fee tier (0-5)
    fees_paid_total: int        # 8 bytes - Total fees paid by trader
    last_tier_update: int       # 8 bytes - Last tier recalculation time

# Volume History (for decay calculations)
box_key = f"volume_history"
class VolumeHistoryBox:
    hourly_volumes: list[int]   # 168 * 8 = 1344 bytes (7 days of hourly data)
    daily_volumes: list[int]    # 30 * 8 = 240 bytes (30 days of daily data)
    current_hour_index: int     # 8 bytes - Current position in hourly array
    current_day_index: int      # 8 bytes - Current position in daily array
```

## Mathematical Formulas

### Dynamic Fee Calculation

```python
def calculate_dynamic_fee(
    base_fee: int,
    volatility: int,
    volume_24h: int,
    current_liquidity: int,
    trade_size: int,
    volatility_multiplier: int,
    volume_discount_factor: int,
    max_fee: int,
    min_fee: int
) -> int:
    """
    Calculate dynamic fee based on market conditions.
    
    Formula:
    adjusted_fee = base_fee * (1 + volatility_adjustment) * (1 - volume_discount) * liquidity_factor
    
    Where:
    - volatility_adjustment = (volatility / 1000) * volatility_multiplier
    - volume_discount = min(volume_24h / volume_threshold, max_discount) * volume_discount_factor
    - liquidity_factor = sqrt(optimal_liquidity / current_liquidity)
    """
    
    # 1. Volatility adjustment (higher volatility = higher fees)
    volatility_adjustment = (volatility * volatility_multiplier) // 10000
    volatility_fee = base_fee + (base_fee * volatility_adjustment) // 10000
    
    # 2. Volume discount (higher volume = lower fees)
    volume_threshold = 1000000  # $1M threshold for max discount
    if volume_24h > 0:
        volume_ratio = min(volume_24h * 10000 // volume_threshold, 5000)  # Max 50% discount base
        volume_discount = (volume_ratio * volume_discount_factor) // 10000
    else:
        volume_discount = 0
    
    volume_adjusted_fee = volatility_fee - (volatility_fee * volume_discount) // 10000
    
    # 3. Liquidity factor (less liquidity = higher fees for large trades)
    if current_liquidity > 0 and trade_size > 0:
        # Calculate utilization ratio
        utilization = (trade_size * 10000) // current_liquidity
        
        if utilization > 1000:  # If trade uses >10% of liquidity
            liquidity_penalty = min(utilization - 1000, 2000)  # Max 20% penalty
            liquidity_factor = 10000 + liquidity_penalty
        else:
            liquidity_factor = 10000
    else:
        liquidity_factor = 10000
    
    final_fee = (volume_adjusted_fee * liquidity_factor) // 10000
    
    # Apply bounds
    return max(min_fee, min(final_fee, max_fee))

def calculate_protocol_fee(total_fee: int, protocol_share: int) -> int:
    """Calculate protocol portion of trading fee."""
    return (total_fee * protocol_share) // 10000

def calculate_lp_fee(total_fee: int, protocol_fee: int) -> int:
    """Calculate liquidity provider portion of trading fee."""
    return total_fee - protocol_fee
```

### Volume-Based Fee Tiers

```python
def calculate_trader_tier(
    trader_volume_30d: int,
    tier_thresholds: list[int]
) -> int:
    """
    Calculate trader's fee tier based on 30-day volume.
    
    Tier structure:
    - Tier 0: < $10K volume (no discount)
    - Tier 1: $10K - $100K (5% discount)
    - Tier 2: $100K - $1M (10% discount)
    - Tier 3: $1M - $10M (15% discount)
    - Tier 4: > $10M (20% discount)
    """
    tier = 0
    for i, threshold in enumerate(tier_thresholds):
        if trader_volume_30d >= threshold:
            tier = i + 1
        else:
            break
    
    return min(tier, len(tier_thresholds))

def apply_trader_discount(
    base_fee: int,
    trader_tier: int,
    tier_discounts: list[int]
) -> int:
    """Apply tier-based discount to trading fee."""
    if trader_tier > 0 and trader_tier <= len(tier_discounts):
        discount = tier_discounts[trader_tier - 1]
        return base_fee - (base_fee * discount) // 10000
    return base_fee
```

### Volume Decay Calculation

```python
def update_volume_with_decay(
    current_volume: int,
    last_update_time: int,
    decay_rate: int
) -> int:
    """
    Apply exponential decay to volume metrics.
    
    Formula: volume(t) = volume(0) * e^(-decay_rate * time_elapsed)
    
    This ensures old volume doesn't artificially inflate current metrics.
    """
    current_time = get_current_timestamp()
    time_elapsed = current_time - last_update_time
    
    if time_elapsed <= 0:
        return current_volume
    
    # Convert to hours for decay calculation
    hours_elapsed = time_elapsed // 3600
    
    # Apply exponential decay (simplified using integer math)
    # decay_rate is in basis points per hour
    decay_factor = 10000 - min(decay_rate * hours_elapsed, 9000)  # Max 90% decay
    
    return (current_volume * decay_factor) // 10000

def update_trader_volume(
    trader_data: TraderDataBox,
    new_trade_volume: int,
    current_time: int
) -> TraderDataBox:
    """Update trader's volume history with decay."""
    # Apply decay to existing volume
    decayed_volume = update_volume_with_decay(
        trader_data.total_volume_30d,
        trader_data.last_trade_time,
        50  # 0.5% decay per hour
    )
    
    # Add new volume
    trader_data.total_volume_30d = decayed_volume + new_trade_volume
    trader_data.last_trade_time = current_time
    trader_data.trade_count += 1
    
    # Recalculate tier if needed
    if current_time - trader_data.last_tier_update > 86400:  # Daily tier updates
        trader_data.current_tier = calculate_trader_tier(
            trader_data.total_volume_30d,
            get_tier_thresholds()
        )
        trader_data.last_tier_update = current_time
    
    return trader_data
```

### LP Yield Estimation

```python
def estimate_lp_yield(
    liquidity_amount: int,
    range_width: int,
    expected_volume: int,
    current_fee_rate: int,
    volatility: int
) -> int:
    """
    Estimate expected APY for LP position.
    
    Factors considered:
    1. Fee generation from trading volume
    2. Range utilization based on volatility
    3. Compounding effect of fee reinvestment
    4. Impermanent loss risk adjustment
    """
    
    # 1. Calculate fee generation potential
    # Assume LP captures fees proportional to their liquidity share in active range
    daily_volume = expected_volume // 365
    
    # Estimate portion of volume that will use this range
    # Narrower ranges capture more fees but risk being out of range
    optimal_width = volatility * 4  # 4 standard deviations
    if range_width > 0:
        utilization_factor = min(optimal_width * 10000 // range_width, 10000)
    else:
        utilization_factor = 0
    
    # Calculate daily fees earned
    daily_fees = (daily_volume * current_fee_rate * utilization_factor) // (10000 * 10000)
    
    # 2. Account for impermanent loss risk
    # Narrower ranges have higher IL risk but higher fee potential
    il_risk_factor = 10000  # Start with no adjustment
    
    if range_width < volatility * 2:  # Range narrower than 2σ
        # Higher IL risk, reduce yield estimate
        il_risk_penalty = (volatility * 2 - range_width) * 10 // volatility
        il_risk_factor = 10000 - min(il_risk_penalty, 3000)  # Max 30% penalty
    
    adjusted_daily_fees = (daily_fees * il_risk_factor) // 10000
    
    # 3. Calculate APY
    if liquidity_amount > 0:
        daily_yield = (adjusted_daily_fees * 10000) // liquidity_amount
        annual_yield = daily_yield * 365
    else:
        annual_yield = 0
    
    return annual_yield
```

## Events

```python
class FeeUpdateEvent:
    """Emitted when fee parameters are updated."""
    old_base_fee: int
    new_base_fee: int
    old_volatility_multiplier: int
    new_volatility_multiplier: int
    timestamp: int

class TradeRecordedEvent:
    """Emitted when trade is recorded for fee calculation."""
    trader: bytes
    trade_size: int
    fee_paid: int
    trader_tier: int
    applied_discount: int
    timestamp: int

class TierUpdatedEvent:
    """Emitted when trader's tier is updated."""
    trader: bytes
    old_tier: int
    new_tier: int
    volume_30d: int
    timestamp: int
```

## Configuration Constants

```python
# Default Fee Parameters
DEFAULT_BASE_FEE = 30              # 0.30% base fee
DEFAULT_MAX_FEE = 300              # 3.00% maximum fee
DEFAULT_MIN_FEE = 5                # 0.05% minimum fee
DEFAULT_PROTOCOL_SHARE = 1000      # 10% to protocol
DEFAULT_VOLATILITY_MULTIPLIER = 5000  # 0.5x volatility impact
DEFAULT_VOLUME_DISCOUNT_FACTOR = 2000  # 0.2x volume discount

# Fee Tier Thresholds (in USD equivalent)
TIER_THRESHOLDS = [
    10000,    # $10K for Tier 1
    100000,   # $100K for Tier 2
    1000000,  # $1M for Tier 3
    10000000  # $10M for Tier 4
]

# Tier Discounts (basis points)
TIER_DISCOUNTS = [
    500,   # 5% discount for Tier 1
    1000,  # 10% discount for Tier 2
    1500,  # 15% discount for Tier 3
    2000   # 20% discount for Tier 4
]

# Volume Decay
DEFAULT_DECAY_RATE = 50  # 0.5% per hour
MAX_VOLUME_AGE = 2592000  # 30 days in seconds
```

## Error Codes

```python
class FeeManagerErrors:
    UNAUTHORIZED_CALLER = 4001
    INVALID_FEE_PARAMETERS = 4002
    FEE_EXCEEDS_MAXIMUM = 4003
    INVALID_TRADE_DATA = 4004
    TRADER_DATA_NOT_FOUND = 4005
    VOLUME_UPDATE_FAILED = 4006
    TIER_CALCULATION_ERROR = 4007
    INVALID_DISCOUNT_RATE = 4008
```

---

This specification defines the complete dynamic fee management system for the Seltra AMM, providing fair and efficient fee structures that adapt to market conditions while incentivizing trading volume and compensating liquidity providers for risk.
