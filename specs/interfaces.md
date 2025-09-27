# Seltra AMM - Interface Definitions

## Overview

This document defines all interfaces, data structures, and communication protocols between Seltra AMM components. These interfaces ensure clean separation of concerns and enable independent development of each component.

## Core Data Structures

### Asset and Pricing

```python
@dataclass
class Asset:
    """Algorand Standard Asset (ASA) representation."""
    id: int                    # Asset ID on Algorand
    name: str                  # Asset name (e.g., "ALGO", "USDC")
    decimals: int             # Number of decimal places
    total_supply: int         # Total asset supply
    
@dataclass  
class Price:
    """Price representation with metadata."""
    value: int                # Price in fixed point (1e18 scale)
    timestamp: int           # When price was recorded
    confidence: int          # Confidence level (0-100)
    source: str              # Source of price data

@dataclass
class PriceMovement:
    """Price change information."""
    old_price: int
    new_price: int
    change_percent: int      # Basis points (e.g., 500 = 5%)
    change_absolute: int
    timestamp: int
```

### Liquidity Management

```python
@dataclass
class LiquidityRange:
    """Concentrated liquidity range specification."""
    range_id: int            # Unique range identifier
    price_lower: int         # Lower price bound (fixed point)
    price_upper: int         # Upper price bound (fixed point)
    liquidity_amount: int    # Total liquidity in range
    active_liquidity: int    # Currently active liquidity
    fees_collected_x: int    # Fees collected for asset X
    fees_collected_y: int    # Fees collected for asset Y
    is_active: bool          # Whether range is currently active
    created_at: int          # Range creation timestamp
    last_updated: int        # Last modification timestamp

@dataclass
class LiquidityPosition:
    """User's liquidity provider position."""
    user_address: bytes      # LP's address
    range_id: int           # Associated range ID
    lp_tokens: int          # LP tokens owned
    original_amount_x: int  # Original asset X deposited
    original_amount_y: int  # Original asset Y deposited
    unclaimed_fees_x: int   # Unclaimed fees in asset X
    unclaimed_fees_y: int   # Unclaimed fees in asset Y
    entry_price: int        # Price when position was created
    last_fee_claim: int     # Last fee claim timestamp

@dataclass
class RebalanceProposal:
    """Proposed liquidity rebalancing operation."""
    proposal_id: int
    current_ranges: list[LiquidityRange]
    proposed_ranges: list[LiquidityRange]
    efficiency_gain: int    # Expected efficiency improvement (basis points)
    gas_estimate: int       # Estimated gas cost
    safety_score: int       # Safety assessment (0-100)
    created_at: int
    expires_at: int
```

### Trading Operations

```python
@dataclass
class TradeRequest:
    """Trading operation request."""
    trader: bytes           # Trader's address
    asset_in: Asset        # Input asset
    asset_out: Asset       # Output asset
    amount_in: int         # Input amount
    min_amount_out: int    # Minimum acceptable output
    max_slippage: int      # Maximum slippage (basis points)
    deadline: int          # Transaction deadline
    
@dataclass
class TradeResult:
    """Result of executed trade."""
    trader: bytes
    asset_in: Asset
    asset_out: Asset
    amount_in: int
    amount_out: int
    actual_slippage: int    # Actual slippage experienced
    fee_paid: int          # Total fee paid
    price_impact: int      # Price impact (basis points)
    execution_price: int   # Average execution price
    gas_used: int          # Gas consumed
    timestamp: int

@dataclass
class SwapQuote:
    """Quote for potential swap."""
    amount_in: int
    estimated_amount_out: int
    price_impact: int      # Estimated price impact (basis points)
    fee_estimate: int      # Estimated fee
    route: list[int]       # Range IDs to be used
    valid_until: int       # Quote expiration time
```

## Component Interfaces

### IPriceOracle Interface

```python
class IPriceOracle:
    """Interface for price and volatility data providers."""
    
    def get_current_price(self) -> Price:
        """Get current market price with metadata."""
        pass
    
    def get_price_history(self, count: int) -> list[Price]:
        """Get recent price history."""
        pass
    
    def get_current_volatility(self) -> tuple[int, int, int]:
        """Get (volatility, regime, confidence)."""
        pass
    
    def update_price(self, new_price: int, volume: int) -> None:
        """Update oracle with new price data."""
        pass
    
    def should_rebalance(self) -> tuple[bool, int]:
        """Check if rebalancing should be triggered."""
        pass
```

### IRebalancer Interface

```python
class IRebalancer:
    """Interface for liquidity rebalancing operations."""
    
    def calculate_optimal_ranges(
        self,
        current_price: int,
        volatility: int,
        regime: int,
        total_liquidity: int
    ) -> list[LiquidityRange]:
        """Calculate optimal range configuration."""
        pass
    
    def validate_rebalance(
        self,
        current_ranges: list[LiquidityRange],
        proposed_ranges: list[LiquidityRange]
    ) -> tuple[bool, str]:
        """Validate proposed rebalancing operation."""
        pass
    
    def execute_rebalance(
        self,
        proposal: RebalanceProposal
    ) -> tuple[bool, str]:
        """Execute validated rebalancing operation."""
        pass
    
    def estimate_rebalance_cost(
        self,
        current_ranges: list[LiquidityRange],
        proposed_ranges: list[LiquidityRange]
    ) -> int:
        """Estimate gas cost for rebalancing."""
        pass
```

### IFeeCalculator Interface

```python
class IFeeCalculator:
    """Interface for dynamic fee calculation."""
    
    def calculate_swap_fee(
        self,
        volatility: int,
        volume_24h: int,
        liquidity: int,
        trade_size: int,
        trader: bytes = None
    ) -> tuple[int, int]:
        """Calculate (total_fee, protocol_fee) for trade."""
        pass
    
    def get_trader_tier(self, trader: bytes) -> tuple[int, int]:
        """Get (tier_level, discount_bps) for trader."""
        pass
    
    def record_trade(
        self,
        trader: bytes,
        trade_size: int,
        fee_paid: int
    ) -> None:
        """Record trade for fee tier calculation."""
        pass
    
    def estimate_lp_yield(
        self,
        liquidity_amount: int,
        range_config: LiquidityRange,
        expected_volume: int
    ) -> int:
        """Estimate APY for LP position."""
        pass
```

### ILiquidityManager Interface

```python
class ILiquidityManager:
    """Interface for liquidity position management."""
    
    def add_liquidity(
        self,
        user: bytes,
        asset_x: Asset,
        asset_y: Asset,
        amount_x: int,
        amount_y: int,
        range_spec: tuple[int, int]
    ) -> LiquidityPosition:
        """Add liquidity to specified range."""
        pass
    
    def remove_liquidity(
        self,
        user: bytes,
        position_id: int,
        liquidity_to_remove: int
    ) -> tuple[int, int]:
        """Remove liquidity and return assets."""
        pass
    
    def claim_fees(
        self,
        user: bytes,
        position_id: int
    ) -> tuple[int, int]:
        """Claim accumulated fees."""
        pass
    
    def get_user_positions(
        self,
        user: bytes
    ) -> list[LiquidityPosition]:
        """Get all positions for user."""
        pass
    
    def redistribute_liquidity(
        self,
        old_ranges: list[LiquidityRange],
        new_ranges: list[LiquidityRange]
    ) -> bool:
        """Redistribute liquidity across ranges."""
        pass
```

### ISwapEngine Interface

```python
class ISwapEngine:
    """Interface for trade execution."""
    
    def get_swap_quote(
        self,
        asset_in: Asset,
        asset_out: Asset,
        amount_in: int
    ) -> SwapQuote:
        """Get quote for potential swap."""
        pass
    
    def execute_swap(
        self,
        trade_request: TradeRequest
    ) -> TradeResult:
        """Execute swap transaction."""
        pass
    
    def calculate_price_impact(
        self,
        asset_in: Asset,
        amount_in: int,
        available_ranges: list[LiquidityRange]
    ) -> int:
        """Calculate price impact for trade size."""
        pass
    
    def find_optimal_route(
        self,
        asset_in: Asset,
        asset_out: Asset,
        amount_in: int,
        ranges: list[LiquidityRange]
    ) -> list[int]:
        """Find optimal routing through ranges."""
        pass
```

## Event Interfaces

### IEventEmitter Interface

```python
class IEventEmitter:
    """Interface for event emission and handling."""
    
    def emit_swap_event(self, trade_result: TradeResult) -> None:
        """Emit swap execution event."""
        pass
    
    def emit_liquidity_event(
        self,
        event_type: str,
        position: LiquidityPosition
    ) -> None:
        """Emit liquidity management event."""
        pass
    
    def emit_rebalance_event(
        self,
        old_ranges: list[LiquidityRange],
        new_ranges: list[LiquidityRange],
        efficiency_gain: int
    ) -> None:
        """Emit rebalancing event."""
        pass
    
    def emit_volatility_event(
        self,
        old_volatility: int,
        new_volatility: int,
        regime_change: bool
    ) -> None:
        """Emit volatility update event."""
        pass

class IEventListener:
    """Interface for event listeners."""
    
    def on_swap_executed(self, trade_result: TradeResult) -> None:
        """Handle swap execution events."""
        pass
    
    def on_liquidity_changed(
        self,
        event_type: str,
        position: LiquidityPosition
    ) -> None:
        """Handle liquidity change events."""
        pass
    
    def on_rebalance_executed(
        self,
        old_ranges: list[LiquidityRange],
        new_ranges: list[LiquidityRange]
    ) -> None:
        """Handle rebalancing events."""
        pass
    
    def on_volatility_updated(
        self,
        new_volatility: int,
        regime: int
    ) -> None:
        """Handle volatility update events."""
        pass
```

## Communication Protocols

### Contract-to-Contract Calls

```python
class ContractCall:
    """Base class for inter-contract communication."""
    
    @dataclass
    class CallParams:
        target_contract: bytes     # Target contract address
        method_selector: bytes     # Method to call
        arguments: list[any]       # Method arguments
        caller_auth: bytes         # Caller authorization
        gas_limit: int            # Gas limit for call
        
    @dataclass
    class CallResult:
        success: bool             # Whether call succeeded
        return_data: bytes        # Returned data
        gas_used: int            # Gas consumed
        error_message: str       # Error message if failed

# Oracle Update Protocol
@dataclass
class OracleUpdateCall(ContractCall):
    """Protocol for updating oracle with price data."""
    new_price: int
    volume: int
    timestamp: int
    
# Rebalancing Protocol  
@dataclass
class RebalanceCall(ContractCall):
    """Protocol for triggering rebalancing."""
    trigger_volatility: int
    proposed_ranges: list[LiquidityRange]
    safety_checks: bool

# Fee Calculation Protocol
@dataclass
class FeeCalculationCall(ContractCall):
    """Protocol for dynamic fee calculation."""
    current_volatility: int
    trade_size: int
    available_liquidity: int
    trader_address: bytes
```

### State Synchronization

```python
class StateSyncProtocol:
    """Protocol for maintaining state consistency across contracts."""
    
    @dataclass
    class StateSnapshot:
        contract_address: bytes
        state_hash: bytes
        timestamp: int
        version: int
        
    @dataclass
    class StateUpdate:
        contract_address: bytes
        field_name: str
        old_value: bytes
        new_value: bytes
        update_timestamp: int
        
    def create_snapshot(self) -> StateSnapshot:
        """Create state snapshot for synchronization."""
        pass
        
    def apply_update(self, update: StateUpdate) -> bool:
        """Apply state update from another contract."""
        pass
        
    def validate_consistency(
        self,
        snapshots: list[StateSnapshot]
    ) -> bool:
        """Validate state consistency across contracts."""
        pass
```

## Error Handling Interfaces

### IErrorHandler Interface

```python
class IErrorHandler:
    """Interface for standardized error handling."""
    
    @dataclass
    class ErrorInfo:
        error_code: int
        error_message: str
        contract_address: bytes
        timestamp: int
        context_data: dict
        
    def handle_error(
        self,
        error_code: int,
        message: str,
        context: dict = None
    ) -> None:
        """Handle and log error."""
        pass
    
    def get_error_history(
        self,
        contract_address: bytes = None,
        since: int = None
    ) -> list[ErrorInfo]:
        """Get error history for debugging."""
        pass
    
    def is_recoverable_error(self, error_code: int) -> bool:
        """Check if error is recoverable."""
        pass
```

## Authentication and Authorization

### IAccessControl Interface

```python
class IAccessControl:
    """Interface for access control management."""
    
    @dataclass
    class Permission:
        resource: str            # Resource identifier
        action: str             # Action being performed
        required_role: str      # Required role for action
        
    def has_permission(
        self,
        user: bytes,
        permission: Permission
    ) -> bool:
        """Check if user has required permission."""
        pass
    
    def grant_role(
        self,
        user: bytes,
        role: str,
        grantor: bytes
    ) -> bool:
        """Grant role to user."""
        pass
    
    def revoke_role(
        self,
        user: bytes,
        role: str,
        revoker: bytes
    ) -> bool:
        """Revoke role from user."""
        pass
    
    def get_user_roles(self, user: bytes) -> list[str]:
        """Get all roles for user."""
        pass
```

## Configuration Interfaces

### IConfigurable Interface

```python
class IConfigurable:
    """Interface for configurable contract parameters."""
    
    @dataclass
    class ConfigParam:
        name: str
        value: any
        value_type: str         # "int", "bytes", "bool", etc.
        min_value: any
        max_value: any
        description: str
        
    def set_config(
        self,
        param_name: str,
        value: any,
        setter: bytes
    ) -> bool:
        """Set configuration parameter."""
        pass
    
    def get_config(self, param_name: str) -> ConfigParam:
        """Get configuration parameter."""
        pass
    
    def get_all_config(self) -> list[ConfigParam]:
        """Get all configuration parameters."""
        pass
    
    def validate_config(
        self,
        param_name: str,
        value: any
    ) -> tuple[bool, str]:
        """Validate configuration value."""
        pass
```

## Integration Constants

```python
# Interface Version Numbers
INTERFACE_VERSION = "1.0.0"
PRICE_ORACLE_VERSION = "1.0.0"
REBALANCER_VERSION = "1.0.0"
FEE_CALCULATOR_VERSION = "1.0.0"
LIQUIDITY_MANAGER_VERSION = "1.0.0"
SWAP_ENGINE_VERSION = "1.0.0"

# Method Selectors (first 4 bytes of method signature hash)
METHOD_SELECTORS = {
    "update_price": b"\x12\x34\x56\x78",
    "calculate_optimal_ranges": b"\x87\x65\x43\x21",
    "calculate_swap_fee": b"\xab\xcd\xef\x12",
    "execute_swap": b"\x34\x56\x78\x9a",
    "add_liquidity": b"\xbc\xde\xf1\x23"
}

# Event Signatures
EVENT_SIGNATURES = {
    "SwapExecuted": "SwapExecuted(address,uint256,uint256,uint256,uint256)",
    "LiquidityAdded": "LiquidityAdded(address,uint256,uint256,uint256)",
    "LiquidityRemoved": "LiquidityRemoved(address,uint256,uint256,uint256)",
    "RebalanceExecuted": "RebalanceExecuted(uint256,uint256[],uint256[])",
    "VolatilityUpdated": "VolatilityUpdated(uint256,uint256,uint256)"
}

# Standard Error Codes
STANDARD_ERRORS = {
    "UNAUTHORIZED": 1000,
    "INVALID_PARAMETERS": 1001,
    "INSUFFICIENT_BALANCE": 1002,
    "SLIPPAGE_EXCEEDED": 1003,
    "DEADLINE_EXCEEDED": 1004,
    "CONTRACT_PAUSED": 1005,
    "INVALID_STATE": 1006,
    "CALCULATION_OVERFLOW": 1007,
    "EXTERNAL_CALL_FAILED": 1008,
    "REENTRANCY_DETECTED": 1009
}
```

---

These interface definitions provide a complete specification for component interaction in the Seltra AMM system, ensuring clean architecture and enabling independent development and testing of each component.
