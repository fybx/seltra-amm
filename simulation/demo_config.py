"""
Demo Configuration for Seltra Simulation

Predefined scenarios and configurations for demonstrating the Seltra AMM
simulation capabilities during hackathon presentations.
"""

from typing import Dict, Any


# Demo Scenarios Configuration
DEMO_SCENARIOS = {
    "calm_trading": {
        "name": "Calm Market - Optimal Liquidity Concentration",
        "description": "Demonstrates tight liquidity concentration during stable market conditions",
        "duration_seconds": 120,
        "market_config": {
            "scenario": "calm",
            "volatility_regime": "low",
            "initial_volatility": 0.005  # 0.5% volatility
        },
        "blockchain_config": {
            "pattern": "normal",
            "num_wallets": 15,
            "whale_ratio": 0.05  # 5% whales for minimal impact
        },
        "expected_behavior": [
            "Low volatility triggers tight liquidity ranges",
            "Frequent small trades from retail traders",
            "Minimal slippage on standard trades",
            "High capital efficiency"
        ]
    },
    
    "volatility_spike": {
        "name": "Volatility Spike - Dynamic Range Expansion", 
        "description": "Shows how the system adapts to sudden volatility increases",
        "duration_seconds": 180,
        "market_config": {
            "scenario": "volatile",
            "volatility_regime": "high", 
            "initial_volatility": 0.08  # 8% volatility
        },
        "blockchain_config": {
            "pattern": "volatile",
            "num_wallets": 25,
            "whale_ratio": 0.15  # 15% whales for more impact
        },
        "expected_behavior": [
            "High volatility triggers range expansion",
            "Increased trading frequency",
            "Larger trade sizes",
            "Adaptive fee increases"
        ]
    },
    
    "whale_activity": {
        "name": "Whale Trading - Large Transaction Handling",
        "description": "Demonstrates how the system handles large trades from whale accounts",
        "duration_seconds": 150,
        "market_config": {
            "scenario": "normal",
            "volatility_regime": "medium",
            "initial_volatility": 0.02  # 2% volatility  
        },
        "blockchain_config": {
            "pattern": "normal",
            "num_wallets": 20,
            "whale_ratio": 0.25  # 25% whales for significant impact
        },
        "expected_behavior": [
            "Large trades cause temporary price impact",
            "System rebalances liquidity ranges",
            "Volatility increases temporarily",
            "Liquidity concentration adjusts"
        ]
    },
    
    "flash_crash": {
        "name": "Flash Crash - Emergency Response",
        "description": "Tests system response to extreme market events",
        "duration_seconds": 90,
        "market_config": {
            "scenario": "flash_crash",
            "volatility_regime": "high",
            "initial_volatility": 0.12  # 12% volatility
        },
        "blockchain_config": {
            "pattern": "volatile", 
            "num_wallets": 30,
            "whale_ratio": 0.20  # 20% whales
        },
        "expected_behavior": [
            "Jump-diffusion price movements",
            "Wide liquidity range deployment",
            "Maximum fee structures activated",
            "Capital protection measures"
        ]
    },
    
    "recovery_phase": {
        "name": "Market Recovery - Gradual Normalization",
        "description": "Shows liquidity reconcentration as markets stabilize",
        "duration_seconds": 200,
        "market_config": {
            "scenario": "mean_reverting", 
            "volatility_regime": "medium",
            "initial_volatility": 0.03  # 3% volatility
        },
        "blockchain_config": {
            "pattern": "normal",
            "num_wallets": 18,
            "whale_ratio": 0.10  # 10% whales
        },
        "expected_behavior": [
            "Mean-reverting price behavior",
            "Gradual range tightening",
            "Fee normalization",
            "Trading frequency reduction"
        ]
    }
}


# Wallet Distribution Profiles
WALLET_PROFILES = {
    "conservative": {
        "whale_ratio": 0.05,
        "avg_whale_size": 5000,  # ALGO
        "avg_retail_size": 50,   # ALGO
        "trade_frequency_multiplier": 0.7
    },
    "balanced": {
        "whale_ratio": 0.15,
        "avg_whale_size": 2000,  # ALGO
        "avg_retail_size": 100,  # ALGO  
        "trade_frequency_multiplier": 1.0
    },
    "aggressive": {
        "whale_ratio": 0.25,
        "avg_whale_size": 1000,  # ALGO
        "avg_retail_size": 150,  # ALGO
        "trade_frequency_multiplier": 1.5
    }
}


# Demo Presentation Script
PRESENTATION_SCRIPT = {
    "introduction": {
        "duration": 30,
        "talking_points": [
            "Traditional AMMs waste capital with static liquidity distribution",
            "Seltra AMM adapts liquidity concentration based on market volatility",
            "Real-time simulation on Algorand blockchain",
            "Demonstrating volatile vs normal market conditions"
        ]
    },
    
    "demo_1_calm": {
        "scenario": "calm_trading",
        "duration": 120,
        "talking_points": [
            "Starting with calm market conditions",
            "Notice tight liquidity concentration around current price",
            "Small trades execute with minimal slippage",
            "Capital efficiency maximized for stable conditions"
        ],
        "key_metrics": [
            "Slippage < 0.1%",
            "Range concentration factor: 0.5x",
            "Trading frequency: 0.5 tx/min/wallet"
        ]
    },
    
    "demo_2_volatility": {
        "scenario": "volatility_spike", 
        "duration": 180,
        "talking_points": [
            "Triggering volatility spike...",
            "Watch liquidity ranges expand automatically",
            "Trading frequency increases with market uncertainty",
            "System protects against impermanent loss"
        ],
        "key_metrics": [
            "Range concentration factor: 2.0x",
            "Trading frequency: 2.0 tx/min/wallet",
            "Fee adjustments: 0.05% → 0.30%"
        ]
    },
    
    "comparison": {
        "duration": 60,
        "talking_points": [
            "Comparison vs static AMM:",
            "3-5x better capital efficiency",
            "Adaptive slippage protection", 
            "Dynamic fee optimization",
            "Real-time market response"
        ]
    },
    
    "conclusion": {
        "duration": 30,
        "talking_points": [
            "Seltra AMM: Intelligence meets liquidity",
            "Built on Algorand for 4.5s finality",
            "Ready for mainnet deployment",
            "The future of automated market making"
        ]
    }
}


def get_scenario_config(scenario_name: str) -> Dict[str, Any]:
    """Get configuration for a specific demo scenario."""
    if scenario_name not in DEMO_SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")
    
    return DEMO_SCENARIOS[scenario_name]


def get_all_scenarios() -> Dict[str, Dict[str, Any]]:
    """Get all available demo scenarios."""
    return DEMO_SCENARIOS


def get_presentation_script() -> Dict[str, Any]:
    """Get the demo presentation script with timing and talking points."""
    return PRESENTATION_SCRIPT


# Demo Parameters for Different Audience Types
AUDIENCE_CONFIGS = {
    "technical": {
        "show_metrics": True,
        "detailed_explanations": True,
        "code_snippets": True,
        "performance_comparisons": True
    },
    "business": {
        "show_metrics": False,
        "detailed_explanations": False,
        "code_snippets": False,
        "performance_comparisons": True,
        "focus_on_value": True
    },
    "judges": {
        "show_metrics": True,
        "detailed_explanations": True,
        "code_snippets": False,
        "performance_comparisons": True,
        "innovation_highlights": True
    }
}
