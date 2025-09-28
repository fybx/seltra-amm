"""
Seltra Backend Service - Off-Chain Logic Handler
Handles complex calculations that were moved off-chain for deployment

This service provides:
- EWMA volatility calculations
- Decision tree logic for rebalancing
- Complex range calculations
- Safety validation
- Integration with on-chain contracts
"""

import math
import json
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
try:
    from .contract_client import SeltraContractClient, load_contract_config, PoolState, LiquidityRange
except ImportError:
    from contract_client import SeltraContractClient, load_contract_config, PoolState, LiquidityRange


@dataclass
class Range:
    """Represents a liquidity range"""
    lower: float
    upper: float
    liquidity: float


@dataclass
class PoolState:
    """Represents current pool state"""
    current_price: float
    total_liquidity: float
    range1_liquidity: float
    range2_liquidity: float
    range3_liquidity: float


@dataclass
class OracleState:
    """Represents current oracle state"""
    current_price: float
    current_volatility: float
    current_regime: str
    last_update_time: int
    price_history: List[float]


class VolatilityCalculator:
    """Handles EWMA volatility calculations"""
    
    def __init__(self, alpha: float = 0.3, window_size: int = 10):
        self.alpha = alpha
        self.window_size = window_size
        self.ewma_mean = 0.0
        self.ewma_variance = 0.0
        self.price_history: List[float] = []
    
    def update_price(self, new_price: float) -> Tuple[float, str]:
        """
        Update price and calculate new volatility
        
        Args:
            new_price: New price observation
            
        Returns:
            Tuple of (volatility, regime)
        """
        if len(self.price_history) > 0:
            # Calculate return
            old_price = self.price_history[-1]
            return_value = (new_price - old_price) / old_price
            
            # Update EWMA
            self.ewma_mean = self.alpha * return_value + (1 - self.alpha) * self.ewma_mean
            self.ewma_variance = self.alpha * (return_value - self.ewma_mean) ** 2 + (1 - self.alpha) * self.ewma_variance
            
            # Calculate volatility
            volatility = math.sqrt(self.ewma_variance) * 100  # Convert to percentage
        
        else:
            volatility = 3.0  # Default 3% volatility
        
        # Add to history
        self.price_history.append(new_price)
        if len(self.price_history) > self.window_size:
            self.price_history.pop(0)
        
        # Classify regime
        regime = self._classify_regime(volatility)
        
        return volatility, regime
    
    def _classify_regime(self, volatility: float) -> str:
        """Classify volatility regime"""
        if volatility < 2.0:
            return "low"
        elif volatility > 5.0:
            return "high"
        else:
            return "medium"


class RebalancingEngine:
    """Handles complex rebalancing logic"""
    
    def __init__(self):
        # Decision tree thresholds
        self.ULTRA_LOW_THRESHOLD = 1.5
        self.LOW_THRESHOLD = 3.0
        self.MEDIUM_THRESHOLD = 6.0
        self.HIGH_THRESHOLD = 12.0
        
        # Concentration factors
        self.ULTRA_LOW_FACTOR = 0.4
        self.LOW_FACTOR = 0.6
        self.MEDIUM_FACTOR = 1.0
        self.HIGH_FACTOR = 1.8
        self.EXTREME_FACTOR = 2.5
        
        # Range counts
        self.ULTRA_LOW_RANGES = 2
        self.LOW_RANGES = 3
        self.MEDIUM_RANGES = 4
        self.HIGH_RANGES = 5
        self.EXTREME_RANGES = 6
    
    def classify_volatility_regime(self, volatility: float) -> Tuple[str, float, int]:
        """
        Classify volatility regime using decision tree logic
        
        Returns:
            Tuple of (regime_name, concentration_factor, num_ranges)
        """
        if volatility < self.ULTRA_LOW_THRESHOLD:
            return "ultra_low", self.ULTRA_LOW_FACTOR, self.ULTRA_LOW_RANGES
        elif volatility < self.LOW_THRESHOLD:
            return "low", self.LOW_FACTOR, self.LOW_RANGES
        elif volatility < self.MEDIUM_THRESHOLD:
            return "medium", self.MEDIUM_FACTOR, self.MEDIUM_RANGES
        elif volatility < self.HIGH_THRESHOLD:
            return "high", self.HIGH_FACTOR, self.HIGH_RANGES
        else:
            return "extreme", self.EXTREME_FACTOR, self.EXTREME_RANGES
    
    def calculate_optimal_ranges(
        self, 
        current_price: float, 
        volatility: float, 
        total_liquidity: float
    ) -> List[Range]:
        """
        Calculate optimal ranges for given market conditions
        
        Args:
            current_price: Current market price
            volatility: Current volatility percentage
            total_liquidity: Total liquidity to distribute
            
        Returns:
            List of optimal ranges
        """
        # Get regime classification
        regime, concentration_factor, num_ranges = self.classify_volatility_regime(volatility)
        
        # Calculate price bounds based on concentration factor
        price_bound_percent = concentration_factor * 100
        price_bound_percent = min(price_bound_percent, 50)  # Cap at 50%
        
        # Calculate actual price bounds
        price_range = current_price * (price_bound_percent / 100)
        min_price = current_price - price_range
        max_price = current_price + price_range
        
        # Ensure minimum bounds
        if min_price <= 0:
            min_price = current_price * 0.5
        if max_price <= min_price:
            max_price = min_price + current_price * 0.1
        
        # Create ranges
        ranges = []
        range_size = (max_price - min_price) / num_ranges
        
        for i in range(num_ranges):
            lower = min_price + (i * range_size)
            upper = min_price + ((i + 1) * range_size)
            
            # Calculate liquidity allocation (more near current price)
            range_center = (lower + upper) / 2
            distance = abs(range_center - current_price)
            max_distance = (max_price - min_price) / 2
            
            if max_distance > 0:
                proximity_factor = (max_distance - distance) / max_distance
            else:
                proximity_factor = 1.0
            
            # Base allocation with proximity bias
            base_allocation = total_liquidity / num_ranges
            proximity_bonus = base_allocation * proximity_factor * 0.5  # Max 50% bonus
            liquidity = base_allocation + proximity_bonus
            
            ranges.append(Range(lower, upper, liquidity))
        
        return ranges
    
    def validate_rebalancing_safety(
        self, 
        old_ranges: List[Range], 
        new_ranges: List[Range]
    ) -> Tuple[bool, str]:
        """
        Validate rebalancing safety
        
        Returns:
            Tuple of (is_safe, reason)
        """
        # Check liquidity conservation
        old_total = sum(r.liquidity for r in old_ranges)
        new_total = sum(r.liquidity for r in new_ranges)
        
        # Allow 0.1% rounding error
        diff = abs(old_total - new_total)
        if diff > (old_total * 0.001):
            return False, "Liquidity not conserved"
        
        # Check range validity
        for i, range_obj in enumerate(new_ranges):
            if range_obj.liquidity > 0:  # Non-empty range
                if range_obj.lower >= range_obj.upper:
                    return False, f"Invalid range {i}: lower >= upper"
                
                if range_obj.liquidity <= 0:
                    return False, f"Invalid range {i}: non-positive liquidity"
                
                # Check minimum range size (0.5%)
                range_size_percent = ((range_obj.upper - range_obj.lower) / range_obj.lower) * 100
                if range_size_percent < 0.5:
                    return False, f"Range {i} too small"
        
        return True, "Validation passed"
    
    def calculate_efficiency_score(
        self, 
        ranges: List[Range], 
        current_price: float, 
        volatility: float
    ) -> float:
        """
        Calculate efficiency score for range configuration
        
        Returns:
            Efficiency score (0-100)
        """
        total_liquidity = sum(r.liquidity for r in ranges)
        if total_liquidity == 0:
            return 0.0
        
        concentration_score = 0.0
        
        for range_obj in ranges:
            if range_obj.liquidity > 0:
                # Calculate proximity to current price
                range_center = (range_obj.lower + range_obj.upper) / 2
                distance = abs(range_center - current_price)
                max_reasonable_distance = current_price * (volatility / 100) * 2  # 2σ movement
                
                if distance <= max_reasonable_distance:
                    proximity_score = 100 - (distance / max_reasonable_distance) * 50
                else:
                    proximity_score = 50 / (1 + distance / max_reasonable_distance)
                
                weighted_score = proximity_score * (range_obj.liquidity / total_liquidity)
                concentration_score += weighted_score
        
        return min(concentration_score, 100.0)
    
    def should_rebalance(
        self, 
        current_efficiency: float, 
        time_since_last: int, 
        volatility_change: float
    ) -> bool:
        """
        Determine if rebalancing should be triggered
        
        Args:
            current_efficiency: Current efficiency score (0-100)
            time_since_last: Time since last rebalance (seconds)
            volatility_change: Change in volatility since last rebalance
            
        Returns:
            True if rebalancing is recommended
        """
        # Check efficiency threshold (rebalance if efficiency < 60%)
        if current_efficiency < 60:
            return True
        
        # Check volatility change threshold (rebalance if change > 2%)
        if volatility_change > 2.0:
            return True
        
        # Check if it's been too long since last rebalance (1 hour)
        if time_since_last > 3600:
            return True
        
        return False


class SeltraBackendService:
    """Main backend service orchestrating all off-chain logic"""
    
    def __init__(self):
        self.volatility_calculator = VolatilityCalculator()
        self.rebalancing_engine = RebalancingEngine()
        self.pool_state: Optional[PoolState] = None
        self.oracle_state: Optional[OracleState] = None
        
        # Initialize contract client
        try:
            self.contract_config = load_contract_config()
            self.contract_client = SeltraContractClient(self.contract_config)
            self.contract_connected = True
            print("✅ Connected to deployed contracts")
        except Exception as e:
            print(f"⚠️ Warning: Could not connect to contracts: {e}")
            self.contract_connected = False
    
    def update_oracle(self, new_price: float) -> Tuple[float, str]:
        """
        Update oracle with new price and calculate volatility
        
        Args:
            new_price: New price observation
            
        Returns:
            Tuple of (volatility, regime)
        """
        volatility, regime = self.volatility_calculator.update_price(new_price)
        
        # Update oracle state
        if self.oracle_state:
            self.oracle_state.current_price = new_price
            self.oracle_state.current_volatility = volatility
            self.oracle_state.current_regime = regime
            self.oracle_state.last_update_time = int(datetime.now().timestamp())
        
        return volatility, regime
    
    def check_rebalancing(
        self, 
        current_price: float, 
        current_volatility: float, 
        total_liquidity: float,
        current_efficiency: float,
        time_since_last: int,
        volatility_change: float
    ) -> Tuple[bool, List[Range], str]:
        """
        Check if rebalancing should be triggered and calculate optimal ranges
        
        Returns:
            Tuple of (should_rebalance, optimal_ranges, reason)
        """
        # Check if rebalancing should be triggered
        should_rebalance = self.rebalancing_engine.should_rebalance(
            current_efficiency, time_since_last, volatility_change
        )
        
        if not should_rebalance:
            return False, [], "No rebalancing needed"
        
        # Calculate optimal ranges
        optimal_ranges = self.rebalancing_engine.calculate_optimal_ranges(
            current_price, current_volatility, total_liquidity
        )
        
        return True, optimal_ranges, "Rebalancing recommended"
    
    def validate_rebalancing_proposal(
        self, 
        old_ranges: List[Range], 
        new_ranges: List[Range],
        current_price: float,
        volatility: float
    ) -> Tuple[bool, str, float]:
        """
        Validate a proposed rebalancing operation
        
        Returns:
            Tuple of (is_valid, reason, efficiency_gain)
        """
        # Validate safety
        is_safe, safety_reason = self.rebalancing_engine.validate_rebalancing_safety(
            old_ranges, new_ranges
        )
        
        if not is_safe:
            return False, f"UNSAFE: {safety_reason}", 0.0
        
        # Calculate efficiency improvement
        current_efficiency = self.rebalancing_engine.calculate_efficiency_score(
            old_ranges, current_price, volatility
        )
        proposed_efficiency = self.rebalancing_engine.calculate_efficiency_score(
            new_ranges, current_price, volatility
        )
        efficiency_gain = proposed_efficiency - current_efficiency
        
        # Determine if improvement is significant
        if efficiency_gain < 1.0:  # Less than 1% improvement
            return False, f"INSUFFICIENT_GAIN: {efficiency_gain:.2f}%", efficiency_gain
        
        return True, f"VALID: efficiency_gain={efficiency_gain:.2f}%", efficiency_gain
    
    def format_ranges_for_contract(self, ranges: List[Range]) -> str:
        """
        Format ranges for on-chain contract storage
        
        Args:
            ranges: List of ranges to format
            
        Returns:
            JSON-like string for contract storage
        """
        range_data = []
        for r in ranges:
            range_data.append({
                "lower": r.lower,
                "upper": r.upper,
                "liquidity": r.liquidity
            })
        
        return json.dumps(range_data)
    
    def parse_ranges_from_contract(self, ranges_json: str) -> List[Range]:
        """
        Parse ranges from contract storage format
        
        Args:
            ranges_json: JSON string from contract
            
        Returns:
            List of Range objects
        """
        try:
            range_data = json.loads(ranges_json)
            ranges = []
            for r in range_data:
                ranges.append(Range(
                    lower=r["lower"],
                    upper=r["upper"],
                    liquidity=r["liquidity"]
                ))
            return ranges
        except (json.JSONDecodeError, KeyError):
            return []
    
    def sync_with_contracts(self) -> Dict[str, Any]:
        """
        Sync backend state with deployed contracts
        
        Returns:
            Dictionary with current contract state
        """
        if not self.contract_connected:
            return {"error": "Not connected to contracts"}
        
        try:
            # Get current pool state from contract
            contract_pool_state = self.contract_client.get_pool_state()
            contract_ranges = self.contract_client.get_liquidity_ranges()
            
            # Update local state
            self.pool_state = PoolState(
                current_price=contract_pool_state.current_price / 1e18,  # Convert from fixed point
                total_liquidity=contract_pool_state.total_liquidity / 1e6,  # Convert from microAlgos
                range1_liquidity=contract_ranges[0].liquidity_amount / 1e6 if len(contract_ranges) > 0 else 0,
                range2_liquidity=contract_ranges[1].liquidity_amount / 1e6 if len(contract_ranges) > 1 else 0,
                range3_liquidity=contract_ranges[2].liquidity_amount / 1e6 if len(contract_ranges) > 2 else 0
            )
            
            return {
                "pool_state": {
                    "current_price": self.pool_state.current_price,
                    "total_liquidity": self.pool_state.total_liquidity,
                    "asset_x_id": contract_pool_state.asset_x_id,
                    "asset_y_id": contract_pool_state.asset_y_id,
                    "fee_rate": contract_pool_state.current_fee_rate
                },
                "liquidity_ranges": [
                    {
                        "range_id": r.range_id,
                        "price_lower": r.price_lower / 1e18,
                        "price_upper": r.price_upper / 1e18,
                        "liquidity": r.liquidity_amount / 1e6,
                        "is_active": r.is_active
                    }
                    for r in contract_ranges
                ],
                "status": "synced"
            }
        except Exception as e:
            return {"error": f"Failed to sync with contracts: {e}"}
    
    async def execute_rebalance_on_chain(self, new_ranges: List[Range]) -> str:
        """
        Execute rebalancing on the deployed contracts
        
        Args:
            new_ranges: New liquidity ranges to set
            
        Returns:
            Transaction ID of the rebalance
        """
        if not self.contract_connected:
            raise Exception("Not connected to contracts")
        
        try:
            # Trigger rebalance on contract
            tx_id = self.contract_client.trigger_rebalance()
            print(f"✅ Rebalance executed: {tx_id}")
            return tx_id
        except Exception as e:
            print(f"❌ Failed to execute rebalance: {e}")
            raise
    
    def get_contract_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive metrics from contracts and backend
        
        Returns:
            Dictionary with all relevant metrics
        """
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "contract_connected": self.contract_connected
        }
        
        if self.contract_connected:
            try:
                # Get contract state
                contract_state = self.sync_with_contracts()
                metrics.update(contract_state)
                
                # Add volatility metrics
                if self.oracle_state:
                    metrics["volatility"] = {
                        "current": self.oracle_state.current_volatility,
                        "regime": self.oracle_state.current_regime,
                        "last_update": self.oracle_state.last_update_time
                    }
                
                # Add efficiency metrics
                if self.pool_state:
                    efficiency = self.rebalancing_engine.calculate_efficiency_score(
                        [],  # Will be filled from contract ranges
                        self.pool_state.current_price,
                        0.02  # Default volatility
                    )
                    metrics["efficiency"] = efficiency
                
            except Exception as e:
                metrics["error"] = f"Failed to get metrics: {e}"
        
        return metrics


# Example usage and testing
if __name__ == "__main__":
    # Initialize backend service
    backend = SeltraBackendService()
    
    # Simulate price updates
    prices = [100.0, 101.0, 99.5, 102.0, 98.0, 103.0, 97.5, 104.0]
    
    print("=== Volatility Calculation Demo ===")
    for price in prices:
        volatility, regime = backend.update_oracle(price)
        print(f"Price: {price:.2f}, Volatility: {volatility:.2f}%, Regime: {regime}")
    
    print("\n=== Rebalancing Demo ===")
    current_price = 100.0
    current_volatility = 3.5
    total_liquidity = 1000000.0
    
    # Check rebalancing
    should_rebalance, optimal_ranges, reason = backend.check_rebalancing(
        current_price, current_volatility, total_liquidity,
        current_efficiency=45.0,  # Low efficiency
        time_since_last=400,      # 400 seconds
        volatility_change=2.5     # 2.5% change
    )
    
    print(f"Should rebalance: {should_rebalance}")
    print(f"Reason: {reason}")
    
    if should_rebalance:
        print("Optimal ranges:")
        for i, r in enumerate(optimal_ranges):
            print(f"  Range {i+1}: {r.lower:.2f} - {r.upper:.2f}, Liquidity: {r.liquidity:.0f}")
        
        # Format for contract
        ranges_json = backend.format_ranges_for_contract(optimal_ranges)
        print(f"\nFormatted for contract: {ranges_json}")
