"""
Market Simulator Implementation

Provides realistic market conditions for testing and demonstrating the Seltra AMM.
Generates price movements, trading volumes, and volatility scenarios.
"""

import asyncio
import time
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from enum import Enum


class VolatilityRegime(Enum):
    """Volatility regime classification."""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"


class MarketScenario(Enum):
    """Predefined market scenarios."""
    NORMAL = "normal"
    VOLATILE = "volatile"
    CALM = "calm"
    TRENDING = "trending"
    MEAN_REVERTING = "mean_reverting"
    FLASH_CRASH = "flash_crash"
    WHALE_ACTIVITY = "whale_activity"


@dataclass
class PricePoint:
    """Single price data point."""
    price: float
    volume: float
    timestamp: int
    volatility: float


@dataclass
class SimulationMetrics:
    """Simulation performance metrics."""
    realized_volatility: float
    max_drawdown: float
    sharpe_ratio: float
    volume_weighted_price: float
    total_trades: int
    average_trade_size: float


class MarketSimulator:
    """
    Market simulator with realistic price movements and volatility regimes.
    """
    
    def __init__(
        self,
        initial_price: float = 100.0,
        initial_volatility: float = 0.02,
        tick_interval: float = 1.0
    ):
        """
        Initialize market simulator.
        
        Args:
            initial_price: Starting price for the asset pair
            initial_volatility: Initial volatility (standard deviation)
            tick_interval: Time between price updates (seconds)
        """
        self.initial_price = initial_price
        self.current_price = initial_price
        self.initial_volatility = initial_volatility
        self.current_volatility = initial_volatility
        self.tick_interval = tick_interval
        
        # State management
        self.is_running = False
        self.current_scenario = MarketScenario.NORMAL
        self.volatility_regime = VolatilityRegime.MEDIUM
        
        # Price history
        self.price_history: List[PricePoint] = []
        self.max_history_size = 1000
        
        # Market parameters
        self.drift = 0.0001  # Expected return
        self.base_volume = 100000  # Base trading volume
        self.volume_multiplier = 1.0
        
        # Simulation state
        self.start_time = time.time()
        self.total_trades = 0
        
        # Event tracking
        self.pending_shocks = []
        self.pending_volume_spikes = []
        
    async def run_simulation(self):
        """Run the market simulation loop."""
        self.is_running = True
        self.start_time = time.time()
        
        # Add initial price point
        self._add_price_point(
            self.current_price,
            self.base_volume,
            self.current_volatility
        )
        
        try:
            while self.is_running:
                await asyncio.sleep(self.tick_interval)
                await self._update_market()
                
        except asyncio.CancelledError:
            self.is_running = False
            raise
    
    def stop_simulation(self):
        """Stop the market simulation."""
        self.is_running = False
    
    def reset_simulation(self, new_initial_price: Optional[float] = None):
        """Reset simulation to initial state."""
        if new_initial_price:
            self.initial_price = new_initial_price
        
        self.current_price = self.initial_price
        self.current_volatility = self.initial_volatility
        self.price_history.clear()
        self.total_trades = 0
        self.start_time = time.time()
        self.pending_shocks.clear()
        self.pending_volume_spikes.clear()
    
    async def _update_market(self):
        """Update market state with new price and volume."""
        # Handle pending price shocks
        self._process_price_shocks()
        
        # Generate new price based on current scenario
        new_price = self._generate_next_price()
        
        # Generate volume
        volume = self._generate_volume()
        
        # Update volatility
        self._update_volatility(new_price)
        
        # Update regime if necessary
        self._update_volatility_regime()
        
        # Add to history
        self._add_price_point(new_price, volume, self.current_volatility)
        
        # Update current price
        self.current_price = new_price
        self.total_trades += 1
    
    def _generate_next_price(self) -> float:
        """Generate next price based on current scenario."""
        dt = self.tick_interval / 86400  # Convert to fraction of day
        
        if self.current_scenario == MarketScenario.NORMAL:
            return self._gbm_price_movement(dt)
        elif self.current_scenario == MarketScenario.VOLATILE:
            return self._volatile_price_movement(dt)
        elif self.current_scenario == MarketScenario.CALM:
            return self._mean_reverting_movement(dt)
        elif self.current_scenario == MarketScenario.TRENDING:
            return self._trending_movement(dt)
        elif self.current_scenario == MarketScenario.FLASH_CRASH:
            return self._jump_diffusion_movement(dt)
        else:
            return self._gbm_price_movement(dt)
    
    def _gbm_price_movement(self, dt: float) -> float:
        """Geometric Brownian Motion price movement."""
        random_shock = random.gauss(0, 1)
        
        price_change = (
            self.drift * self.current_price * dt +
            self.current_volatility * self.current_price * math.sqrt(dt) * random_shock
        )
        
        new_price = self.current_price + price_change
        return max(new_price, 0.01)  # Prevent negative prices
    
    def _volatile_price_movement(self, dt: float) -> float:
        """High volatility price movement with regime switching."""
        # Increase volatility randomly
        volatility_multiplier = 1.0 + random.uniform(0, 2.0)
        effective_volatility = self.current_volatility * volatility_multiplier
        
        random_shock = random.gauss(0, 1)
        
        price_change = (
            self.drift * self.current_price * dt +
            effective_volatility * self.current_price * math.sqrt(dt) * random_shock
        )
        
        new_price = self.current_price + price_change
        return max(new_price, 0.01)
    
    def _mean_reverting_movement(self, dt: float) -> float:
        """Mean-reverting (Ornstein-Uhlenbeck) price movement."""
        reversion_speed = 0.1
        mean_price = self.initial_price
        
        log_current = math.log(self.current_price)
        log_mean = math.log(mean_price)
        
        random_shock = random.gauss(0, 1)
        
        log_change = (
            reversion_speed * (log_mean - log_current) * dt +
            self.current_volatility * math.sqrt(dt) * random_shock
        )
        
        new_log_price = log_current + log_change
        return math.exp(new_log_price)
    
    def _trending_movement(self, dt: float) -> float:
        """Trending price movement with directional bias."""
        enhanced_drift = self.drift * 5  # Stronger trend
        
        random_shock = random.gauss(0, 1)
        
        price_change = (
            enhanced_drift * self.current_price * dt +
            self.current_volatility * self.current_price * math.sqrt(dt) * random_shock
        )
        
        new_price = self.current_price + price_change
        return max(new_price, 0.01)
    
    def _jump_diffusion_movement(self, dt: float) -> float:
        """Jump-diffusion model for flash crash scenarios."""
        # Standard GBM component
        random_shock = random.gauss(0, 1)
        diffusion_change = (
            self.drift * self.current_price * dt +
            self.current_volatility * self.current_price * math.sqrt(dt) * random_shock
        )
        
        # Jump component
        jump_probability = 0.01 * dt  # 1% daily jump probability
        if random.random() < jump_probability:
            jump_size = random.gauss(-0.05, 0.02)  # Negative jumps (crashes)
            jump_change = self.current_price * (math.exp(jump_size) - 1)
        else:
            jump_change = 0
        
        new_price = self.current_price + diffusion_change + jump_change
        return max(new_price, 0.01)
    
    def _generate_volume(self) -> float:
        """Generate realistic trading volume."""
        current_hour = (int(time.time()) // 3600) % 24
        
        # Time-of-day multiplier
        if 9 <= current_hour <= 16:  # Market hours
            time_multiplier = 1.5
        elif 0 <= current_hour <= 6:  # Overnight
            time_multiplier = 0.3
        else:  # Pre/post market
            time_multiplier = 0.8
        
        # Volatility effect (higher volatility = higher volume)
        volatility_multiplier = 1 + 2 * self.current_volatility
        
        # Price movement effect
        if self.price_history:
            price_change = abs(self.current_price - self.price_history[-1].price) / self.current_price
            movement_multiplier = 1 + 5 * price_change
        else:
            movement_multiplier = 1.0
        
        # Random component
        random_multiplier = random.uniform(0.7, 1.3)
        
        # Process volume spikes
        spike_multiplier = self._process_volume_spikes()
        
        total_volume = (
            self.base_volume *
            time_multiplier *
            volatility_multiplier *
            movement_multiplier *
            random_multiplier *
            spike_multiplier *
            self.volume_multiplier
        )
        
        return max(total_volume, 1000)  # Minimum volume floor
    
    def _update_volatility(self, new_price: float):
        """Update current volatility using EWMA."""
        if not self.price_history:
            return
        
        # Calculate return
        last_price = self.price_history[-1].price
        if last_price > 0:
            return_val = (new_price - last_price) / last_price
            
            # EWMA volatility update
            alpha = 0.1  # Smoothing factor
            self.current_volatility = (
                alpha * abs(return_val) +
                (1 - alpha) * self.current_volatility
            )
    
    def _update_volatility_regime(self):
        """Update volatility regime classification."""
        if self.current_volatility < 0.01:  # < 1%
            self.volatility_regime = VolatilityRegime.LOW
        elif self.current_volatility < 0.05:  # < 5%
            self.volatility_regime = VolatilityRegime.MEDIUM
        else:
            self.volatility_regime = VolatilityRegime.HIGH
    
    def _add_price_point(self, price: float, volume: float, volatility: float):
        """Add new price point to history."""
        point = PricePoint(
            price=price,
            volume=volume,
            timestamp=int(time.time()),
            volatility=volatility
        )
        
        self.price_history.append(point)
        
        # Maintain history size limit
        if len(self.price_history) > self.max_history_size:
            self.price_history.pop(0)
    
    def _process_price_shocks(self):
        """Process any pending price shocks."""
        current_time = time.time()
        active_shocks = []
        
        for shock in self.pending_shocks:
            shock_time, magnitude, duration = shock
            if current_time < shock_time + duration:
                # Apply shock effect
                shock_factor = 1.0 + magnitude * math.exp(-(current_time - shock_time) / duration)
                self.current_price *= shock_factor
                active_shocks.append(shock)
        
        self.pending_shocks = active_shocks
    
    def _process_volume_spikes(self) -> float:
        """Process any pending volume spikes."""
        current_time = time.time()
        active_spikes = []
        spike_multiplier = 1.0
        
        for spike in self.pending_volume_spikes:
            spike_time, multiplier, duration = spike
            if current_time < spike_time + duration:
                # Apply volume spike
                decay = math.exp(-(current_time - spike_time) / duration)
                spike_multiplier *= (1.0 + (multiplier - 1.0) * decay)
                active_spikes.append(spike)
        
        self.pending_volume_spikes = active_spikes
        return spike_multiplier
    
    # Public API methods
    
    def get_current_price(self) -> float:
        """Get the current simulated market price."""
        return self.current_price
    
    def get_current_volatility(self) -> float:
        """Get current simulated volatility."""
        return self.current_volatility
    
    def get_price_history(self, window: int = 100) -> List[Tuple[float, float, int]]:
        """Get recent price history."""
        recent_history = self.price_history[-window:] if window else self.price_history
        return [(p.price, p.volume, p.timestamp) for p in recent_history]
    
    def set_scenario(self, scenario: str):
        """Set market scenario."""
        try:
            self.current_scenario = MarketScenario(scenario)
        except ValueError:
            self.current_scenario = MarketScenario.NORMAL
    
    def set_volatility_regime(self, regime: str):
        """Set volatility regime."""
        try:
            target_regime = VolatilityRegime(regime)
            if target_regime == VolatilityRegime.LOW:
                self.current_volatility = 0.005
            elif target_regime == VolatilityRegime.MEDIUM:
                self.current_volatility = 0.02
            else:  # HIGH
                self.current_volatility = 0.08
                
            self.volatility_regime = target_regime
        except ValueError:
            pass
    
    def add_price_shock(self, magnitude: float, duration: int = 60):
        """Add a temporary price shock to the simulation."""
        shock_time = time.time()
        self.pending_shocks.append((shock_time, magnitude, duration))
    
    def add_volume_spike(self, multiplier: float, duration: int):
        """Add temporary volume spike."""
        spike_time = time.time()
        self.pending_volume_spikes.append((spike_time, multiplier, duration))
    
    def set_volume_profile(self, profile: str):
        """Set trading volume profile."""
        profiles = {
            "light": 0.5,
            "normal": 1.0,
            "heavy": 2.0,
            "whale_activity": 5.0
        }
        self.volume_multiplier = profiles.get(profile, 1.0)
    
    def simulate_trade(self, size: float, direction: str = "buy") -> Tuple[float, float]:
        """Simulate a trade and its price impact."""
        # Simple price impact model
        impact_factor = min(size / (self.base_volume * 0.1), 0.05)  # Max 5% impact
        
        if direction == "buy":
            execution_price = self.current_price * (1 + impact_factor)
        else:
            execution_price = self.current_price * (1 - impact_factor)
        
        slippage = abs(execution_price - self.current_price) / self.current_price
        
        return execution_price, slippage
    
    def get_metrics(self) -> Dict[str, float]:
        """Get simulation performance metrics."""
        if len(self.price_history) < 2:
            return {}
        
        prices = [p.price for p in self.price_history]
        volumes = [p.volume for p in self.price_history]
        
        # Calculate realized volatility
        returns = []
        for i in range(1, len(prices)):
            ret = math.log(prices[i] / prices[i-1])
            returns.append(ret)
        
        realized_vol = math.sqrt(sum(r**2 for r in returns) / len(returns)) * math.sqrt(252)
        
        # Calculate max drawdown
        peak = prices[0]
        max_drawdown = 0.0
        
        for price in prices:
            if price > peak:
                peak = price
            else:
                drawdown = (peak - price) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        # Volume-weighted price
        total_volume = sum(volumes)
        if total_volume > 0:
            vwap = sum(p * v for p, v in zip(prices, volumes)) / total_volume
        else:
            vwap = sum(prices) / len(prices)
        
        return {
            "realized_volatility": realized_vol,
            "max_drawdown": max_drawdown,
            "volume_weighted_price": vwap,
            "current_volatility": self.current_volatility,
            "total_trades": self.total_trades,
            "uptime_seconds": time.time() - self.start_time,
            "scenario": self.current_scenario.value,
            "regime": self.volatility_regime.value
        }
