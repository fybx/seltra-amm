"""
VolatilityOracleState - Minimal Oracle State Contract
Refactored version focusing on state management only

This is a stripped-down version that:
- Removes complex EWMA calculations
- Keeps only essential oracle state
- Targets <500 TEAL lines for deployment
- Relies on off-chain backend for volatility calculations
"""

from algopy import (
    ARC4Contract,
    Global,
    UInt64,
    Bytes,
    arc4,
    subroutine,
)
from algopy.arc4 import abimethod


# Constants
FIXED_POINT_SCALE = 1_000_000_000_000_000_000  # 1e18 for price calculations
VOLATILITY_SCALE = 1_000_000  # 1e6 for volatility (percentage with 4 decimals)


class VolatilityOracleState(ARC4Contract):
    """
    Minimal Volatility Oracle State Contract - Deployable Version
    
    Features:
    - Basic price and volatility state management
    - Simple regime classification storage
    - Integration with off-chain backend for calculations
    - Minimal state variables for deployment
    """
    
    def __init__(self) -> None:
        # Oracle State (6 variables - minimal state)
        self.current_price = UInt64(0)
        self.current_volatility = UInt64(0)  # Scaled by VOLATILITY_SCALE
        self.current_regime = arc4.String("medium")  # "low", "medium", "high"
        self.last_update_time = UInt64(0)
        self.last_rebalance_time = UInt64(0)
        self.is_initialized = False

    @abimethod()
    def initialize_oracle(
        self,
        initial_price: UInt64,
    ) -> arc4.String:
        """
        Initialize the volatility oracle state
        
        Args:
            initial_price: Starting price (fixed point)
        """
        assert not self.is_initialized, "Oracle already initialized"
        assert initial_price > UInt64(0), "Price must be positive"
        
        # Set initial state
        self.current_price = initial_price
        self.last_update_time = Global.latest_timestamp
        
        # Initialize with default values (will be updated by backend)
        self.current_volatility = UInt64(30_000)  # 3% default volatility
        self.current_regime = arc4.String("medium")
        
        self.is_initialized = True
        
        return arc4.String("Volatility Oracle initialized successfully")

    @abimethod()
    def update_price(self, new_price: UInt64) -> arc4.String:
        """
        Update oracle with new price (backend will calculate volatility)
        
        Args:
            new_price: New price observation (fixed point)
        """
        assert self.is_initialized, "Oracle not initialized"
        assert new_price > UInt64(0), "Price must be positive"
        
        # Update price and timestamp
        self.current_price = new_price
        self.last_update_time = Global.latest_timestamp
        
        return arc4.String("Price updated successfully")

    @abimethod()
    def update_volatility_from_backend(
        self,
        new_volatility: UInt64,
        new_regime: arc4.String
    ) -> arc4.String:
        """
        Update volatility and regime from off-chain backend calculation
        
        Args:
            new_volatility: New volatility value (scaled by VOLATILITY_SCALE)
            new_regime: New volatility regime ("low", "medium", "high")
        """
        assert self.is_initialized, "Oracle not initialized"
        assert new_volatility >= UInt64(0), "Volatility must be non-negative"
        
        # Validate regime
        valid_regimes = ["low", "medium", "high"]
        assert new_regime.native in valid_regimes, "Invalid regime"
        
        # Update volatility state
        self.current_volatility = new_volatility
        self.current_regime = new_regime
        
        return arc4.String("Volatility updated from backend")

    @abimethod()
    def should_rebalance(self) -> arc4.Bool:
        """
        Simple rebalancing trigger (backend handles complex logic)
        
        Returns:
            True if rebalancing is recommended
        """
        assert self.is_initialized, "Oracle not initialized"
        
        # Simple time-based check (backend handles volatility-based logic)
        time_since_rebalance = Global.latest_timestamp - self.last_rebalance_time
        
        # Rebalance every 5 minutes (300 seconds) for demo
        return arc4.Bool(time_since_rebalance >= UInt64(300))

    @abimethod()
    def mark_rebalance_completed(self) -> arc4.String:
        """Mark that rebalancing has been completed"""
        assert self.is_initialized, "Oracle not initialized"
        
        self.last_rebalance_time = Global.latest_timestamp
        
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
    def get_current_price(self) -> UInt64:
        """Get current price"""
        assert self.is_initialized, "Oracle not initialized"
        return self.current_price

    @abimethod()
    def get_last_update_time(self) -> UInt64:
        """Get last update timestamp"""
        assert self.is_initialized, "Oracle not initialized"
        return self.last_update_time

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
