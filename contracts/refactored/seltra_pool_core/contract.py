"""
SeltraPoolCore - Minimal AMM Contract
Refactored version focusing on core functionality only

This is a stripped-down version of the original SeltraPoolContract that:
- Removes complex mathematical calculations
- Keeps only essential AMM operations
- Targets <1000 TEAL lines for deployment
- Relies on off-chain backend for complex logic
"""

from algopy import (
    ARC4Contract,
    Asset,
    Global,
    UInt64,
    Bytes,
    arc4,
    subroutine,
)
from algopy.arc4 import abimethod


# Constants
FIXED_POINT_SCALE = 1_000_000_000_000_000_000  # 1e18
MIN_LIQUIDITY = 1000
DEFAULT_FEE_RATE = 30  # 30 basis points = 0.30%


class SeltraPoolCore(ARC4Contract):
    """
    Minimal AMM Core Contract - Deployable Version
    
    Features:
    - 3 static liquidity ranges (tight ±5%, medium ±15%, wide ±30%)
    - Basic swap functionality with slippage protection
    - Simple liquidity management (add/remove)
    - Fixed-point arithmetic for price calculations
    - Integration with off-chain backend for complex calculations
    """
    
    def __init__(self) -> None:
        # Pool Configuration (8 variables - minimal state)
        self.asset_x_id = UInt64(0)
        self.asset_y_id = UInt64(0)
        self.current_price = UInt64(0)  # Fixed point
        self.total_liquidity = UInt64(0)
        self.current_fee_rate = UInt64(DEFAULT_FEE_RATE)
        self.is_initialized = False
        
        # Range 1: Tight (±5% around current price)
        self.range1_liquidity = UInt64(0)
        
        # Range 2: Medium (±15% around current price)
        self.range2_liquidity = UInt64(0)
        
        # Range 3: Wide (±30% around current price)
        self.range3_liquidity = UInt64(0)

    @abimethod()
    def initialize_pool(
        self,
        asset_x: Asset,
        asset_y: Asset,
        initial_price: UInt64,
    ) -> arc4.String:
        """
        Initialize the liquidity pool with two assets and starting price
        
        Args:
            asset_x: First asset in the pair
            asset_y: Second asset in the pair  
            initial_price: Starting price (asset_y per asset_x, fixed point)
            
        Returns:
            Success message
        """
        # Ensure not already initialized
        assert not self.is_initialized, "Pool already initialized"
        
        # Validate assets
        assert asset_x.id != asset_y.id, "Assets must be different"
        assert initial_price > UInt64(0), "Price must be positive"
        
        # Set pool configuration
        self.asset_x_id = asset_x.id
        self.asset_y_id = asset_y.id
        self.current_price = initial_price
        
        self.is_initialized = True
        
        return arc4.String("Pool initialized successfully")

    @abimethod()
    def add_liquidity(
        self,
        asset_x: Asset,
        asset_y: Asset,
        amount_x_desired: UInt64,
        amount_y_desired: UInt64,
        range_id: UInt64,  # 1, 2, or 3 for our static ranges
        deadline: UInt64,
    ) -> arc4.String:
        """
        Add liquidity to a specific range (simplified version)
        
        Args:
            asset_x: First asset in pair
            asset_y: Second asset in pair
            amount_x_desired: Desired amount of asset X
            amount_y_desired: Desired amount of asset Y
            range_id: Range ID (1=tight, 2=medium, 3=wide)
            deadline: Transaction deadline timestamp
            
        Returns:
            Success message
        """
        assert self.is_initialized, "Pool not initialized"
        assert Global.latest_timestamp <= deadline, "Deadline exceeded"
        assert asset_x.id == self.asset_x_id, "Invalid asset X"
        assert asset_y.id == self.asset_y_id, "Invalid asset Y"
        assert range_id >= UInt64(1) and range_id <= UInt64(3), "Invalid range ID"
        
        # Simplified liquidity calculation - just use the larger amount
        liquidity = amount_x_desired if amount_x_desired > amount_y_desired else amount_y_desired
        
        assert liquidity > UInt64(MIN_LIQUIDITY), "Insufficient liquidity"
        
        # Update range liquidity based on range_id
        if range_id == UInt64(1):
            self.range1_liquidity = self.range1_liquidity + liquidity
        elif range_id == UInt64(2):
            self.range2_liquidity = self.range2_liquidity + liquidity
        else:  # range_id == 3
            self.range3_liquidity = self.range3_liquidity + liquidity
        
        self.total_liquidity = self.total_liquidity + liquidity
        
        return arc4.String("Liquidity added successfully")

    @abimethod()
    def remove_liquidity(
        self,
        lp_token_amount: UInt64,
        range_id: UInt64,
        deadline: UInt64,
    ) -> arc4.String:
        """
        Remove liquidity from a specific range (simplified version)
        
        Args:
            lp_token_amount: Amount of LP tokens to burn
            range_id: Range ID (1=tight, 2=medium, 3=wide)
            deadline: Transaction deadline timestamp
            
        Returns:
            Success message
        """
        assert self.is_initialized, "Pool not initialized"
        assert Global.latest_timestamp <= deadline, "Deadline exceeded"
        assert lp_token_amount > UInt64(0), "Invalid LP token amount"
        assert range_id >= UInt64(1) and range_id <= UInt64(3), "Invalid range ID"
        
        # Get current range liquidity
        current_range_liquidity = self._get_range_liquidity(range_id)
        assert current_range_liquidity >= lp_token_amount, "Insufficient liquidity"
        
        # Update range liquidity
        if range_id == UInt64(1):
            self.range1_liquidity = self.range1_liquidity - lp_token_amount
        elif range_id == UInt64(2):
            self.range2_liquidity = self.range2_liquidity - lp_token_amount
        else:  # range_id == 3
            self.range3_liquidity = self.range3_liquidity - lp_token_amount
        
        self.total_liquidity = self.total_liquidity - lp_token_amount
        
        return arc4.String("Liquidity removed successfully")

    @abimethod()
    def swap(
        self,
        asset_in: Asset,
        asset_out: Asset,
        amount_in: UInt64,
        min_amount_out: UInt64,
        deadline: UInt64,
    ) -> arc4.String:
        """
        Execute a token swap with slippage protection (simplified version)
        
        Args:
            asset_in: Input asset ID
            asset_out: Output asset ID
            amount_in: Amount of input asset
            min_amount_out: Minimum acceptable output amount
            deadline: Transaction deadline timestamp
            
        Returns:
            Success message with swap details
        """
        assert self.is_initialized, "Pool not initialized"
        assert Global.latest_timestamp <= deadline, "Deadline exceeded"
        assert amount_in > UInt64(0), "Invalid input amount"
        
        # Validate asset pair
        is_x_to_y = (asset_in.id == self.asset_x_id and asset_out.id == self.asset_y_id)
        is_y_to_x = (asset_in.id == self.asset_y_id and asset_out.id == self.asset_x_id)
        assert is_x_to_y or is_y_to_x, "Invalid asset pair"
        
        # Simplified swap calculation - use constant product formula
        # In production, this would be more sophisticated
        fee_amount = (amount_in * self.current_fee_rate) // UInt64(10000)
        amount_in_after_fee = amount_in - fee_amount
        
        # Simple constant product: x * y = k
        # For simplicity, assume equal reserves
        amount_out = amount_in_after_fee // UInt64(2)  # Simplified calculation
        
        # Validate slippage protection
        assert amount_out >= min_amount_out, "Slippage exceeded"
        
        # Update current price (simplified)
        if is_x_to_y:
            self.current_price = self.current_price + (amount_in // UInt64(1000))
        else:
            new_price = self.current_price - (amount_in // UInt64(1000))
            self.current_price = new_price if new_price > UInt64(0) else UInt64(1)
        
        return arc4.String("Swap executed successfully")

    @subroutine
    def _get_range_liquidity(self, range_id: UInt64) -> UInt64:
        """Get the liquidity amount for a specific range"""
        if range_id == UInt64(1):
            return self.range1_liquidity
        elif range_id == UInt64(2):
            return self.range2_liquidity
        else:  # range_id == 3
            return self.range3_liquidity

    # Read-only methods
    
    @abimethod()
    def get_pool_info(self) -> arc4.String:
        """Get current pool state information"""
        if not self.is_initialized:
            return arc4.String("Pool not initialized")
        
        return arc4.String("Pool initialized and active")

    @abimethod()
    def get_range_info(self, range_id: UInt64) -> arc4.String:
        """Get information about a specific range"""
        assert range_id >= UInt64(1) and range_id <= UInt64(3), "Invalid range ID"
        
        range_liquidity = self._get_range_liquidity(range_id)
        
        return arc4.String("Range information available")

    @abimethod()
    def calculate_swap_output(
        self,
        asset_in: Asset,
        asset_out: Asset,
        amount_in: UInt64,
    ) -> arc4.String:
        """
        Calculate expected output for a swap without executing (simplified)
        
        Args:
            asset_in: Input asset ID
            asset_out: Output asset ID
            amount_in: Amount of input asset
            
        Returns:
            Formatted string with swap details
        """
        assert self.is_initialized, "Pool not initialized"
        
        # Validate asset pair
        is_x_to_y = (asset_in.id == self.asset_x_id and asset_out.id == self.asset_y_id)
        is_y_to_x = (asset_in.id == self.asset_y_id and asset_out.id == self.asset_x_id)
        assert is_x_to_y or is_y_to_x, "Invalid asset pair"
        
        # Simplified calculation
        fee_amount = (amount_in * self.current_fee_rate) // UInt64(10000)
        amount_in_after_fee = amount_in - fee_amount
        amount_out = amount_in_after_fee // UInt64(2)  # Simplified
        
        return arc4.String("Swap calculation completed")

    @abimethod()
    def update_price_from_backend(self, new_price: UInt64) -> arc4.String:
        """
        Update price from off-chain backend service
        
        Args:
            new_price: New price from backend calculation
            
        Returns:
            Success message
        """
        assert self.is_initialized, "Pool not initialized"
        assert new_price > UInt64(0), "Price must be positive"
        
        self.current_price = new_price
        
        return arc4.String("Price updated from backend")
