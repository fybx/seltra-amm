# VolatilityOracle Specification

## Overview

The VolatilityOracle calculates real-time market volatility using Exponentially Weighted Moving Average (EWMA) and provides volatility regime classification to trigger dynamic liquidity rebalancing.

## Contract Interface

### External Methods

#### Price Updates

```python
@external
def update_price(new_price: int, volume: int) -> None:
    """
    Update the oracle with new price data from trading activity.
    
    Args:
        new_price: New market price (fixed point, 1e18 scale)
        volume: Trading volume for this price update
        
    Requires:
        - Called by authorized pool contract only
        - Price within reasonable bounds (max 10x movement)
        - Non-zero volume
        
    Effects:
        - Updates price history
        - Recalculates volatility metrics
        - May trigger rebalancing event
    """

@external
def force_volatility_update() -> None:
    """
    Force recalculation of volatility metrics.
    
    Requires:
        - Called by authorized administrator
        - At least one price update since last calculation
        
    Effects:
        - Recalculates all volatility metrics
        - Updates regime classification
    """
```

#### Configuration

```python
@external
def set_volatility_params(
    window_size: int,
    alpha: int,
    rebalance_threshold: int
) -> None:
    """
    Update volatility calculation parameters.
    
    Args:
        window_size: Number of price points to consider (10-50)
        alpha: EWMA smoothing factor (fixed point, 0.1-0.5 range)
        rebalance_threshold: Volatility change threshold for rebalancing (basis points)
        
    Requires:
        - Called by administrator only
        - Parameters within valid ranges
    """

@external
def set_authorized_caller(caller: bytes, authorized: bool) -> None:
    """
    Set authorization for price update callers.
    
    Args:
        caller: Address to authorize/deauthorize
        authorized: Whether address is authorized
        
    Requires:
        - Called by administrator only
    """
```

### Read-Only Methods

```python
@external(readonly=True)
def get_current_volatility() -> tuple[int, int, int]:
    """
    Get current volatility metrics.
    
    Returns:
        (volatility_value, regime, confidence_level)
        - volatility_value: Current volatility (basis points, 0-10000)
        - regime: 0=low, 1=medium, 2=high
        - confidence_level: Reliability of calculation (0-100)
    """

@external(readonly=True)
def get_price_history(count: int) -> list[tuple[int, int, int]]:
    """
    Get recent price history.
    
    Args:
        count: Number of recent price points to return (max 50)
        
    Returns:
        List of (price, volume, timestamp) tuples
    """

@external(readonly=True)
def should_rebalance() -> tuple[bool, int]:
    """
    Check if rebalancing should be triggered.
    
    Returns:
        (should_rebalance, new_regime)
        - should_rebalance: Whether to trigger rebalancing
        - new_regime: Target volatility regime (0-2)
    """

@external(readonly=True)
def get_volatility_metrics() -> tuple[int, int, int, int]:
    """
    Get detailed volatility analysis.
    
    Returns:
        (ewma_volatility, rolling_volatility, price_range, trend_direction)
        - ewma_volatility: EWMA-based volatility (basis points)
        - rolling_volatility: Simple rolling window volatility (basis points)
        - price_range: Price range over window (percentage, basis points)
        - trend_direction: -1=down, 0=sideways, 1=up
    """
```

## State Management

### Global State Variables

```python
# Core Volatility Data (80 bytes)
current_volatility: int      # 8 bytes - Current volatility (basis points)
volatility_regime: int       # 8 bytes - 0=low, 1=medium, 2=high
last_volatility: int         # 8 bytes - Previous volatility for comparison
last_update_time: int        # 8 bytes - Timestamp of last update
last_rebalance_trigger: int  # 8 bytes - Last rebalancing trigger time
confidence_score: int        # 8 bytes - Confidence in current calculation (0-100)
trend_direction: int         # 8 bytes - Market trend (-1, 0, 1)
price_range_24h: int         # 8 bytes - 24-hour price range (basis points)

# Configuration Parameters (32 bytes)
window_size: int             # 8 bytes - EWMA window size (default: 20)
alpha: int                   # 8 bytes - EWMA alpha parameter (fixed point)
rebalance_threshold: int     # 8 bytes - Threshold for triggering rebalance (basis points)
min_update_interval: int     # 8 bytes - Minimum time between updates (seconds)

# Authorization (32 bytes)
admin_address: bytes         # 32 bytes - Administrator address

# Statistics (32 bytes)
total_updates: int           # 8 bytes - Total price updates received
rebalance_triggers: int      # 8 bytes - Total rebalancing events triggered
last_major_move: int         # 8 bytes - Timestamp of last major price movement
average_daily_volatility: int # 8 bytes - 30-day average volatility
```

### Box Storage (Price History)

```python
# Recent Price Data (stored in boxes for efficient access)
box_key = f"price_history"
class PriceHistoryBox:
    prices: list[int]        # Up to 50 recent prices (400 bytes)
    volumes: list[int]       # Corresponding volumes (400 bytes)
    timestamps: list[int]    # Timestamps for each price (400 bytes)
    write_index: int         # Circular buffer write position (8 bytes)
    
# Volatility History (for longer-term analysis)
box_key = f"volatility_history"
class VolatilityHistoryBox:
    daily_volatilities: list[int]  # Last 30 days (240 bytes)
    regime_changes: list[tuple[int, int]]  # (timestamp, new_regime) (400 bytes)
    major_events: list[tuple[int, int]]    # (timestamp, volatility) for events >2σ (400 bytes)
```

## Mathematical Formulas

### EWMA Volatility Calculation

```python
def calculate_ewma_volatility(
    price_history: list[int],
    alpha: int,
    window_size: int
) -> int:
    """
    Calculate Exponentially Weighted Moving Average volatility.
    
    Formula: σ²(t) = α * r²(t) + (1-α) * σ²(t-1)
    Where r(t) = ln(P(t)/P(t-1)) is the return
    """
    if len(price_history) < 2:
        return 0
    
    # Calculate returns
    returns = []
    for i in range(1, min(len(price_history), window_size + 1)):
        if price_history[i-1] > 0:
            return_val = (price_history[i] - price_history[i-1]) * FIXED_POINT_SCALE // price_history[i-1]
            returns.append(return_val)
    
    if len(returns) < 2:
        return 0
    
    # Calculate EWMA variance
    variance = 0
    for i, ret in enumerate(returns):
        weight = pow(1 - alpha, i)
        variance += weight * ret * ret
    
    # Convert to volatility (standard deviation) in basis points
    volatility = int_sqrt(variance * 10000 // FIXED_POINT_SCALE)
    return min(volatility, 10000)  # Cap at 100%

def calculate_rolling_volatility(
    price_history: list[int],
    window_size: int
) -> int:
    """Calculate simple rolling window volatility for comparison."""
    if len(price_history) < window_size:
        return 0
    
    recent_prices = price_history[-window_size:]
    mean_price = sum(recent_prices) // len(recent_prices)
    
    variance = sum((price - mean_price) ** 2 for price in recent_prices) // len(recent_prices)
    volatility = int_sqrt(variance * 10000 // mean_price // mean_price)
    
    return min(volatility, 10000)
```

### Regime Classification

```python
def classify_volatility_regime(volatility: int) -> int:
    """
    Classify volatility into regimes for rebalancing decisions.
    
    Args:
        volatility: Current volatility in basis points
        
    Returns:
        0: Low volatility (< 200 bps = 2%)
        1: Medium volatility (200-800 bps = 2-8%)
        2: High volatility (> 800 bps = 8%)
    """
    if volatility < 200:
        return 0  # Low volatility
    elif volatility < 800:
        return 1  # Medium volatility
    else:
        return 2  # High volatility

def should_trigger_rebalance(
    current_volatility: int,
    last_volatility: int,
    current_regime: int,
    last_trigger_time: int,
    rebalance_threshold: int,
    min_interval: int
) -> bool:
    """
    Determine if rebalancing should be triggered.
    
    Conditions:
    1. Significant volatility change (> threshold)
    2. Regime change detected
    3. Sufficient time since last rebalance
    4. Volatility confidence above minimum level
    """
    now = get_current_timestamp()
    
    # Check minimum time interval
    if now - last_trigger_time < min_interval:
        return False
    
    # Check volatility change threshold
    volatility_change = abs(current_volatility - last_volatility)
    if volatility_change < rebalance_threshold:
        return False
    
    # Check for regime change
    new_regime = classify_volatility_regime(current_volatility)
    if new_regime != current_regime:
        return True
    
    # Check for significant volatility spike
    if volatility_change > 2 * rebalance_threshold:
        return True
    
    return False
```

### Price Movement Analysis

```python
def calculate_price_metrics(
    price_history: list[int],
    volume_history: list[int],
    time_window: int
) -> tuple[int, int, int]:
    """
    Calculate price movement metrics for volatility analysis.
    
    Returns:
        (price_range, trend_strength, volume_weighted_price)
    """
    if len(price_history) < 2:
        return (0, 0, 0)
    
    # Calculate price range over window
    recent_prices = price_history[-time_window:]
    price_min = min(recent_prices)
    price_max = max(recent_prices)
    price_range = ((price_max - price_min) * 10000) // price_min
    
    # Calculate trend strength using linear regression
    n = len(recent_prices)
    x_sum = n * (n - 1) // 2
    y_sum = sum(recent_prices)
    xy_sum = sum(i * price for i, price in enumerate(recent_prices))
    x2_sum = n * (n - 1) * (2 * n - 1) // 6
    
    if n * x2_sum - x_sum * x_sum != 0:
        slope = (n * xy_sum - x_sum * y_sum) // (n * x2_sum - x_sum * x_sum)
        trend_strength = abs(slope * 10000 // (y_sum // n))
    else:
        trend_strength = 0
    
    # Calculate volume-weighted average price
    if len(volume_history) >= len(recent_prices) and sum(volume_history[-len(recent_prices):]) > 0:
        total_volume = sum(volume_history[-len(recent_prices):])
        vwap = sum(p * v for p, v in zip(recent_prices, volume_history[-len(recent_prices):])) // total_volume
    else:
        vwap = sum(recent_prices) // len(recent_prices)
    
    return (price_range, trend_strength, vwap)
```

## Events

```python
class VolatilityUpdateEvent:
    """Emitted when volatility metrics are updated."""
    old_volatility: int
    new_volatility: int
    old_regime: int
    new_regime: int
    confidence_score: int
    timestamp: int

class RebalanceTriggerEvent:
    """Emitted when rebalancing is triggered."""
    trigger_volatility: int
    volatility_change: int
    old_regime: int
    new_regime: int
    timestamp: int

class PriceUpdateEvent:
    """Emitted on significant price movements."""
    new_price: int
    price_change: int
    volume: int
    volatility_impact: int
    timestamp: int
```

## Configuration Constants

```python
# Volatility Calculation
DEFAULT_WINDOW_SIZE = 20         # Number of price points
DEFAULT_ALPHA = 3000             # EWMA alpha (0.3 in fixed point)
DEFAULT_REBALANCE_THRESHOLD = 50 # 0.5% volatility change threshold
MIN_UPDATE_INTERVAL = 30         # Minimum 30 seconds between updates
MAX_VOLATILITY = 10000           # Maximum 100% volatility

# Regime Thresholds
LOW_VOLATILITY_THRESHOLD = 200   # 2% volatility
HIGH_VOLATILITY_THRESHOLD = 800  # 8% volatility

# ALGO-HACK Specific Thresholds (higher for crypto)
ALGO_HACK_LOW_VOLATILITY = 400   # 4% volatility (crypto baseline)
ALGO_HACK_HIGH_VOLATILITY = 1500 # 15% volatility (crypto high threshold)

# Confidence Scoring
MIN_CONFIDENCE_UPDATES = 5       # Minimum updates for reliable calculation
CONFIDENCE_DECAY_RATE = 100      # Confidence decay per hour without updates

# Safety Limits
MAX_PRICE_CHANGE = 1000          # Maximum 10% price change per update
MAX_HISTORY_SIZE = 50            # Maximum price history length

# ALGO-HACK Specific Configuration
ALGO_HACK_VOLATILITY_CONFIG = {
    # Adjusted parameters for crypto volatility patterns
    "WINDOW_SIZE": 15,                    # Shorter window for faster adaptation
    "ALPHA": 4000,                        # 0.4 (more responsive EWMA)
    "REBALANCE_THRESHOLD": 100,           # 1% change triggers rebalance
    "MIN_UPDATE_INTERVAL": 15,            # 15 seconds (faster updates)
    
    # Crypto-appropriate thresholds
    "LOW_VOLATILITY_THRESHOLD": 400,      # 4% (crypto low)
    "HIGH_VOLATILITY_THRESHOLD": 1500,    # 15% (crypto high)
    
    # Higher price change tolerance
    "MAX_PRICE_CHANGE": 3000,             # 30% max change (crypto markets)
    "EXTREME_VOLATILITY_THRESHOLD": 2500, # 25% extreme volatility
    
    # Enhanced confidence scoring
    "MIN_CONFIDENCE_UPDATES": 3,          # Faster confidence building
    "CONFIDENCE_DECAY_RATE": 150,         # Faster confidence decay
    
    # Regime switching parameters
    "REGIME_PERSISTENCE": 5,              # Regime must persist 5 updates
    "VOLATILITY_SMOOTHING": 0.7,          # Smooth volatility estimates
}

def classify_algo_hack_regime(volatility: int) -> int:
    """
    Classify volatility regime for ALGO-HACK pair.
    
    Returns:
        0: Low volatility (< 4%)
        1: Medium volatility (4-15%) 
        2: High volatility (> 15%)
    """
    if volatility < ALGO_HACK_LOW_VOLATILITY:
        return 0
    elif volatility < ALGO_HACK_HIGH_VOLATILITY:
        return 1
    else:
        return 2
```

## Error Codes

```python
class VolatilityOracleErrors:
    UNAUTHORIZED_CALLER = 2001
    INVALID_PRICE = 2002
    INSUFFICIENT_HISTORY = 2003
    INVALID_PARAMETERS = 2004
    UPDATE_TOO_FREQUENT = 2005
    PRICE_CHANGE_TOO_LARGE = 2006
    ZERO_VOLUME = 2007
    CALCULATION_OVERFLOW = 2008
```

## Security Considerations

### Input Validation
- Price movements limited to reasonable bounds (max 10% per update)
- Volume must be positive and non-zero
- Update frequency limits to prevent spam
- Parameter bounds checking for configuration changes

### Oracle Manipulation Protection
- Minimum time intervals between price updates
- Volume-weighted price calculations to reduce manipulation impact
- Outlier detection and filtering
- Multiple data source validation (future enhancement)

### Fallback Mechanisms
- Default to conservative volatility estimates if calculation fails
- Graceful degradation with limited price history
- Emergency pause functionality for extreme market conditions

---

This specification defines the complete volatility calculation and regime detection system for the Seltra AMM, providing the intelligence needed for dynamic liquidity management.
