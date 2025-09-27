"""
ALGO-HACK Demo Configuration

Specialized configuration for ALGO-HACK trading pair demonstration.
Optimized for hackathon presentation with realistic crypto market behavior.
"""

from typing import Dict, Any

# ALGO-HACK Token Configuration
ALGO_HACK_TOKENS = {
    "ALGO": {
        "id": 0,  # Native token
        "name": "ALGO", 
        "decimals": 6,
        "is_base": True
    },
    "HACK": {
        "id": None,  # Set after token creation
        "name": "HACK",
        "decimals": 6,
        "is_base": False,
        "total_supply": 1_000_000_000_000  # 1M tokens
    }
}

# ALGO-HACK Specific Market Scenarios
ALGO_HACK_SCENARIOS = {
    "algo_hack_stable": {
        "name": "ALGO-HACK Stable Trading",
        "description": "Stable 1:1 parity with low volatility",
        "duration_seconds": 120,
        "market_config": {
            "scenario": "mean_reverting",
            "volatility_regime": "low",
            "initial_price": 1.0,  # 1 HACK = 1 ALGO
            "initial_volatility": 0.015,  # 1.5% volatility
            "mean_reversion_speed": 0.1,
            "drift": 0.0001  # Slight positive drift
        },
        "blockchain_config": {
            "pattern": "normal",
            "num_wallets": 20,
            "whale_ratio": 0.10,
            "base_frequency": 0.8  # transactions per minute per wallet
        },
        "expected_behavior": [
            "Price oscillates around 1:1 parity",
            "Tight liquidity concentration (±5%)",
            "Low fees due to stable conditions", 
            "Efficient capital utilization"
        ]
    },
    
    "algo_hack_volatile": {
        "name": "ALGO-HACK Volatile Trading", 
        "description": "High volatility crypto market simulation",
        "duration_seconds": 180,
        "market_config": {
            "scenario": "jump_diffusion",
            "volatility_regime": "high",
            "initial_price": 1.0,
            "initial_volatility": 0.05,  # 5% volatility
            "jump_intensity": 0.03,  # 3% jump probability per update
            "jump_mean": 0.0,
            "jump_std": 0.04,  # 4% jump magnitude
            "drift": 0.0002
        },
        "blockchain_config": {
            "pattern": "volatile", 
            "num_wallets": 25,
            "whale_ratio": 0.20,
            "base_frequency": 2.5
        },
        "expected_behavior": [
            "Sudden price jumps and volatility spikes",
            "Wide liquidity range deployment",
            "Dynamic fee adjustments",
            "Frequent rebalancing events"
        ]
    },
    
    "hack_token_launch": {
        "name": "HACK Token Launch Simulation",
        "description": "Simulates initial token launch with high interest",
        "duration_seconds": 240,
        "market_config": {
            "scenario": "trending",
            "volatility_regime": "medium", 
            "initial_price": 0.5,  # Launch at 0.5 ALGO per HACK
            "initial_volatility": 0.08,  # 8% launch volatility
            "drift": 0.008,  # Strong upward trend (0.8% per update)
            "trend_strength": 0.7
        },
        "blockchain_config": {
            "pattern": "launch_frenzy",
            "num_wallets": 30,
            "whale_ratio": 0.15,
            "base_frequency": 4.0,
            "burst_probability": 0.4
        },
        "expected_behavior": [
            "Price trend from 0.5 to ~1.2 ALGO per HACK",
            "High trading volume and frequency",
            "Wide price ranges due to uncertainty",
            "Progressive fee reductions as volume increases"
        ]
    },
    
    "algo_hack_crash": {
        "name": "ALGO-HACK Flash Crash",
        "description": "Extreme market stress test",
        "duration_seconds": 90,
        "market_config": {
            "scenario": "flash_crash",
            "volatility_regime": "extreme",
            "initial_price": 1.0,
            "initial_volatility": 0.12,  # 12% extreme volatility
            "jump_intensity": 0.1,  # 10% crash probability
            "jump_mean": -0.15,  # 15% downward jumps
            "jump_std": 0.05
        },
        "blockchain_config": {
            "pattern": "panic_selling",
            "num_wallets": 35,
            "whale_ratio": 0.25,
            "base_frequency": 5.0
        },
        "expected_behavior": [
            "Rapid price decline with recovery attempts",
            "Maximum range expansion for protection",
            "Peak fee rates activated",
            "Stress testing of all systems"
        ]
    }
}

# ALGO-HACK Specific Wallet Profiles  
ALGO_HACK_WALLETS = {
    "algo_retail": {
        "algo_balance_range": (500_000_000, 2_000_000_000),  # 500-2000 ALGO
        "hack_balance_range": (10_000_000_000, 50_000_000_000),  # 10K-50K HACK
        "trade_size_range": (10_000_000, 100_000_000),  # 10-100 ALGO per trade
        "frequency_multiplier": 1.0,
        "risk_tolerance": "conservative"
    },
    
    "algo_whale": {
        "algo_balance_range": (5_000_000_000, 20_000_000_000),  # 5K-20K ALGO
        "hack_balance_range": (50_000_000_000, 200_000_000_000),  # 50K-200K HACK  
        "trade_size_range": (1_000_000_000, 5_000_000_000),  # 1K-5K ALGO per trade
        "frequency_multiplier": 0.3,
        "risk_tolerance": "aggressive"
    },
    
    "arbitrage_bot": {
        "algo_balance_range": (1_000_000_000, 5_000_000_000),  # 1K-5K ALGO
        "hack_balance_range": (20_000_000_000, 100_000_000_000),  # 20K-100K HACK
        "trade_size_range": (50_000_000, 500_000_000),  # 50-500 ALGO per trade
        "frequency_multiplier": 3.0,
        "risk_tolerance": "neutral",
        "behavior": "mean_reverting"  # Profits from price deviations
    }
}

# Trading Patterns for Different Market Conditions
ALGO_HACK_PATTERNS = {
    "normal": {
        "base_frequency": 0.8,  # tx/min/wallet
        "size_variance": 0.3,
        "burst_probability": 0.1,
        "directional_bias": 0.0  # No bias
    },
    
    "volatile": {
        "base_frequency": 2.5,
        "size_variance": 0.7, 
        "burst_probability": 0.3,
        "directional_bias": 0.0
    },
    
    "launch_frenzy": {
        "base_frequency": 4.0,
        "size_variance": 0.9,
        "burst_probability": 0.4,
        "directional_bias": 0.7  # Strong buy bias
    },
    
    "panic_selling": {
        "base_frequency": 5.0,
        "size_variance": 1.2,
        "burst_probability": 0.6,
        "directional_bias": -0.8  # Strong sell bias
    }
}

# ALGO-HACK Specific Parameters
ALGO_HACK_PARAMETERS = {
    # Price configuration
    "initial_price": 1_000_000,  # 1 HACK = 1 ALGO (microunit scale)
    "min_price": 100_000,       # 0.1 ALGO minimum (prevent extreme crashes) 
    "max_price": 10_000_000,    # 10 ALGO maximum (prevent extreme pumps)
    
    # Liquidity configuration
    "initial_algo_liquidity": 50_000_000_000,   # 50K ALGO
    "initial_hack_liquidity": 50_000_000_000,   # 50K HACK
    "min_liquidity_per_range": 1_000_000_000,   # 1K ALGO minimum per range
    
    # Trading limits
    "max_trade_size": 5_000_000_000,    # 5K ALGO max trade
    "min_trade_size": 1_000_000,        # 1 ALGO min trade
    "max_slippage_tolerance": 500,       # 5% max slippage
    
    # Volatility settings
    "volatility_thresholds": {
        "low": 200,     # 2%
        "medium": 500,  # 5%  
        "high": 1000,   # 10%
        "extreme": 2000 # 20%
    },
    
    # Fee settings
    "fee_tiers": {
        "base_fee": 30,        # 0.30%
        "min_fee": 5,          # 0.05%
        "max_fee": 500,        # 5.00%
        "volume_thresholds": [
            50_000_000_000,    # 50K ALGO for tier 1
            500_000_000_000,   # 500K ALGO for tier 2
            5_000_000_000_000  # 5M ALGO for tier 3
        ]
    },
    
    # Rebalancing settings
    "rebalance_threshold": 100,  # 1% volatility change
    "min_rebalance_interval": 60,  # 60 seconds
    "concentration_factors": [5000, 10000, 20000],  # 0.5x, 1.0x, 2.0x
    "range_counts": [2, 3, 5]  # Number of ranges per regime
}

# Demo Presentation Configuration
ALGO_HACK_PRESENTATION = {
    "demo_sequence": [
        {
            "phase": "introduction",
            "scenario": None,
            "duration": 30,
            "talking_points": [
                "ALGO-HACK demonstrates dynamic AMM on Algorand",
                "Real crypto volatility patterns",
                "Adaptive liquidity management",
                "4.5 second finality advantage"
            ]
        },
        {
            "phase": "stable_demo",
            "scenario": "algo_hack_stable", 
            "duration": 120,
            "talking_points": [
                "Starting with stable 1:1 parity",
                "Tight liquidity ranges for efficiency", 
                "Low fees due to predictable conditions",
                "Capital efficiency maximized"
            ]
        },
        {
            "phase": "volatility_demo",
            "scenario": "algo_hack_volatile",
            "duration": 180,
            "talking_points": [
                "Increasing volatility triggers adaptation",
                "Range expansion for protection",
                "Dynamic fee adjustments",
                "Automatic rebalancing in action"
            ]
        },
        {
            "phase": "stress_test",
            "scenario": "algo_hack_crash",
            "duration": 90,
            "talking_points": [
                "Stress testing with flash crash",
                "Emergency protection mechanisms",
                "Maximum range deployment",
                "System resilience demonstration"
            ]
        }
    ],
    
    "key_metrics_to_highlight": [
        "Capital efficiency improvement",
        "Slippage reduction vs static AMM",
        "Fee optimization",
        "Rebalancing frequency and triggers",
        "Transaction throughput"
    ]
}


def get_algo_hack_scenario(scenario_name: str) -> Dict[str, Any]:
    """Get ALGO-HACK specific scenario configuration."""
    if scenario_name not in ALGO_HACK_SCENARIOS:
        raise ValueError(f"Unknown ALGO-HACK scenario: {scenario_name}")
    return ALGO_HACK_SCENARIOS[scenario_name]


def get_wallet_profile(profile_name: str) -> Dict[str, Any]:
    """Get wallet configuration profile."""
    if profile_name not in ALGO_HACK_WALLETS:
        raise ValueError(f"Unknown wallet profile: {profile_name}")
    return ALGO_HACK_WALLETS[profile_name]


def get_trading_pattern(pattern_name: str) -> Dict[str, Any]:
    """Get trading pattern configuration.""" 
    if pattern_name not in ALGO_HACK_PATTERNS:
        raise ValueError(f"Unknown trading pattern: {pattern_name}")
    return ALGO_HACK_PATTERNS[pattern_name]
