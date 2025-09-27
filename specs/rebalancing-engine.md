# RebalancingEngine Specification

## Overview

The RebalancingEngine calculates optimal liquidity concentration ranges based on volatility regimes and executes atomic rebalancing operations to redistribute liquidity across price ranges for maximum capital efficiency.

## Contract Interface

### External Methods

#### Rebalancing Operations

```python
@external
def calculate_optimal_ranges(
    current_price: int,
    volatility: int,
    regime: int,
    total_liquidity: int
) -> list[tuple[int, int, int]]:
    """
    Calculate optimal liquidity ranges for current market conditions.
    
    Args:
        current_price: Current market price (fixed point)
        volatility: Current volatility (basis points)
        regime: Volatility regime (0=low, 1=medium, 2=high)
        total_liquidity: Total available liquidity to distribute
        
    Returns:
        List of (price_lower, price_upper, liquidity_amount) tuples
        
    Requires:
        - Called by authorized pool contract
        - Valid volatility regime (0-2)
        - Positive total liquidity
    """

@external
def execute_rebalance(
    pool_address: bytes,
    old_ranges: list[tuple[int, int, int]],
    new_ranges: list[tuple[int, int, int]]
) -> None:
    """
    Execute atomic rebalancing operation.
    
    Args:
        pool_address: Target pool contract address
        old_ranges: Current ranges to close (id, lower, upper)
        new_ranges: New ranges to create (lower, upper, liquidity)
        
    Requires:
        - Called by authorized pool contract
        - Total liquidity conservation
        - Valid range specifications
        
    Effects:
        - Removes liquidity from old ranges
        - Creates new optimized ranges
        - Preserves total liquidity value
    """

@external
def validate_rebalance_proposal(
    current_ranges: list[tuple[int, int, int]],
    proposed_ranges: list[tuple[int, int, int]],
    current_price: int,
    volatility: int
) -> tuple[bool, int]:
    """
    Validate a proposed rebalancing operation.
    
    Args:
        current_ranges: Existing liquidity ranges
        proposed_ranges: Proposed new ranges
        current_price: Current market price
        volatility: Current volatility level
        
    Returns:
        (is_valid, efficiency_score)
        - is_valid: Whether proposal passes validation
        - efficiency_score: Expected efficiency improvement (basis points)
        
    Requires:
        - Called by authorized entities
    """
```

#### Configuration Management

```python
@external
def set_rebalancing_params(
    concentration_factors: list[int],
    range_counts: list[int],
    min_range_size: int,
    max_concentration: int
) -> None:
    """
    Update rebalancing parameters for different volatility regimes.
    
    Args:
        concentration_factors: Concentration multipliers for each regime [low, med, high]
        range_counts: Number of ranges for each regime [low, med, high]
        min_range_size: Minimum range size (basis points)
        max_concentration: Maximum concentration factor
        
    Requires:
        - Called by administrator
        - Valid parameter ranges
    """

@external
def set_safety_params(
    max_slippage: int,
    min_liquidity_per_range: int,
    rebalance_cooldown: int
) -> None:
    """
    Update safety parameters for rebalancing operations.
    
    Args:
        max_slippage: Maximum allowed slippage during rebalancing (basis points)
        min_liquidity_per_range: Minimum liquidity required per range
        rebalance_cooldown: Minimum time between rebalances (seconds)
        
    Requires:
        - Called by administrator
        - Parameters within safe bounds
    """
```

### Read-Only Methods

```python
@external(readonly=True)
def simulate_rebalance(
    current_price: int,
    volatility: int,
    regime: int,
    total_liquidity: int
) -> tuple[list[tuple[int, int, int]], int, int]:
    """
    Simulate rebalancing without execution.
    
    Args:
        current_price: Current market price
        volatility: Current volatility
        regime: Volatility regime
        total_liquidity: Available liquidity
        
    Returns:
        (proposed_ranges, efficiency_gain, gas_estimate)
        - proposed_ranges: Optimal ranges for conditions
        - efficiency_gain: Expected efficiency improvement (basis points)
        - gas_estimate: Estimated gas cost for execution
    """

@external(readonly=True)
def get_rebalancing_params() -> tuple[list[int], list[int], int, int]:
    """
    Get current rebalancing parameters.
    
    Returns:
        (concentration_factors, range_counts, min_range_size, max_concentration)
    """

@external(readonly=True)
def calculate_efficiency_score(
    ranges: list[tuple[int, int, int]],
    current_price: int,
    volatility: int
) -> int:
    """
    Calculate efficiency score for given range configuration.
    
    Args:
        ranges: Liquidity ranges to evaluate
        current_price: Current market price
        volatility: Current volatility
        
    Returns:
        Efficiency score (0-10000, higher is better)
    """

@external(readonly=True)
def get_last_rebalance_info() -> tuple[int, int, int, list[tuple[int, int, int]]]:
    """
    Get information about the last rebalancing operation.
    
    Returns:
        (timestamp, trigger_volatility, efficiency_gain, resulting_ranges)
    """
```

## State Management

### Global State Variables

```python
# Rebalancing Configuration (96 bytes)
concentration_factors: list[int]  # 24 bytes - [low, med, high] regime factors
range_counts: list[int]          # 24 bytes - [low, med, high] range counts
min_range_size: int              # 8 bytes - Minimum range size (basis points)
max_concentration: int           # 8 bytes - Maximum concentration factor
min_liquidity_per_range: int     # 8 bytes - Minimum liquidity per range
max_slippage: int                # 8 bytes - Maximum rebalance slippage (basis points)
rebalance_cooldown: int          # 8 bytes - Cooldown period between rebalances (seconds)
admin_address: bytes             # 32 bytes - Administrator address

# Rebalancing History (64 bytes)
last_rebalance_time: int         # 8 bytes - Timestamp of last rebalance
last_trigger_volatility: int     # 8 bytes - Volatility that triggered last rebalance
last_efficiency_gain: int        # 8 bytes - Efficiency improvement from last rebalance
total_rebalances: int            # 8 bytes - Total number of rebalances executed
successful_rebalances: int       # 8 bytes - Number of successful rebalances
failed_rebalances: int           # 8 bytes - Number of failed rebalance attempts
total_gas_used: int              # 8 bytes - Cumulative gas used for rebalancing
average_efficiency_gain: int     # 8 bytes - Average efficiency gain per rebalance

# Authorization (64 bytes)
authorized_pools: bytes          # Up to 2 pool contracts (64 bytes)
```

### Box Storage (Rebalancing History)

```python
# Recent Rebalancing Operations
box_key = f"rebalance_history"
class RebalanceHistoryBox:
    operations: list[RebalanceOperation]  # Last 20 operations (1600 bytes)

@dataclass
class RebalanceOperation:
    timestamp: int                   # 8 bytes
    trigger_volatility: int          # 8 bytes
    old_ranges: list[tuple[int, int, int]]  # Variable size
    new_ranges: list[tuple[int, int, int]]  # Variable size
    efficiency_gain: int             # 8 bytes
    gas_used: int                    # 8 bytes
    success: bool                    # 1 byte (packed)
```

## Mathematical Formulas

### Range Calculation Algorithm

```python
def calculate_optimal_ranges(
    current_price: int,
    volatility: int,
    regime: int,
    total_liquidity: int,
    concentration_factors: list[int],
    range_counts: list[int]
) -> list[tuple[int, int, int]]:
    """
    Calculate optimal liquidity ranges using volatility-adaptive algorithm.
    
    Algorithm:
    1. Determine concentration factor based on regime
    2. Calculate price bounds using volatility
    3. Distribute ranges symmetrically around current price
    4. Allocate liquidity based on distance from current price
    """
    
    concentration_factor = concentration_factors[regime]
    num_ranges = range_counts[regime]
    
    # Calculate price bounds based on volatility
    # Higher volatility = wider bounds
    volatility_multiplier = volatility * concentration_factor // 10000
    price_bound_percent = min(volatility_multiplier, 5000)  # Cap at 50%
    
    max_price = current_price * (10000 + price_bound_percent) // 10000
    min_price = current_price * (10000 - price_bound_percent) // 10000
    
    # Create symmetric ranges around current price
    ranges = []
    range_size = (max_price - min_price) // num_ranges
    
    for i in range(num_ranges):
        # Calculate range bounds
        lower = min_price + i * range_size
        upper = min_price + (i + 1) * range_size
        
        # Calculate liquidity allocation based on distance from current price
        range_center = (lower + upper) // 2
        distance_from_current = abs(range_center - current_price)
        max_distance = (max_price - min_price) // 2
        
        # More liquidity closer to current price
        if max_distance > 0:
            distance_factor = (max_distance - distance_from_current) * 10000 // max_distance
        else:
            distance_factor = 10000
        
        # Allocate liquidity with bias toward current price
        base_allocation = total_liquidity // num_ranges
        distance_adjustment = (base_allocation * distance_factor) // 20000  # 50% max adjustment
        liquidity_amount = base_allocation + distance_adjustment
        
        ranges.append((lower, upper, liquidity_amount))
    
    # Normalize liquidity to ensure total is preserved
    total_allocated = sum(r[2] for r in ranges)
    if total_allocated > 0:
        ranges = [
            (lower, upper, liquidity * total_liquidity // total_allocated)
            for lower, upper, liquidity in ranges
        ]
    
    return ranges

def calculate_concentration_factor(volatility: int, regime: int) -> int:
    """
    Calculate dynamic concentration factor based on volatility.
    
    Low volatility: Concentrate liquidity tightly (factor < 1.0)
    High volatility: Spread liquidity widely (factor > 1.0)
    """
    base_factors = [5000, 10000, 20000]  # 0.5x, 1.0x, 2.0x for low/med/high
    base_factor = base_factors[regime]
    
    # Fine-tune based on specific volatility level
    if regime == 0:  # Low volatility regime
        # Even tighter concentration for very low volatility
        if volatility < 100:  # < 1%
            return base_factor // 2  # 0.25x
        else:
            return base_factor
    elif regime == 1:  # Medium volatility regime
        # Gradual adjustment within medium range
        volatility_adjustment = (volatility - 200) * 2500 // 600  # Scale 200-800bp to 0-2500
        return base_factor + volatility_adjustment
    else:  # High volatility regime
        # Wider spread for extreme volatility
        if volatility > 1500:  # > 15%
            return base_factor * 2  # 4.0x
        else:
            return base_factor
```

### Efficiency Calculation

```python
def calculate_efficiency_score(
    ranges: list[tuple[int, int, int]],
    current_price: int,
    volatility: int,
    trading_volume_distribution: list[int] = None
) -> int:
    """
    Calculate capital efficiency score for range configuration.
    
    Factors considered:
    1. Liquidity concentration around current price
    2. Coverage of likely price movements (based on volatility)
    3. Fragmentation penalty for too many small ranges
    4. Historical trading pattern alignment
    """
    
    if not ranges:
        return 0
    
    total_liquidity = sum(r[2] for r in ranges)
    if total_liquidity == 0:
        return 0
    
    # 1. Concentration score (higher for liquidity near current price)
    concentration_score = 0
    for lower, upper, liquidity in ranges:
        range_center = (lower + upper) // 2
        distance_from_current = abs(range_center - current_price)
        max_reasonable_distance = current_price * volatility // 5000  # 2σ movement
        
        if distance_from_current <= max_reasonable_distance:
            # Liquidity within reasonable range gets full score
            proximity_score = 10000 - (distance_from_current * 5000 // max_reasonable_distance)
        else:
            # Liquidity far from current price gets reduced score
            proximity_score = 5000 // (1 + distance_from_current // max_reasonable_distance)
        
        weighted_score = (proximity_score * liquidity) // total_liquidity
        concentration_score += weighted_score
    
    # 2. Coverage score (penalty for gaps in coverage)
    sorted_ranges = sorted(ranges, key=lambda x: x[0])
    coverage_score = 10000
    
    for i in range(len(sorted_ranges) - 1):
        gap = sorted_ranges[i+1][0] - sorted_ranges[i][1]
        if gap > 0:
            gap_penalty = min(gap * 100 // current_price, 2000)  # Max 20% penalty per gap
            coverage_score -= gap_penalty
    
    # 3. Fragmentation penalty (too many small ranges is inefficient)
    fragmentation_score = 10000
    if len(ranges) > 5:
        fragmentation_penalty = (len(ranges) - 5) * 500  # 5% penalty per extra range
        fragmentation_score -= fragmentation_penalty
    
    # Small ranges penalty
    min_useful_liquidity = total_liquidity // 20  # 5% minimum per range
    for _, _, liquidity in ranges:
        if liquidity < min_useful_liquidity:
            fragmentation_score -= 500  # 5% penalty for tiny ranges
    
    # 4. Volatility alignment score
    volatility_score = 10000
    price_span_needed = current_price * volatility // 2500  # 4σ movement coverage
    
    actual_span = max(r[1] for r in ranges) - min(r[0] for r in ranges)
    if actual_span < price_span_needed:
        # Insufficient coverage for volatility level
        coverage_ratio = actual_span * 10000 // price_span_needed
        volatility_score = coverage_ratio
    elif actual_span > 2 * price_span_needed:
        # Excessive coverage wastes capital
        excess_ratio = actual_span * 10000 // (2 * price_span_needed)
        volatility_score = 20000 - excess_ratio  # Penalty for over-coverage
    
    # Combine scores with weights
    final_score = (
        concentration_score * 40 +      # 40% weight on concentration
        coverage_score * 25 +           # 25% weight on coverage
        fragmentation_score * 20 +      # 20% weight on fragmentation
        volatility_score * 15           # 15% weight on volatility alignment
    ) // 100
    
    return max(0, min(final_score, 10000))
```

### Rebalancing Safety Validation

```python
def validate_rebalancing_safety(
    old_ranges: list[tuple[int, int, int]],
    new_ranges: list[tuple[int, int, int]],
    current_price: int,
    max_slippage: int
) -> tuple[bool, str]:
    """
    Validate that rebalancing operation is safe to execute.
    
    Safety checks:
    1. Total liquidity conservation
    2. Price impact within acceptable bounds
    3. No range overlaps or gaps larger than threshold
    4. Minimum liquidity per range requirement
    """
    
    # 1. Liquidity conservation check
    old_total = sum(r[2] for r in old_ranges)
    new_total = sum(r[2] for r in new_ranges)
    
    liquidity_diff = abs(old_total - new_total)
    if liquidity_diff > old_total // 1000:  # Allow 0.1% rounding error
        return False, "Total liquidity not conserved"
    
    # 2. Price impact check
    # Estimate price impact of moving liquidity between ranges
    estimated_slippage = estimate_rebalancing_slippage(old_ranges, new_ranges, current_price)
    if estimated_slippage > max_slippage:
        return False, f"Estimated slippage {estimated_slippage} exceeds limit {max_slippage}"
    
    # 3. Range validity checks
    sorted_new_ranges = sorted(new_ranges, key=lambda x: x[0])
    
    for i, (lower, upper, liquidity) in enumerate(sorted_new_ranges):
        # Check range validity
        if lower >= upper:
            return False, f"Invalid range {i}: lower >= upper"
        
        if liquidity <= 0:
            return False, f"Invalid range {i}: non-positive liquidity"
        
        # Check for overlaps
        if i > 0:
            prev_upper = sorted_new_ranges[i-1][1]
            if lower < prev_upper:
                return False, f"Range overlap between ranges {i-1} and {i}"
    
    # 4. Coverage check - ensure reasonable price coverage
    total_span = sorted_new_ranges[-1][1] - sorted_new_ranges[0][0]
    min_required_span = current_price // 10  # Minimum 10% price coverage
    
    if total_span < min_required_span:
        return False, "Insufficient price range coverage"
    
    return True, "Validation passed"

def estimate_rebalancing_slippage(
    old_ranges: list[tuple[int, int, int]],
    new_ranges: list[tuple[int, int, int]],
    current_price: int
) -> int:
    """
    Estimate price slippage from rebalancing operation.
    
    Simplified model: price impact proportional to liquidity movement
    distance from current price.
    """
    total_impact = 0
    
    # Calculate impact of removing old liquidity
    for lower, upper, liquidity in old_ranges:
        range_center = (lower + upper) // 2
        distance_factor = abs(range_center - current_price) * 10000 // current_price
        removal_impact = (liquidity * distance_factor) // 1000000  # Scaled impact
        total_impact += removal_impact
    
    # Calculate impact of adding new liquidity (opposite direction)
    for lower, upper, liquidity in new_ranges:
        range_center = (lower + upper) // 2
        distance_factor = abs(range_center - current_price) * 10000 // current_price
        addition_impact = (liquidity * distance_factor) // 1000000  # Scaled impact
        total_impact -= addition_impact  # Subtracts because adding liquidity reduces slippage
    
    return abs(total_impact)
```

## Events

```python
class RebalanceCalculatedEvent:
    """Emitted when new optimal ranges are calculated."""
    trigger_volatility: int
    old_efficiency_score: int
    new_efficiency_score: int
    proposed_ranges: list[tuple[int, int, int]]
    timestamp: int

class RebalanceExecutedEvent:
    """Emitted when rebalancing is successfully executed."""
    old_ranges: list[tuple[int, int, int]]
    new_ranges: list[tuple[int, int, int]]
    liquidity_moved: int
    efficiency_gain: int
    gas_used: int
    timestamp: int

class RebalanceFailedEvent:
    """Emitted when rebalancing execution fails."""
    reason: str
    attempted_ranges: list[tuple[int, int, int]]
    error_code: int
    timestamp: int
```

## Configuration Constants

```python
# Default Concentration Factors (fixed point, 10000 = 1.0x)
DEFAULT_CONCENTRATION_FACTORS = [5000, 10000, 20000]  # 0.5x, 1.0x, 2.0x

# Default Range Counts
DEFAULT_RANGE_COUNTS = [3, 4, 5]  # Low, medium, high volatility

# Safety Parameters
DEFAULT_MIN_RANGE_SIZE = 50        # 0.5% minimum range size
DEFAULT_MAX_CONCENTRATION = 50000   # 5.0x maximum concentration
DEFAULT_MAX_SLIPPAGE = 100         # 1% maximum slippage
DEFAULT_COOLDOWN = 300             # 5 minutes between rebalances
DEFAULT_MIN_LIQUIDITY = 1000       # Minimum liquidity per range

# Efficiency Thresholds
MIN_EFFICIENCY_GAIN = 100          # 1% minimum efficiency gain to rebalance
EXCELLENT_EFFICIENCY = 8000        # 80%+ efficiency considered excellent
POOR_EFFICIENCY = 3000             # <30% efficiency triggers immediate rebalance
```

## Error Codes

```python
class RebalancingEngineErrors:
    UNAUTHORIZED_CALLER = 3001
    INVALID_VOLATILITY_REGIME = 3002
    INSUFFICIENT_LIQUIDITY = 3003
    INVALID_RANGE_SPECIFICATION = 3004
    LIQUIDITY_NOT_CONSERVED = 3005
    SLIPPAGE_TOO_HIGH = 3006
    REBALANCE_TOO_FREQUENT = 3007
    INVALID_CONFIGURATION = 3008
    EXECUTION_FAILED = 3009
    SAFETY_CHECK_FAILED = 3010
```

---

This specification defines the complete rebalancing logic for the Seltra AMM, providing intelligent liquidity management that adapts to market conditions while maintaining safety and capital efficiency.
