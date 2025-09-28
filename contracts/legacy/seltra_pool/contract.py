"""
Seltra AMM Pool Contract - Basic Version
Concentrated liquidity AMM with dynamic range management for Algorand

This implementation uses proper Algorand Python syntax and provides:
- Multi-range concentrated liquidity (3 static ranges)
- Basic swap functionality
- Liquidity management (add/remove)
- Fixed-point arithmetic for precision
- ASA token support
- Slippage protection

Based on roadmap.md and seltra-pool-contract.md specifications.
"""

from algopy import (
    ARC4Contract,
    Asset,
    Global,
    UInt64,
    Bytes,
    arc4,
    subroutine,
    urange,
)
from algopy.arc4 import abimethod


# Constants (as integers, will be converted to UInt64 in methods)
FIXED_POINT_SCALE = 1_000_000_000_000_000_000  # 1e18
MIN_LIQUIDITY = 1000
DEFAULT_FEE_RATE = 30  # 30 basis points = 0.30%


class SeltraPoolContract(ARC4Contract):
    """
    Main Seltra AMM Pool Contract implementing concentrated liquidity
    
    Features:
    - 3 static liquidity ranges (tight ±5%, medium ±15%, wide ±30%)
    - Basic swap functionality with slippage protection
    - Add/remove liquidity operations
    - Fixed-point arithmetic for price calculations
    """
    
    def __init__(self) -> None:
        # Pool Configuration
        self.asset_x_id = UInt64(0)
        self.asset_y_id = UInt64(0)
        self.current_price = UInt64(0)  # Fixed point
        self.total_liquidity = UInt64(0)
        self.current_fee_rate = UInt64(DEFAULT_FEE_RATE)
        self.last_rebalance_time = UInt64(0)
        self.protocol_fees_x = UInt64(0)
        self.protocol_fees_y = UInt64(0)
        
        # Range 1: Tight (±5% around current price)
        self.range1_lower = UInt64(0)
        self.range1_upper = UInt64(0)
        self.range1_liquidity = UInt64(0)
        
        # Range 2: Medium (±15% around current price)
        self.range2_lower = UInt64(0)
        self.range2_upper = UInt64(0)
        self.range2_liquidity = UInt64(0)
        
        # Range 3: Wide (±30% around current price)
        self.range3_lower = UInt64(0)
        self.range3_upper = UInt64(0)
        self.range3_liquidity = UInt64(0)
        
        # Pool state
        self.is_initialized = False
        self.total_lp_tokens = UInt64(0)

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
        self.last_rebalance_time = Global.latest_timestamp
        
        # Initialize 3 static liquidity ranges around the initial price
        self._initialize_static_ranges(initial_price)
        
        self.is_initialized = True
        
        return arc4.String("Pool initialized successfully")

    @subroutine
    def _initialize_static_ranges(self, initial_price: UInt64) -> None:
        """Initialize 3 static liquidity ranges around the current price"""
        
        price = initial_price
        
        # Range 1: Tight range (±5% around current price)
        self.range1_lower = (price * UInt64(95)) // UInt64(100)
        self.range1_upper = (price * UInt64(105)) // UInt64(100)
        self.range1_liquidity = UInt64(0)
        
        # Range 2: Medium range (±15% around current price)  
        self.range2_lower = (price * UInt64(85)) // UInt64(100)
        self.range2_upper = (price * UInt64(115)) // UInt64(100)
        self.range2_liquidity = UInt64(0)
        
        # Range 3: Wide range (±30% around current price)
        self.range3_lower = (price * UInt64(70)) // UInt64(100)
        self.range3_upper = (price * UInt64(130)) // UInt64(100)
        self.range3_liquidity = UInt64(0)

    @abimethod()
    def add_liquidity(
        self,
        asset_x: Asset,
        asset_y: Asset,
        amount_x_desired: UInt64,
        amount_y_desired: UInt64,
        amount_x_min: UInt64,
        amount_y_min: UInt64,
        range_id: UInt64,  # 1, 2, or 3 for our static ranges
        deadline: UInt64,
    ) -> arc4.String:
        """
        Add liquidity to a specific range
        
        Args:
            asset_x: First asset in pair
            asset_y: Second asset in pair
            amount_x_desired: Desired amount of asset X
            amount_y_desired: Desired amount of asset Y
            amount_x_min: Minimum amount of asset X
            amount_y_min: Minimum amount of asset Y
            range_id: Range ID (1=tight, 2=medium, 3=wide)
            deadline: Transaction deadline timestamp
            
        Returns:
            Success message with amounts
        """
        assert self.is_initialized, "Pool not initialized"
        assert Global.latest_timestamp <= deadline, "Deadline exceeded"
        assert asset_x.id == self.asset_x_id, "Invalid asset X"
        assert asset_y.id == self.asset_y_id, "Invalid asset Y"
        assert range_id >= UInt64(1) and range_id <= UInt64(3), "Invalid range ID"
        
        # Get range bounds based on range_id
        range_lower, range_upper = self._get_range_bounds(range_id)
        
        # Calculate optimal amounts based on current price and range
        actual_x, actual_y = self._calculate_liquidity_amounts(
            amount_x_desired,
            amount_y_desired,
            range_lower,
            range_upper,
            self.current_price
        )
        
        # Validate minimum amounts
        assert actual_x >= amount_x_min, "Insufficient amount X"
        assert actual_y >= amount_y_min, "Insufficient amount Y"
        
        # Calculate liquidity tokens to mint
        liquidity = self._calculate_liquidity_for_amounts(
            actual_x,
            actual_y,
            range_lower,
            range_upper,
            self.current_price
        )
        
        assert liquidity > UInt64(MIN_LIQUIDITY), "Insufficient liquidity"
        
        # Update range liquidity based on range_id
        if range_id == UInt64(1):
            self.range1_liquidity = self.range1_liquidity + liquidity
        elif range_id == UInt64(2):
            self.range2_liquidity = self.range2_liquidity + liquidity
        else:  # range_id == 3
            self.range3_liquidity = self.range3_liquidity + liquidity
        
        self.total_liquidity = self.total_liquidity + liquidity
        self.total_lp_tokens = self.total_lp_tokens + liquidity
        
        # TODO: Transfer assets from user (will be handled by atomic transaction group)
        # TODO: Mint LP tokens to user
        
        return arc4.String("Liquidity added successfully")

    @abimethod()
    def remove_liquidity(
        self,
        lp_token_amount: UInt64,
        amount_x_min: UInt64,
        amount_y_min: UInt64,
        range_id: UInt64,
        deadline: UInt64,
    ) -> arc4.String:
        """
        Remove liquidity from a specific range
        
        Args:
            lp_token_amount: Amount of LP tokens to burn
            amount_x_min: Minimum amount of asset X to receive
            amount_y_min: Minimum amount of asset Y to receive
            range_id: Range ID (1=tight, 2=medium, 3=wide)
            deadline: Transaction deadline timestamp
            
        Returns:
            Success message with amounts
        """
        assert self.is_initialized, "Pool not initialized"
        assert Global.latest_timestamp <= deadline, "Deadline exceeded"
        assert lp_token_amount > UInt64(0), "Invalid LP token amount"
        assert range_id >= UInt64(1) and range_id <= UInt64(3), "Invalid range ID"
        
        # Get current range liquidity
        current_range_liquidity = self._get_range_liquidity(range_id)
        assert current_range_liquidity >= lp_token_amount, "Insufficient liquidity"
        
        # Get range bounds
        range_lower, range_upper = self._get_range_bounds(range_id)
        
        # Calculate amounts to return
        amount_x, amount_y = self._calculate_amounts_for_liquidity(
            lp_token_amount,
            range_lower,
            range_upper,
            self.current_price
        )
        
        # Validate minimum amounts
        assert amount_x >= amount_x_min, "Insufficient amount X"
        assert amount_y >= amount_y_min, "Insufficient amount Y"
        
        # Update range liquidity
        if range_id == UInt64(1):
            self.range1_liquidity = self.range1_liquidity - lp_token_amount
        elif range_id == UInt64(2):
            self.range2_liquidity = self.range2_liquidity - lp_token_amount
        else:  # range_id == 3
            self.range3_liquidity = self.range3_liquidity - lp_token_amount
        
        self.total_liquidity = self.total_liquidity - lp_token_amount
        self.total_lp_tokens = self.total_lp_tokens - lp_token_amount
        
        # TODO: Burn LP tokens from user
        # TODO: Transfer assets to user
        
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
        Execute a token swap with slippage protection
        
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
        
        # Calculate swap across all active ranges
        total_amount_out, total_fee_paid, new_price = self._execute_swap_across_ranges(
            amount_in, is_x_to_y
        )
        
        # Validate slippage protection
        assert total_amount_out >= min_amount_out, "Slippage exceeded"
        
        # Update current price
        self.current_price = new_price
        
        # TODO: Transfer assets (handled by atomic transaction group)
        
        return arc4.String("Swap executed successfully")

    @subroutine
    def _execute_swap_across_ranges(
        self, amount_in: UInt64, is_x_to_y: bool
    ) -> tuple[UInt64, UInt64, UInt64]:
        """Execute swap across all active ranges that can handle the trade"""
        
        total_amount_out = UInt64(0)
        total_fee_paid = UInt64(0)
        current_price = self.current_price
        
        # For simplicity, use the range that contains current price
        best_range = self._find_active_range_for_price(current_price)
        
        if best_range > UInt64(0):
            range_lower, range_upper = self._get_range_bounds(best_range)
            range_liquidity = self._get_range_liquidity(best_range)
            
            if range_liquidity > UInt64(0):
                amount_out, fee_paid, new_price = self._calculate_swap_in_range(
                    amount_in, range_lower, range_upper, range_liquidity, is_x_to_y
                )
                
                total_amount_out = amount_out
                total_fee_paid = fee_paid
                current_price = new_price
        
        return total_amount_out, total_fee_paid, current_price

    @subroutine
    def _calculate_swap_in_range(
        self, 
        amount_in: UInt64,
        range_lower: UInt64,
        range_upper: UInt64, 
        liquidity: UInt64,
        is_x_to_y: bool
    ) -> tuple[UInt64, UInt64, UInt64]:
        """Calculate swap output for a specific range"""
        
        # Apply fee
        fee_amount = (amount_in * self.current_fee_rate) // UInt64(10000)
        amount_in_after_fee = amount_in - fee_amount
        
        # Simplified constant product formula for this range
        # In a full implementation, this would use concentrated liquidity math
        if liquidity == UInt64(0):
            return UInt64(0), UInt64(0), self.current_price
        
        # Simplified calculation - in production would use proper concentrated liquidity formula
        amount_out = (amount_in_after_fee * liquidity) // (liquidity + amount_in_after_fee)
        
        # Calculate new price (simplified)
        price_impact = (amount_in * UInt64(FIXED_POINT_SCALE)) // (liquidity * UInt64(100))  # 1% per unit
        
        if is_x_to_y:
            new_price = self.current_price + price_impact
        else:
            new_price_calc = self.current_price - price_impact
            new_price = new_price_calc if new_price_calc >= range_lower else range_lower
        
        return amount_out, fee_amount, new_price

    @subroutine
    def _find_active_range_for_price(self, price: UInt64) -> UInt64:
        """Find which range contains the given price"""
        
        # Check Range 1 (tight)
        if price >= self.range1_lower and price <= self.range1_upper and self.range1_liquidity > UInt64(0):
            return UInt64(1)
        
        # Check Range 2 (medium)
        if price >= self.range2_lower and price <= self.range2_upper and self.range2_liquidity > UInt64(0):
            return UInt64(2)
        
        # Check Range 3 (wide)
        if price >= self.range3_lower and price <= self.range3_upper and self.range3_liquidity > UInt64(0):
            return UInt64(3)
        
        # Default to range 2 if no perfect match
        return UInt64(2)

    @subroutine
    def _get_range_bounds(self, range_id: UInt64) -> tuple[UInt64, UInt64]:
        """Get the price bounds for a specific range"""
        if range_id == UInt64(1):
            return self.range1_lower, self.range1_upper
        elif range_id == UInt64(2):
            return self.range2_lower, self.range2_upper
        else:  # range_id == 3
            return self.range3_lower, self.range3_upper

    @subroutine
    def _get_range_liquidity(self, range_id: UInt64) -> UInt64:
        """Get the liquidity amount for a specific range"""
        if range_id == UInt64(1):
            return self.range1_liquidity
        elif range_id == UInt64(2):
            return self.range2_liquidity
        else:  # range_id == 3
            return self.range3_liquidity

    @subroutine
    def _calculate_liquidity_amounts(
        self,
        amount_x_desired: UInt64,
        amount_y_desired: UInt64,
        price_lower: UInt64,
        price_upper: UInt64,
        price_current: UInt64,
    ) -> tuple[UInt64, UInt64]:
        """Calculate optimal amounts to add based on current price and range"""
        
        # Simplified calculation - maintain ratio based on current price position in range
        if price_current <= price_lower:
            # All in asset X
            return amount_x_desired, UInt64(0)
        elif price_current >= price_upper:
            # All in asset Y
            return UInt64(0), amount_y_desired
        else:
            # Mixed - use desired amounts but maintain some ratio
            # Simplified for basic version
            ratio_in_range = ((price_current - price_lower) * UInt64(FIXED_POINT_SCALE)) // (price_upper - price_lower)
            
            # Adjust amounts based on position in range
            actual_x = (amount_x_desired * (UInt64(FIXED_POINT_SCALE) - ratio_in_range)) // UInt64(FIXED_POINT_SCALE)
            actual_y = (amount_y_desired * ratio_in_range) // UInt64(FIXED_POINT_SCALE)
            
            return actual_x, actual_y

    @subroutine
    def _calculate_liquidity_for_amounts(
        self,
        amount_x: UInt64,
        amount_y: UInt64,
        price_lower: UInt64,
        price_upper: UInt64,
        price_current: UInt64,
    ) -> UInt64:
        """Calculate liquidity tokens for given amounts"""
        
        # Simplified calculation - geometric mean of amounts
        if amount_x == UInt64(0):
            return amount_y
        elif amount_y == UInt64(0):
            return amount_x
        else:
            # Use geometric mean as approximation
            return self._sqrt(amount_x * amount_y)

    @subroutine
    def _calculate_amounts_for_liquidity(
        self,
        liquidity: UInt64,
        price_lower: UInt64,
        price_upper: UInt64,
        price_current: UInt64,
    ) -> tuple[UInt64, UInt64]:
        """Calculate asset amounts for given liquidity"""
        
        # Simplified calculation based on current price position
        if price_current <= price_lower:
            return liquidity, UInt64(0)
        elif price_current >= price_upper:
            return UInt64(0), liquidity
        else:
            # Split based on position in range
            ratio = ((price_current - price_lower) * UInt64(FIXED_POINT_SCALE)) // (price_upper - price_lower)
            
            amount_x = (liquidity * (UInt64(FIXED_POINT_SCALE) - ratio)) // UInt64(FIXED_POINT_SCALE)
            amount_y = (liquidity * ratio) // UInt64(FIXED_POINT_SCALE)
            
            return amount_x, amount_y

    @subroutine
    def _sqrt(self, x: UInt64) -> UInt64:
        """Integer square root using Newton's method"""
        if x == UInt64(0):
            return UInt64(0)
        
        # Initial guess
        z = x
        y = (x + UInt64(1)) // UInt64(2)
        
        # Newton's method iteration (limited iterations for gas efficiency)
        for i in urange(10):
            if y >= z:
                return z
            z = y
            y = (y + x // y) // UInt64(2)
        
        return z

    # Read-only methods
    
    @abimethod()
    def get_pool_info(self) -> arc4.String:
        """Get current pool state information as formatted string"""
        if not self.is_initialized:
            return arc4.String("Pool not initialized")
        
        return arc4.String("Pool initialized and active")

    @abimethod()
    def get_range_info(self, range_id: UInt64) -> arc4.String:
        """Get information about a specific range"""
        assert range_id >= UInt64(1) and range_id <= UInt64(3), "Invalid range ID"
        
        range_lower, range_upper = self._get_range_bounds(range_id)
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
        Calculate expected output for a swap without executing
        
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
        
        # Calculate swap (read-only)
        amount_out, fee_paid, new_price = self._execute_swap_across_ranges(amount_in, is_x_to_y)
        
        # Calculate price impact in basis points
        price_change = new_price - self.current_price if new_price >= self.current_price else self.current_price - new_price
        price_impact_bps = (price_change * UInt64(10000)) // self.current_price
        
        return arc4.String("Swap calculation completed")
