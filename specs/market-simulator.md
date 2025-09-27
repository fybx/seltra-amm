# MarketSimulator Specification

## Overview

The MarketSimulator provides realistic market conditions for testing and demonstrating the Seltra AMM. It generates price movements, trading volumes, and volatility scenarios to showcase the dynamic liquidity management capabilities.

## Component Interface

### Simulation Control

```python
class MarketSimulator:
    def __init__(
        self,
        initial_price: float,
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

    def start_simulation(self, scenario: str = "normal") -> None:
        """
        Start price simulation with specified scenario.
        
        Args:
            scenario: Market scenario type
                - "normal": Regular market conditions
                - "volatile": High volatility periods
                - "calm": Low volatility periods  
                - "trending": Strong directional movement
                - "mean_reverting": Price oscillation around mean
                - "flash_crash": Sudden large price movement
        """

    def stop_simulation(self) -> None:
        """Stop the current simulation."""

    def reset_simulation(self, new_initial_price: float = None) -> None:
        """Reset simulation to initial state."""
```

### Price Generation

```python
    def get_current_price(self) -> float:
        """Get the current simulated market price."""

    def get_price_history(self, window: int) -> list[tuple[float, float, int]]:
        """
        Get recent price history.
        
        Args:
            window: Number of recent price points to return
            
        Returns:
            List of (price, volume, timestamp) tuples
        """

    def simulate_trade(
        self,
        size: float,
        direction: str = "buy"
    ) -> tuple[float, float]:
        """
        Simulate a trade and its price impact.
        
        Args:
            size: Trade size in base asset
            direction: "buy" or "sell"
            
        Returns:
            (execution_price, slippage)
        """

    def add_price_shock(
        self,
        magnitude: float,
        duration: int = 60
    ) -> None:
        """
        Add a temporary price shock to the simulation.
        
        Args:
            magnitude: Price change magnitude (e.g., 0.1 for 10%)
            duration: Duration of shock effect (seconds)
        """
```

### Volatility Control

```python
    def set_volatility_regime(self, regime: str) -> None:
        """
        Set volatility regime for simulation.
        
        Args:
            regime: "low", "medium", "high", or "extreme"
        """

    def get_current_volatility(self) -> float:
        """Get current simulated volatility."""

    def schedule_volatility_change(
        self,
        target_volatility: float,
        transition_time: int
    ) -> None:
        """
        Schedule a gradual volatility change.
        
        Args:
            target_volatility: Target volatility level
            transition_time: Time to reach target (seconds)
        """
```

### Volume Simulation

```python
    def simulate_trading_volume(self) -> float:
        """Generate realistic trading volume for current conditions."""

    def set_volume_profile(self, profile: str) -> None:
        """
        Set trading volume profile.
        
        Args:
            profile: "light", "normal", "heavy", "whale_activity"
        """

    def add_volume_spike(self, multiplier: float, duration: int) -> None:
        """
        Add temporary volume spike.
        
        Args:
            multiplier: Volume multiplier (e.g., 5.0 for 5x volume)
            duration: Duration of spike (seconds)
        """
```

### Data Export

```python
    def export_simulation_data(self) -> dict:
        """
        Export simulation data for analysis.
        
        Returns:
            Dictionary containing:
            - price_history: List of price points
            - volume_history: List of volume data
            - volatility_history: List of volatility measurements
            - events: List of market events (shocks, regime changes)
            - statistics: Summary statistics
        """

    def get_metrics(self) -> dict[str, float]:
        """
        Get simulation performance metrics.
        
        Returns:
            Dictionary with metrics like:
            - realized_volatility: Actual volatility observed
            - sharpe_ratio: Risk-adjusted return measure
            - max_drawdown: Maximum price decline
            - volume_weighted_price: VWAP over simulation period
        """
```

## Mathematical Models

### Price Movement Models

```python
class GeometricBrownianMotion:
    """
    Standard GBM model for price simulation.
    
    Formula: dS = μ * S * dt + σ * S * dW
    Where:
    - S: Current price
    - μ: Drift (expected return)
    - σ: Volatility (standard deviation)
    - dW: Wiener process (random walk)
    """
    
    def __init__(self, drift: float, volatility: float):
        self.drift = drift
        self.volatility = volatility
        
    def next_price(self, current_price: float, dt: float) -> float:
        """Generate next price using GBM."""
        random_shock = np.random.normal(0, 1)
        
        price_change = (
            self.drift * current_price * dt +
            self.volatility * current_price * math.sqrt(dt) * random_shock
        )
        
        return max(current_price + price_change, 0.01)  # Prevent negative prices

class JumpDiffusionModel:
    """
    Merton jump-diffusion model for extreme price movements.
    
    Adds jump component to GBM:
    dS = μ * S * dt + σ * S * dW + S * (e^Y - 1) * dN
    Where:
    - Y: Jump size (normally distributed)
    - dN: Poisson process for jump timing
    """
    
    def __init__(
        self,
        drift: float,
        volatility: float,
        jump_intensity: float,
        jump_mean: float,
        jump_std: float
    ):
        self.drift = drift
        self.volatility = volatility
        self.jump_intensity = jump_intensity  # Average jumps per unit time
        self.jump_mean = jump_mean           # Average jump size
        self.jump_std = jump_std             # Jump size volatility
        
    def next_price(self, current_price: float, dt: float) -> float:
        """Generate next price with potential jumps."""
        # Standard GBM component
        random_shock = np.random.normal(0, 1)
        diffusion_change = (
            self.drift * current_price * dt +
            self.volatility * current_price * math.sqrt(dt) * random_shock
        )
        
        # Jump component
        jump_probability = self.jump_intensity * dt
        if np.random.random() < jump_probability:
            jump_size = np.random.normal(self.jump_mean, self.jump_std)
            jump_change = current_price * (math.exp(jump_size) - 1)
        else:
            jump_change = 0
        
        new_price = current_price + diffusion_change + jump_change
        return max(new_price, 0.01)

class MeanRevertingModel:
    """
    Ornstein-Uhlenbeck process for mean-reverting prices.
    
    Formula: dx = θ(μ - x)dt + σ dW
    Where:
    - θ: Mean reversion speed
    - μ: Long-term mean
    - x: Current value (log price)
    """
    
    def __init__(
        self,
        mean_price: float,
        reversion_speed: float,
        volatility: float
    ):
        self.mean_price = mean_price
        self.reversion_speed = reversion_speed
        self.volatility = volatility
        
    def next_price(self, current_price: float, dt: float) -> float:
        """Generate mean-reverting price movement."""
        log_current = math.log(current_price)
        log_mean = math.log(self.mean_price)
        
        random_shock = np.random.normal(0, 1)
        
        log_change = (
            self.reversion_speed * (log_mean - log_current) * dt +
            self.volatility * math.sqrt(dt) * random_shock
        )
        
        new_log_price = log_current + log_change
        return math.exp(new_log_price)
```

### Volatility Models

```python
class GARCHVolatility:
    """
    GARCH(1,1) model for dynamic volatility.
    
    Formula: σ²(t) = α₀ + α₁ * ε²(t-1) + β₁ * σ²(t-1)
    Where:
    - α₀: Base volatility
    - α₁: Reaction to recent shocks
    - β₁: Persistence of volatility
    """
    
    def __init__(
        self,
        alpha0: float = 0.00001,  # Base volatility
        alpha1: float = 0.1,      # Shock reaction
        beta1: float = 0.85       # Persistence
    ):
        self.alpha0 = alpha0
        self.alpha1 = alpha1
        self.beta1 = beta1
        self.last_volatility_squared = alpha0
        self.last_shock_squared = 0
        
    def update_volatility(self, price_return: float) -> float:
        """Update volatility based on recent price return."""
        # Calculate current shock
        shock_squared = price_return ** 2
        
        # Update volatility using GARCH formula
        new_volatility_squared = (
            self.alpha0 +
            self.alpha1 * self.last_shock_squared +
            self.beta1 * self.last_volatility_squared
        )
        
        # Update state
        self.last_volatility_squared = new_volatility_squared
        self.last_shock_squared = shock_squared
        
        return math.sqrt(new_volatility_squared)

class RegimeSwitchingVolatility:
    """
    Markov regime-switching volatility model.
    
    Two states: High and Low volatility with transition probabilities.
    """
    
    def __init__(
        self,
        low_vol: float = 0.01,
        high_vol: float = 0.05,
        prob_low_to_high: float = 0.02,
        prob_high_to_low: float = 0.1
    ):
        self.low_vol = low_vol
        self.high_vol = high_vol
        self.prob_low_to_high = prob_low_to_high
        self.prob_high_to_low = prob_high_to_low
        self.current_regime = "low"  # Start in low volatility
        
    def update_regime(self) -> str:
        """Update volatility regime based on transition probabilities."""
        random_value = np.random.random()
        
        if self.current_regime == "low":
            if random_value < self.prob_low_to_high:
                self.current_regime = "high"
        else:  # high volatility regime
            if random_value < self.prob_high_to_low:
                self.current_regime = "low"
                
        return self.current_regime
        
    def get_current_volatility(self) -> float:
        """Get volatility for current regime."""
        return self.high_vol if self.current_regime == "high" else self.low_vol
```

### Volume Generation

```python
class VolumeGenerator:
    """Generate realistic trading volume patterns."""
    
    def __init__(self, base_volume: float = 100000):
        self.base_volume = base_volume
        self.time_of_day_multipliers = self._create_time_multipliers()
        
    def _create_time_multipliers(self) -> list[float]:
        """Create hourly volume multipliers based on typical trading patterns."""
        # Higher volume during market open/close hours
        multipliers = []
        for hour in range(24):
            if 9 <= hour <= 16:  # Market hours
                base_mult = 1.5
            elif 0 <= hour <= 6:  # Overnight
                base_mult = 0.3
            else:  # Pre/post market
                base_mult = 0.8
                
            # Add some randomness
            multiplier = base_mult * (0.8 + 0.4 * np.random.random())
            multipliers.append(multiplier)
            
        return multipliers
        
    def generate_volume(
        self,
        current_hour: int,
        volatility: float,
        price_change: float
    ) -> float:
        """
        Generate trading volume based on time and market conditions.
        
        Args:
            current_hour: Hour of day (0-23)
            volatility: Current market volatility
            price_change: Recent price change magnitude
            
        Returns:
            Simulated trading volume
        """
        # Base time-of-day effect
        time_multiplier = self.time_of_day_multipliers[current_hour]
        
        # Volatility effect (higher volatility = higher volume)
        volatility_multiplier = 1 + 2 * volatility
        
        # Price movement effect (large moves attract volume)
        movement_multiplier = 1 + 5 * abs(price_change)
        
        # Random component
        random_multiplier = 0.7 + 0.6 * np.random.random()
        
        total_volume = (
            self.base_volume *
            time_multiplier *
            volatility_multiplier *
            movement_multiplier *
            random_multiplier
        )
        
        return max(total_volume, 1000)  # Minimum volume floor

class AlgoHackVolumeGenerator(VolumeGenerator):
    """Specialized volume generator for ALGO-HACK trading pair."""
    
    def __init__(self, base_volume: float = 50000):  # Lower base for crypto
        super().__init__(base_volume)
        self.crypto_multipliers = self._create_crypto_multipliers()
        
    def _create_crypto_multipliers(self) -> dict:
        """Create crypto-specific volume patterns."""
        return {
            "stable": 0.8,      # Lower volume during stable periods
            "volatile": 2.5,    # High volume during volatility  
            "launch": 5.0,      # Extreme volume during token launch
            "crash": 3.0,       # Panic trading volume
            "weekend": 0.4      # Reduced weekend crypto trading
        }
        
    def generate_algo_hack_volume(
        self,
        market_condition: str,
        price_volatility: float,
        time_factor: float = 1.0
    ) -> float:
        """Generate volume specific to ALGO-HACK conditions."""
        base = self.base_volume * time_factor
        condition_multiplier = self.crypto_multipliers.get(market_condition, 1.0)
        volatility_multiplier = 1 + (price_volatility * 8)  # Crypto vol correlation
        
        return base * condition_multiplier * volatility_multiplier
```

## Scenario Definitions

### Pre-defined Scenarios

```python
class MarketScenarios:
    """Pre-defined market scenarios for demonstrations."""
    
    SCENARIOS = {
        "normal": {
            "model": "gbm",
            "drift": 0.0001,
            "volatility": 0.02,
            "regime_switching": False,
            "jumps": False,
            "description": "Normal market conditions with moderate volatility"
        },
        
        "volatile": {
            "model": "garch",
            "base_volatility": 0.05,
            "regime_switching": True,
            "high_vol_probability": 0.3,
            "jumps": True,
            "jump_intensity": 0.1,
            "description": "High volatility with regime switching"
        },
        
        "calm": {
            "model": "mean_reverting",
            "volatility": 0.005,
            "reversion_speed": 0.1,
            "mean_price": None,  # Use current price
            "description": "Low volatility mean-reverting market"
        },
        
        "trending": {
            "model": "gbm", 
            "drift": 0.001,  # Strong upward trend
            "volatility": 0.015,
            "regime_switching": False,
            "description": "Strong trending market with directional bias"
        },
        
        "flash_crash": {
            "model": "jump_diffusion",
            "volatility": 0.02,
            "jump_intensity": 0.05,
            "jump_mean": -0.1,  # Negative jumps (crashes)
            "jump_std": 0.02,
            "description": "Market with potential flash crash events"
        },
        
        "whale_activity": {
            "model": "gbm",
            "volatility": 0.03,
            "volume_spikes": True,
            "spike_frequency": 0.02,
            "spike_magnitude": 10.0,
            "description": "Large trader activity causing volume spikes"
        },
        
        # ALGO-HACK Specific Scenarios
        "algo_hack_stable": {
            "model": "mean_reverting",
            "mean_price": None,  # Use current price
            "reversion_speed": 0.1,
            "volatility": 0.015,
            "drift": 0.0001,
            "description": "Stable ALGO-HACK parity with mean reversion"
        },
        
        "algo_hack_volatile": {
            "model": "jump_diffusion",
            "volatility": 0.05,
            "jump_intensity": 0.03,
            "jump_mean": 0.0,
            "jump_std": 0.04,
            "drift": 0.0002,
            "description": "High volatility ALGO-HACK with crypto-style jumps"
        },
        
        "hack_token_launch": {
            "model": "trending",
            "drift": 0.008,
            "volatility": 0.08,
            "volume_multiplier": 4.0,
            "launch_dynamics": True,
            "description": "HACK token launch with strong upward trend"
        },
        
        "algo_hack_crash": {
            "model": "jump_diffusion",
            "volatility": 0.12,
            "jump_intensity": 0.1,
            "jump_mean": -0.15,
            "jump_std": 0.05,
            "drift": -0.002,
            "description": "Flash crash scenario with large downward movements"
        }
    }
    
    @classmethod
    def get_scenario_config(cls, scenario_name: str) -> dict:
        """Get configuration for named scenario."""
        return cls.SCENARIOS.get(scenario_name, cls.SCENARIOS["normal"])
```

## Performance Metrics

```python
class SimulationMetrics:
    """Calculate performance metrics for simulation analysis."""
    
    @staticmethod
    def calculate_realized_volatility(price_history: list[float]) -> float:
        """Calculate realized volatility from price history."""
        if len(price_history) < 2:
            return 0.0
            
        returns = []
        for i in range(1, len(price_history)):
            ret = math.log(price_history[i] / price_history[i-1])
            returns.append(ret)
            
        if not returns:
            return 0.0
            
        variance = np.var(returns)
        return math.sqrt(variance * 252 * 24 * 3600)  # Annualized
    
    @staticmethod
    def calculate_max_drawdown(price_history: list[float]) -> float:
        """Calculate maximum drawdown during simulation."""
        if len(price_history) < 2:
            return 0.0
            
        peak = price_history[0]
        max_drawdown = 0.0
        
        for price in price_history:
            if price > peak:
                peak = price
            else:
                drawdown = (peak - price) / peak
                max_drawdown = max(max_drawdown, drawdown)
                
        return max_drawdown
    
    @staticmethod
    def calculate_volume_weighted_price(
        price_history: list[float],
        volume_history: list[float]
    ) -> float:
        """Calculate volume-weighted average price."""
        if len(price_history) != len(volume_history) or not price_history:
            return 0.0
            
        total_volume = sum(volume_history)
        if total_volume == 0:
            return sum(price_history) / len(price_history)
            
        weighted_sum = sum(p * v for p, v in zip(price_history, volume_history))
        return weighted_sum / total_volume
```

## Event System

```python
class SimulationEvent:
    """Base class for simulation events."""
    
    def __init__(self, timestamp: int, event_type: str):
        self.timestamp = timestamp
        self.event_type = event_type

class VolatilityRegimeChange(SimulationEvent):
    """Event for volatility regime changes."""
    
    def __init__(self, timestamp: int, old_regime: str, new_regime: str):
        super().__init__(timestamp, "volatility_regime_change")
        self.old_regime = old_regime
        self.new_regime = new_regime

class PriceShock(SimulationEvent):
    """Event for sudden price movements."""
    
    def __init__(self, timestamp: int, magnitude: float, duration: int):
        super().__init__(timestamp, "price_shock")
        self.magnitude = magnitude
        self.duration = duration

class VolumeSpike(SimulationEvent):
    """Event for volume spikes."""
    
    def __init__(self, timestamp: int, multiplier: float, duration: int):
        super().__init__(timestamp, "volume_spike")
        self.multiplier = multiplier
        self.duration = duration
```

## Configuration Constants

```python
# Default Parameters
DEFAULT_INITIAL_PRICE = 100.0
DEFAULT_VOLATILITY = 0.02
DEFAULT_TICK_INTERVAL = 1.0
DEFAULT_BASE_VOLUME = 100000

# Model Parameters
GBM_DEFAULT_DRIFT = 0.0001
GARCH_ALPHA0 = 0.00001
GARCH_ALPHA1 = 0.1
GARCH_BETA1 = 0.85

# Regime Switching
LOW_VOL_REGIME = 0.01
HIGH_VOL_REGIME = 0.05
REGIME_TRANSITION_PROB = 0.02

# Jump Parameters
DEFAULT_JUMP_INTENSITY = 0.01
DEFAULT_JUMP_MEAN = 0.0
DEFAULT_JUMP_STD = 0.02

# Volume Parameters
MIN_VOLUME = 1000
MAX_VOLUME_MULTIPLIER = 20
VOLUME_SHOCK_FREQUENCY = 0.01
```

---

This specification defines a comprehensive market simulation system that provides realistic testing conditions for the Seltra AMM, enabling demonstration of dynamic liquidity management under various market scenarios.
