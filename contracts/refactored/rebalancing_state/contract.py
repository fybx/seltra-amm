"""
RebalancingState - Minimal Rebalancing State Contract
Refactored version focusing on state management only

This is a stripped-down version that:
- Removes complex decision tree logic
- Keeps only essential rebalancing state
- Targets <500 TEAL lines for deployment
- Relies on off-chain backend for complex calculations
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
DEFAULT_COOLDOWN = 300  # 5 minutes between rebalances (seconds)


class RebalancingState(ARC4Contract):
    """
    Minimal Rebalancing State Contract - Deployable Version
    
    Features:
    - Basic rebalancing state management
    - Simple cooldown enforcement
    - Integration with off-chain backend for complex logic
    - Minimal state variables for deployment
    """
    
    def __init__(self) -> None:
        # Configuration Parameters (8 variables - minimal state)
        self.is_initialized = False
        self.admin_address = Global.creator_address
        self.authorized_pool = UInt64(0)  # Pool contract app ID
        
        # Safety Parameters
        self.rebalance_cooldown = UInt64(DEFAULT_COOLDOWN)
        
        # Rebalancing History
        self.last_rebalance_time = UInt64(0)
        self.total_rebalances = UInt64(0)
        self.successful_rebalances = UInt64(0)
        
        # Current ranges (stored as simple string)
        self.current_ranges = arc4.String("")

    @abimethod()
    def initialize_engine(
        self,
        authorized_pool_id: UInt64,
        cooldown_seconds: UInt64,
    ) -> arc4.String:
        """
        Initialize the rebalancing engine with basic configuration
        
        Args:
            authorized_pool_id: Pool contract app ID that can call rebalancing
            cooldown_seconds: Minimum time between rebalances (seconds)
        """
        assert not self.is_initialized, "Engine already initialized"
        assert authorized_pool_id > UInt64(0), "Invalid pool ID"
        assert cooldown_seconds > UInt64(0), "Invalid cooldown period"
        
        self.authorized_pool = authorized_pool_id
        self.rebalance_cooldown = cooldown_seconds
        self.is_initialized = True
        
        return arc4.String("RebalancingEngine initialized successfully")

    @abimethod()
    def should_rebalance(
        self,
        time_since_last: UInt64,
    ) -> arc4.Bool:
        """
        Simple rebalancing trigger (backend handles complex logic)
        
        Args:
            time_since_last: Time since last rebalance (seconds)
            
        Returns:
            True if rebalancing is recommended
        """
        assert self.is_initialized, "Engine not initialized"
        
        # Simple cooldown check (backend handles efficiency and volatility logic)
        return arc4.Bool(time_since_last >= self.rebalance_cooldown)

    @abimethod()
    def update_ranges_from_backend(
        self,
        new_ranges_json: arc4.String
    ) -> arc4.String:
        """
        Update ranges from off-chain backend calculation
        
        Args:
            new_ranges_json: New ranges in JSON format from backend
        """
        assert self.is_initialized, "Engine not initialized"
        
        # Simple validation - just check it's not empty
        assert len(new_ranges_json.native) > 0, "Empty ranges not allowed"
        
        # Update current ranges
        self.current_ranges = new_ranges_json
        
        return arc4.String("Ranges updated from backend")

    @abimethod()
    def execute_rebalance(
        self,
        pool_address: Bytes,
        old_ranges_json: arc4.String,
        new_ranges_json: arc4.String
    ) -> arc4.String:
        """
        Execute rebalancing operation (simplified version)
        
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
        
        # Simple validation - just check ranges are not empty
        if len(new_ranges_json.native) == 0:
            return arc4.String("EXECUTION_FAILED: Empty new ranges")
        
        # Update ranges and tracking
        self.current_ranges = new_ranges_json
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
            f"Cooldown: {self.rebalance_cooldown}s"
        )
        
        return arc4.String(status)

    @abimethod()
    def get_rebalancing_params(self) -> arc4.String:
        """Get current rebalancing parameters"""
        if not self.is_initialized:
            return arc4.String("Engine not initialized")
        
        params = (
            f"Cooldown: {self.rebalance_cooldown}s, "
            f"Authorized Pool: {self.authorized_pool}"
        )
        
        return arc4.String(params)

    @abimethod()
    def get_current_ranges(self) -> arc4.String:
        """Get current ranges configuration"""
        assert self.is_initialized, "Engine not initialized"
        return self.current_ranges

    @abimethod()
    def get_last_rebalance_time(self) -> UInt64:
        """Get last rebalance timestamp"""
        assert self.is_initialized, "Engine not initialized"
        return self.last_rebalance_time

    @abimethod()
    def get_total_rebalances(self) -> UInt64:
        """Get total number of rebalances"""
        assert self.is_initialized, "Engine not initialized"
        return self.total_rebalances

    @abimethod()
    def get_successful_rebalances(self) -> UInt64:
        """Get number of successful rebalances"""
        assert self.is_initialized, "Engine not initialized"
        return self.successful_rebalances

    @abimethod()
    def get_authorized_pool(self) -> UInt64:
        """Get authorized pool contract ID"""
        assert self.is_initialized, "Engine not initialized"
        return self.authorized_pool

    @abimethod()
    def get_cooldown_seconds(self) -> UInt64:
        """Get rebalancing cooldown period"""
        assert self.is_initialized, "Engine not initialized"
        return self.rebalance_cooldown
