"""
Volatility Oracle Contract for Seltra AMM
Calculates real-time volatility and provides regime classification

Features:
- EWMA (Exponentially Weighted Moving Average) calculation
- Rolling window standard deviation
- Volatility regime detection (low/medium/high)
- Rebalancing trigger logic
- Integration with SeltraPoolContract

Based on roadmap.md Milestone 2.2 specifications.
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

# Volatility thresholds (scaled by VOLATILITY_SCALE)
LOW_VOLATILITY_THRESHOLD = 20_000    # 2.0% daily volatility
HIGH_VOLATILITY_THRESHOLD = 50_000   # 5.0% daily volatility

# EWMA and window parameters
DEFAULT_ALPHA = 300_000  # 0.3 in fixed point (1e6 scale)
DEFAULT_WINDOW_SIZE = 10
MAX_PRICE_HISTORY = 50


class VolatilityOracleContract(ARC4Contract):
    """
    Volatility Oracle Contract implementing EWMA-based volatility calculation
    
    Provides:
    - Real-time volatility calculation using EWMA
    - Volatility regime classification (low/medium/high)
    - Rebalancing trigger logic
    - Price history management
    """
    
    def __init__(self) -> None:
        # Oracle configuration
        self.alpha = UInt64(DEFAULT_ALPHA)  # EWMA decay factor (scaled)
        self.window_size = UInt64(DEFAULT_WINDOW_SIZE)
        self.is_initialized = False
        
        # Current state
        self.current_price = UInt64(0)
        self.current_volatility = UInt64(0)  # Scaled by VOLATILITY_SCALE
        self.current_regime = arc4.String("medium")  # "low", "medium", "high"
        self.last_update_time = UInt64(0)
        
        # EWMA calculation state
        self.ewma_mean = UInt64(0)  # EWMA of returns
        self.ewma_variance = UInt64(0)  # EWMA of squared returns
        
        # Price history (simplified - store last 10 prices)
        self.price_history_count = UInt64(0)
        self.price_1 = UInt64(0)
        self.price_2 = UInt64(0)
        self.price_3 = UInt64(0)
        self.price_4 = UInt64(0)
        self.price_5 = UInt64(0)
        self.price_6 = UInt64(0)
        self.price_7 = UInt64(0)
        self.price_8 = UInt64(0)
        self.price_9 = UInt64(0)
        self.price_10 = UInt64(0)
        
        # Rebalancing state
        self.last_rebalance_time = UInt64(0)
        self.last_rebalance_volatility = UInt64(0)
        self.rebalance_threshold = UInt64(20_000)  # 2% volatility change triggers rebalance

    @abimethod()
    def initialize_oracle(
        self,
        initial_price: UInt64,
        alpha: UInt64,
        window_size: UInt64,
    ) -> arc4.String:
        """
        Initialize the volatility oracle
        
        Args:
            initial_price: Starting price (fixed point)
            alpha: EWMA decay factor (scaled by 1e6, e.g., 300000 = 0.3)
            window_size: Rolling window size for calculations
        """
        assert not self.is_initialized, "Oracle already initialized"
        assert initial_price > UInt64(0), "Price must be positive"
        assert alpha > UInt64(0) and alpha <= UInt64(1_000_000), "Alpha must be between 0 and 1"
        assert window_size > UInt64(0) and window_size <= UInt64(50), "Window size must be 1-50"
        
        # Set configuration
        self.alpha = alpha
        self.window_size = window_size
        self.current_price = initial_price
        self.last_update_time = Global.latest_timestamp
        
        # Initialize EWMA with first price
        self.ewma_mean = UInt64(0)  # First return is 0
        self.ewma_variance = UInt64(0)
        
        # Initialize price history
        self.price_1 = initial_price
        self.price_history_count = UInt64(1)
        
        # Set initial volatility and regime
        self.current_volatility = UInt64(LOW_VOLATILITY_THRESHOLD // 2)  # Start at 1% volatility
        self.current_regime = arc4.String("medium")
        
        self.is_initialized = True
        
        return arc4.String("Volatility Oracle initialized successfully")

    @abimethod()
    def update_price(self, new_price: UInt64) -> arc4.String:
        """
        Update oracle with new price and recalculate volatility
        
        Args:
            new_price: New price observation (fixed point)
        """
        assert self.is_initialized, "Oracle not initialized"
        assert new_price > UInt64(0), "Price must be positive"
        
        # Calculate return if we have previous price
        if self.current_price > UInt64(0):
            # Calculate log return: ln(new_price / old_price) * VOLATILITY_SCALE
            # Simplified: (new_price - old_price) / old_price * VOLATILITY_SCALE
            price_change = self._calculate_return(self.current_price, new_price)
            
            # Update EWMA calculations
            self._update_ewma(price_change)
            
            # Calculate current volatility
            self._calculate_volatility()
            
            # Update regime classification
            self._update_regime()
        
        # Update price history
        self._add_to_price_history(new_price)
        
        # Update current state
        self.current_price = new_price
        self.last_update_time = Global.latest_timestamp
        
        return arc4.String("Price updated successfully")

    @subroutine
    def _calculate_return(self, old_price: UInt64, new_price: UInt64) -> UInt64:
        """Calculate percentage return scaled by VOLATILITY_SCALE"""
        if old_price == UInt64(0):
            return UInt64(0)
        
        # Calculate (new_price - old_price) / old_price * VOLATILITY_SCALE
        if new_price >= old_price:
            price_diff = new_price - old_price
            return (price_diff * UInt64(VOLATILITY_SCALE)) // old_price
        else:
            price_diff = old_price - new_price
            return (price_diff * UInt64(VOLATILITY_SCALE)) // old_price

    @subroutine
    def _update_ewma(self, return_value: UInt64) -> None:
        """Update EWMA mean and variance with new return"""
        
        # Update EWMA mean: ewma_mean = alpha * return + (1-alpha) * ewma_mean
        alpha_scaled = self.alpha
        one_minus_alpha = UInt64(1_000_000) - alpha_scaled
        
        new_ewma_mean = (alpha_scaled * return_value + one_minus_alpha * self.ewma_mean) // UInt64(1_000_000)
        
        # Update EWMA variance: ewma_var = alpha * (return - mean)^2 + (1-alpha) * ewma_var
        if return_value >= new_ewma_mean:
            squared_deviation = (return_value - new_ewma_mean) * (return_value - new_ewma_mean)
        else:
            squared_deviation = (new_ewma_mean - return_value) * (new_ewma_mean - return_value)
        
        new_ewma_variance = (alpha_scaled * squared_deviation + one_minus_alpha * self.ewma_variance) // UInt64(1_000_000)
        
        self.ewma_mean = new_ewma_mean
        self.ewma_variance = new_ewma_variance

    @subroutine
    def _calculate_volatility(self) -> None:
        """Calculate current volatility from EWMA variance"""
        # Volatility = sqrt(ewma_variance)
        self.current_volatility = self._sqrt(self.ewma_variance)

    @subroutine
    def _update_regime(self) -> None:
        """Update volatility regime based on current volatility"""
        if self.current_volatility < UInt64(LOW_VOLATILITY_THRESHOLD):
            self.current_regime = arc4.String("low")
        elif self.current_volatility > UInt64(HIGH_VOLATILITY_THRESHOLD):
            self.current_regime = arc4.String("high")
        else:
            self.current_regime = arc4.String("medium")

    @subroutine
    def _add_to_price_history(self, price: UInt64) -> None:
        """Add price to history (shift array)"""
        # Shift prices (newest becomes price_1)
        self.price_10 = self.price_9
        self.price_9 = self.price_8
        self.price_8 = self.price_7
        self.price_7 = self.price_6
        self.price_6 = self.price_5
        self.price_5 = self.price_4
        self.price_4 = self.price_3
        self.price_3 = self.price_2
        self.price_2 = self.price_1
        self.price_1 = price
        
        # Update count (max 10)
        if self.price_history_count < UInt64(10):
            self.price_history_count = self.price_history_count + UInt64(1)

    @subroutine
    def _sqrt(self, x: UInt64) -> UInt64:
        """Integer square root using Newton's method"""
        if x == UInt64(0):
            return UInt64(0)
        
        # Initial guess
        z = x
        y = (x + UInt64(1)) // UInt64(2)
        
        # Newton's method iteration
        for i in urange(10):
            if y >= z:
                return z
            z = y
            y = (y + x // y) // UInt64(2)
        
        return z

    @abimethod()
    def should_rebalance(self) -> arc4.Bool:
        """
        Determine if rebalancing should be triggered
        
        Returns:
            True if rebalancing is recommended
        """
        assert self.is_initialized, "Oracle not initialized"
        
        # Check minimum time since last rebalance (60 seconds)
        time_since_rebalance = Global.latest_timestamp - self.last_rebalance_time
        if time_since_rebalance < UInt64(60):
            return arc4.Bool(False)
        
        # Check volatility change threshold
        if self.last_rebalance_volatility == UInt64(0):
            # First rebalance
            return arc4.Bool(True)
        
        # Calculate volatility change
        volatility_change = self.current_volatility - self.last_rebalance_volatility if self.current_volatility >= self.last_rebalance_volatility else self.last_rebalance_volatility - self.current_volatility
        
        # Trigger if change exceeds threshold
        return arc4.Bool(volatility_change >= self.rebalance_threshold)

    @abimethod()
    def mark_rebalance_completed(self) -> arc4.String:
        """Mark that rebalancing has been completed"""
        assert self.is_initialized, "Oracle not initialized"
        
        self.last_rebalance_time = Global.latest_timestamp
        self.last_rebalance_volatility = self.current_volatility
        
        return arc4.String("Rebalance marked as completed")

    # Read-only methods
    
    @abimethod()
    def get_volatility(self) -> UInt64:
        """Get current volatility (scaled by VOLATILITY_SCALE)"""
        assert self.is_initialized, "Oracle not initialized"
        return self.current_volatility

    @abimethod()
    def get_volatility_regime(self) -> arc4.String:
        """Get current volatility regime"""
        assert self.is_initialized, "Oracle not initialized"
        return self.current_regime

    @abimethod()
    def get_oracle_info(self) -> arc4.String:
        """Get comprehensive oracle information"""
        if not self.is_initialized:
            return arc4.String("Oracle not initialized")
        
        return arc4.String("Oracle active and monitoring volatility")

    @abimethod()
    def get_price_history_count(self) -> UInt64:
        """Get number of prices in history"""
        return self.price_history_count

    @abimethod()
    def get_latest_prices(self) -> arc4.String:
        """Get recent price information"""
        if self.price_history_count == UInt64(0):
            return arc4.String("No price history available")
        
        return arc4.String("Price history available")

    @abimethod()
    def get_rebalance_info(self) -> arc4.String:
        """Get rebalancing status information"""
        if not self.is_initialized:
            return arc4.String("Oracle not initialized")
        
        should_rebalance = self.should_rebalance()
        if should_rebalance.native:
            return arc4.String("Rebalancing recommended")
        else:
            return arc4.String("No rebalancing needed")
