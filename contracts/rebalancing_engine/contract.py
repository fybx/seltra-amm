"""
RebalancingEngine Contract for Seltra AMM
Intelligent liquidity range adjustment based on volatility regimes

Features:
- Decision tree logic for volatility-based range concentration
- Optimal range calculation with concentration factors
- Safety validation for rebalancing operations
- Efficiency scoring for range configurations
- Integration with VolatilityOracle and SeltraPoolContract

Based on roadmap.md Milestone 2.3 specifications.
"""

from algopy import (
    ARC4Contract,
    Global,
    UInt64,
    Bytes,
    arc4,
    subroutine,
    urange,
)
from algopy.arc4 import abimethod


# Constants
FIXED_POINT_SCALE = 1_000_000_000_000_000_000  # 1e18 for price calculations
VOLATILITY_SCALE = 1_000_000  # 1e6 for volatility (percentage with 4 decimals)

# Decision Tree Thresholds (scaled by VOLATILITY_SCALE)
ULTRA_LOW_THRESHOLD = 15_000    # 1.5% volatility
LOW_THRESHOLD = 30_000          # 3.0% volatility  
MEDIUM_THRESHOLD = 60_000       # 6.0% volatility
HIGH_THRESHOLD = 120_000        # 12.0% volatility

# Concentration Factors (scaled by 10000, 10000 = 1.0x)
ULTRA_LOW_FACTOR = 4_000        # 0.4x (very tight)
LOW_FACTOR = 6_000              # 0.6x (tight)
MEDIUM_FACTOR = 10_000          # 1.0x (normal)
HIGH_FACTOR = 18_000            # 1.8x (wide)
EXTREME_FACTOR = 25_000         # 2.5x (very wide)

# Range Counts
ULTRA_LOW_RANGES = 2
LOW_RANGES = 3
MEDIUM_RANGES = 4
HIGH_RANGES = 5
EXTREME_RANGES = 6

# Safety Parameters
DEFAULT_MAX_SLIPPAGE = 100      # 1% maximum slippage (basis points)
DEFAULT_COOLDOWN = 300          # 5 minutes between rebalances (seconds)
DEFAULT_MIN_RANGE_SIZE = 50     # 0.5% minimum range size (basis points)


class RebalancingEngine(ARC4Contract):
    """
    Intelligent Rebalancing Engine for Seltra AMM
    
    Core Responsibilities:
    - Calculate optimal liquidity ranges based on volatility regimes
    - Execute atomic rebalancing operations
    - Validate rebalancing safety and efficiency
    - Track rebalancing history and performance
    """
    
    def __init__(self) -> None:
        # Configuration Parameters
        self.is_initialized = False
        self.admin_address = Global.creator_address
        self.authorized_pool = UInt64(0)  # Pool contract app ID
        
        # Safety Parameters
        self.max_slippage = UInt64(DEFAULT_MAX_SLIPPAGE)
        self.rebalance_cooldown = UInt64(DEFAULT_COOLDOWN)
        self.min_range_size = UInt64(DEFAULT_MIN_RANGE_SIZE)
        
        # Rebalancing History
        self.last_rebalance_time = UInt64(0)
        self.last_trigger_volatility = UInt64(0)
        self.total_rebalances = UInt64(0)
        self.successful_rebalances = UInt64(0)
        self.failed_rebalances = UInt64(0)
        
        # Performance Tracking
        self.total_efficiency_gain = UInt64(0)
        self.average_efficiency_gain = UInt64(0)

    @abimethod()
    def initialize_engine(
        self,
        authorized_pool_id: UInt64,
        max_slippage: UInt64,
        cooldown_seconds: UInt64,
        min_range_size: UInt64
    ) -> arc4.String:
        """
        Initialize the rebalancing engine with configuration parameters
        
        Args:
            authorized_pool_id: Pool contract app ID that can call rebalancing
            max_slippage: Maximum allowed slippage during rebalancing (basis points)
            cooldown_seconds: Minimum time between rebalances (seconds)
            min_range_size: Minimum range size (basis points)
        """
        assert not self.is_initialized, "Engine already initialized"
        assert authorized_pool_id > UInt64(0), "Invalid pool ID"
        assert max_slippage > UInt64(0) and max_slippage <= UInt64(1000), "Invalid slippage limit"
        assert cooldown_seconds > UInt64(0), "Invalid cooldown period"
        assert min_range_size > UInt64(0), "Invalid minimum range size"
        
        self.authorized_pool = authorized_pool_id
        self.max_slippage = max_slippage
        self.rebalance_cooldown = cooldown_seconds
        self.min_range_size = min_range_size
        self.is_initialized = True
        
        return arc4.String("RebalancingEngine initialized successfully")

    @abimethod()
    def calculate_optimal_ranges(
        self,
        current_price: UInt64,
        volatility: UInt64,
        total_liquidity: UInt64
    ) -> arc4.String:
        """
        Calculate optimal liquidity ranges using decision tree logic
        
        Args:
            current_price: Current market price (fixed point)
            volatility: Current volatility (scaled by VOLATILITY_SCALE)
            total_liquidity: Total liquidity to distribute
            
        Returns:
            JSON-encoded string with optimal ranges
        """
        assert self.is_initialized, "Engine not initialized"
        assert current_price > UInt64(0), "Invalid current price"
        assert volatility >= UInt64(0), "Invalid volatility"
        assert total_liquidity > UInt64(0), "Invalid total liquidity"
        
        # Determine volatility regime using decision tree
        regime, concentration_factor, num_ranges = self._classify_volatility_regime(volatility)
        
        # Calculate optimal ranges
        ranges = self._calculate_ranges_for_regime(
            current_price, concentration_factor, num_ranges, total_liquidity
        )
        
        # Format result as JSON-like string
        result = self._format_ranges_result(ranges, regime, concentration_factor)
        
        return arc4.String(result)

    @abimethod()
    def should_rebalance(
        self,
        current_efficiency: UInt64,
        time_since_last: UInt64,
        volatility_change: UInt64
    ) -> arc4.Bool:
        """
        Determine if rebalancing should be triggered
        
        Args:
            current_efficiency: Current efficiency score (0-10000)
            time_since_last: Time since last rebalance (seconds)
            volatility_change: Change in volatility since last rebalance
            
        Returns:
            True if rebalancing is recommended
        """
        assert self.is_initialized, "Engine not initialized"
        
        # Check cooldown period
        if time_since_last < self.rebalance_cooldown:
            return arc4.Bool(False)
        
        # Check efficiency threshold (rebalance if efficiency < 60%)
        if current_efficiency < UInt64(6000):
            return arc4.Bool(True)
        
        # Check volatility change threshold (rebalance if change > 2%)
        if volatility_change > UInt64(20_000):  # 2% change
            return arc4.Bool(True)
        
        # Check if it's been too long since last rebalance (1 hour)
        if time_since_last > UInt64(3600):
            return arc4.Bool(True)
        
        return arc4.Bool(False)

    @abimethod()
    def validate_rebalance_proposal(
        self,
        current_ranges_json: arc4.String,
        proposed_ranges_json: arc4.String,
        current_price: UInt64,
        volatility: UInt64
    ) -> arc4.String:
        """
        Validate a proposed rebalancing operation
        
        Args:
            current_ranges_json: Current ranges (JSON string)
            proposed_ranges_json: Proposed new ranges (JSON string)
            current_price: Current market price
            volatility: Current volatility
            
        Returns:
            Validation result with efficiency score
        """
        assert self.is_initialized, "Engine not initialized"
        
        # Parse ranges (simplified for hackathon)
        current_ranges = self._parse_ranges(current_ranges_json.native)
        proposed_ranges = self._parse_ranges(proposed_ranges_json.native)
        
        # Validate safety
        is_safe, safety_reason = self._validate_safety(current_ranges, proposed_ranges)
        
        if not is_safe:
            return arc4.String(f"UNSAFE: {safety_reason}")
        
        # Calculate efficiency improvement
        current_efficiency = self._calculate_efficiency_score(current_ranges, current_price, volatility)
        proposed_efficiency = self._calculate_efficiency_score(proposed_ranges, current_price, volatility)
        efficiency_gain = proposed_efficiency - current_efficiency
        
        # Determine if improvement is significant
        if efficiency_gain < UInt64(100):  # Less than 1% improvement
            return arc4.String(f"INSUFFICIENT_GAIN: {efficiency_gain}")
        
        return arc4.String(f"VALID: efficiency_gain={efficiency_gain}")

    @abimethod()
    def execute_rebalance(
        self,
        pool_address: Bytes,
        old_ranges_json: arc4.String,
        new_ranges_json: arc4.String
    ) -> arc4.String:
        """
        Execute atomic rebalancing operation
        
        Args:
            pool_address: Target pool contract address
            old_ranges_json: Current ranges to close
            new_ranges_json: New ranges to create
            
        Returns:
            Execution result
        """
        assert self.is_initialized, "Engine not initialized"
        assert Global.caller_app_id == self.authorized_pool, "Unauthorized caller"
        
        # Check cooldown
        current_time = Global.latest_timestamp
        if current_time - self.last_rebalance_time < self.rebalance_cooldown:
            return arc4.String("REBALANCE_COOLDOWN_ACTIVE")
        
        # Parse and validate ranges
        old_ranges = self._parse_ranges(old_ranges_json.native)
        new_ranges = self._parse_ranges(new_ranges_json.native)
        
        # Validate safety
        is_safe, reason = self._validate_safety(old_ranges, new_ranges)
        if not is_safe:
            self.failed_rebalances += UInt64(1)
            return arc4.String(f"EXECUTION_FAILED: {reason}")
        
        # Execute rebalancing (simplified for hackathon)
        # In full implementation, this would call pool contract methods
        
        # Update tracking
        self.last_rebalance_time = current_time
        self.total_rebalances += UInt64(1)
        self.successful_rebalances += UInt64(1)
        
        return arc4.String("REBALANCE_EXECUTED_SUCCESSFULLY")

    @abimethod()
    def get_engine_status(self) -> arc4.String:
        """Get comprehensive engine status"""
        if not self.is_initialized:
            return arc4.String("Engine not initialized")
        
        status = (
            f"RebalancingEngine Active. "
            f"Total: {self.total_rebalances}, "
            f"Successful: {self.successful_rebalances}, "
            f"Failed: {self.failed_rebalances}, "
            f"Avg Efficiency: {self.average_efficiency_gain}"
        )
        
        return arc4.String(status)

    @abimethod()
    def get_rebalancing_params(self) -> arc4.String:
        """Get current rebalancing parameters"""
        if not self.is_initialized:
            return arc4.String("Engine not initialized")
        
        params = (
            f"Max Slippage: {self.max_slippage}bp, "
            f"Cooldown: {self.rebalance_cooldown}s, "
            f"Min Range: {self.min_range_size}bp"
        )
        
        return arc4.String(params)

    # ==================== DECISION TREE LOGIC ====================

    @subroutine
    def _classify_volatility_regime(
        self, 
        volatility: UInt64
    ) -> tuple[arc4.String, UInt64, UInt64]:
        """
        Classify volatility regime using decision tree logic
        
        Returns:
            (regime_name, concentration_factor, num_ranges)
        """
        if volatility < UInt64(ULTRA_LOW_THRESHOLD):
            return (
                arc4.String("ultra_low"),
                UInt64(ULTRA_LOW_FACTOR),
                UInt64(ULTRA_LOW_RANGES)
            )
        elif volatility < UInt64(LOW_THRESHOLD):
            return (
                arc4.String("low"),
                UInt64(LOW_FACTOR),
                UInt64(LOW_RANGES)
            )
        elif volatility < UInt64(MEDIUM_THRESHOLD):
            return (
                arc4.String("medium"),
                UInt64(MEDIUM_FACTOR),
                UInt64(MEDIUM_RANGES)
            )
        elif volatility < UInt64(HIGH_THRESHOLD):
            return (
                arc4.String("high"),
                UInt64(HIGH_FACTOR),
                UInt64(HIGH_RANGES)
            )
        else:
            return (
                arc4.String("extreme"),
                UInt64(EXTREME_FACTOR),
                UInt64(EXTREME_RANGES)
            )

    @subroutine
    def _calculate_ranges_for_regime(
        self,
        current_price: UInt64,
        concentration_factor: UInt64,
        num_ranges: UInt64,
        total_liquidity: UInt64
    ) -> arc4.StaticArray[arc4.StaticArray[arc4.UInt64, 3], 6]:
        """
        Calculate optimal ranges for given regime
        
        Returns:
            Array of (lower, upper, liquidity) tuples
        """
        # Calculate price bounds based on concentration factor
        # Higher concentration factor = wider price bounds
        price_bound_percent = (concentration_factor * UInt64(100)) // UInt64(10000)  # Convert to percentage
        
        # Cap at 50% to prevent excessive ranges
        if price_bound_percent > UInt64(50):
            price_bound_percent = UInt64(50)
        
        # Calculate actual price bounds
        price_range = (current_price * price_bound_percent) // UInt64(100)
        min_price = current_price - price_range
        max_price = current_price + price_range
        
        # Ensure minimum bounds
        if min_price <= UInt64(0):
            min_price = current_price // UInt64(2)
        if max_price <= min_price:
            max_price = min_price + current_price // UInt64(10)
        
        # Create ranges
        ranges = arc4.StaticArray[arc4.StaticArray[arc4.UInt64, 3], 6]()
        range_size = (max_price - min_price) // num_ranges
        
        for i in urange(6):  # Maximum 6 ranges
            if i < num_ranges:
                lower = min_price + (UInt64(i) * range_size)
                upper = min_price + ((UInt64(i) + UInt64(1)) * range_size)
                
                # Calculate liquidity allocation (more near current price)
                range_center = (lower + upper) // UInt64(2)
                distance = abs(range_center - current_price)
                max_distance = (max_price - min_price) // UInt64(2)
                
                if max_distance > UInt64(0):
                    proximity_factor = (max_distance - distance) * UInt64(10000) // max_distance
                else:
                    proximity_factor = UInt64(10000)
                
                # Base allocation with proximity bias
                base_allocation = total_liquidity // num_ranges
                proximity_bonus = (base_allocation * proximity_factor) // UInt64(20000)  # Max 50% bonus
                liquidity = base_allocation + proximity_bonus
                
                ranges[i] = arc4.StaticArray[arc4.UInt64, 3]([
                    arc4.UInt64(lower),
                    arc4.UInt64(upper),
                    arc4.UInt64(liquidity)
                ])
            else:
                # Empty range
                ranges[i] = arc4.StaticArray[arc4.UInt64, 3]([
                    arc4.UInt64(0),
                    arc4.UInt64(0),
                    arc4.UInt64(0)
                ])
        
        return ranges

    # ==================== SAFETY VALIDATION ====================

    @subroutine
    def _validate_safety(
        self,
        old_ranges: arc4.StaticArray[arc4.StaticArray[arc4.UInt64, 3], 6],
        new_ranges: arc4.StaticArray[arc4.StaticArray[arc4.UInt64, 3], 6]
    ) -> tuple[arc4.Bool, arc4.String]:
        """Validate rebalancing safety"""
        
        # Check liquidity conservation
        old_total = UInt64(0)
        new_total = UInt64(0)
        
        for i in urange(6):
            if old_ranges[i][2].native > 0:
                old_total += old_ranges[i][2].native
            if new_ranges[i][2].native > 0:
                new_total += new_ranges[i][2].native
        
        # Allow 0.1% rounding error
        diff = abs(old_total - new_total)
        if diff > (old_total // UInt64(1000)):
            return arc4.Bool(False), arc4.String("Liquidity not conserved")
        
        # Check range validity
        for i in urange(6):
            if new_ranges[i][2].native > 0:  # Non-empty range
                lower = new_ranges[i][0].native
                upper = new_ranges[i][1].native
                liquidity = new_ranges[i][2].native
                
                if lower >= upper:
                    return arc4.Bool(False), arc4.String(f"Invalid range {i}: lower >= upper")
                
                if liquidity <= UInt64(0):
                    return arc4.Bool(False), arc4.String(f"Invalid range {i}: non-positive liquidity")
                
                # Check minimum range size
                range_size = ((upper - lower) * UInt64(10000)) // lower
                if range_size < self.min_range_size:
                    return arc4.Bool(False), arc4.String(f"Range {i} too small")
        
        return arc4.Bool(True), arc4.String("Validation passed")

    # ==================== EFFICIENCY CALCULATION ====================

    @subroutine
    def _calculate_efficiency_score(
        self,
        ranges: arc4.StaticArray[arc4.StaticArray[arc4.UInt64, 3], 6],
        current_price: UInt64,
        volatility: UInt64
    ) -> UInt64:
        """Calculate efficiency score for range configuration"""
        
        total_liquidity = UInt64(0)
        concentration_score = UInt64(0)
        
        # Calculate total liquidity and concentration score
        for i in urange(6):
            if ranges[i][2].native > 0:
                liquidity = ranges[i][2].native
                total_liquidity += liquidity
                
                # Calculate proximity to current price
                lower = ranges[i][0].native
                upper = ranges[i][1].native
                range_center = (lower + upper) // UInt64(2)
                
                distance = abs(range_center - current_price)
                max_reasonable_distance = (current_price * volatility) // UInt64(5000)  # 2σ movement
                
                if distance <= max_reasonable_distance:
                    proximity_score = UInt64(10000) - (distance * UInt64(5000) // max_reasonable_distance)
                else:
                    proximity_score = UInt64(5000) // (UInt64(1) + distance // max_reasonable_distance)
                
                weighted_score = (proximity_score * liquidity) // UInt64(10000)
                concentration_score += weighted_score
        
        if total_liquidity == UInt64(0):
            return UInt64(0)
        
        # Normalize concentration score
        final_score = (concentration_score * UInt64(10000)) // total_liquidity
        
        return min(final_score, UInt64(10000))

    # ==================== UTILITY METHODS ====================

    @subroutine
    def _format_ranges_result(
        self,
        ranges: arc4.StaticArray[arc4.StaticArray[arc4.UInt64, 3], 6],
        regime: arc4.String,
        concentration_factor: UInt64
    ) -> arc4.String:
        """Format ranges as JSON-like string"""
        result = f"regime={regime.native},factor={concentration_factor},ranges=["
        
        for i in urange(6):
            if ranges[i][2].native > 0:
                lower = ranges[i][0].native
                upper = ranges[i][1].native
                liquidity = ranges[i][2].native
                result += f"({lower},{upper},{liquidity})"
                if i < UInt64(5) and ranges[i + UInt64(1)][2].native > 0:
                    result += ","
        
        result += "]"
        return arc4.String(result)

    @subroutine
    def _parse_ranges(self, ranges_json: str) -> arc4.StaticArray[arc4.StaticArray[arc4.UInt64, 3], 6]:
        """Parse ranges from JSON string (simplified)"""
        # Simplified parsing for hackathon - in production would use proper JSON parsing
        ranges = arc4.StaticArray[arc4.StaticArray[arc4.UInt64, 3], 6]()
        
        # Initialize with empty ranges
        for i in urange(6):
            ranges[i] = arc4.StaticArray[arc4.UInt64, 3]([
                arc4.UInt64(0),
                arc4.UInt64(0),
                arc4.UInt64(0)
            ])
        
        return ranges
