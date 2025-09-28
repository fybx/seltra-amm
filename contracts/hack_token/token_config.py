"""
HACK Token Configuration
Configuration for the HACK ASA token based on algo-hack-token-spec.md
"""

from typing import Dict, Any

# HACK Token Specifications from algo-hack-token-spec.md
HACK_TOKEN_SPEC = {
    "name": "HACK",
    "unit_name": "HACK", 
    "decimals": 6,  # Match ALGO's decimals for easier calculations
    "total_supply": 1_000_000_000_000,  # 1M HACK tokens (in microunits)
    "default_frozen": False,
    "url": "https://seltra-amm.com/hack-token",
    "metadata": {
        "description": "Hackathon demonstration token for Seltra AMM",
        "external_url": "https://github.com/seltra-amm",
        "created_for": "Algorand Hackathon Demo"
    },
    # Management addresses (to be set during minting)
    "manager": "",    # Can modify token properties
    "reserve": "",    # Can mint/burn tokens
    "freeze": "",     # Can freeze accounts  
    "clawback": ""    # Can clawback tokens
}

# ALGO-HACK Pool Configuration
ALGO_HACK_POOL_CONFIG = {
    "asset_x": 0,  # ALGO (always first)
    "asset_y": None,  # HACK token ID (set after minting)
    "initial_price": 1_000_000,  # 1 HACK = 1 ALGO (fixed point, 1e6 scale)
    "initial_liquidity": {
        "algo_amount": 50_000_000_000,  # 50K ALGO (50M microAlgos)
        "hack_amount": 50_000_000_000,  # 50K HACK (50M microHACK)
    },
    "fee_tier": "medium",  # 0.30% base fee
    "range_configuration": {
        "initial_ranges": 3,
        "price_range_percent": 10,  # ±10% around current price
        "concentration_factor": 1.0
    }
}

# Demo-Specific Parameters
DEMO_PARAMETERS = {
    # Price bounds for demo safety
    "min_price": 500_000,   # 0.5 HACK per ALGO (50% down)
    "max_price": 2_000_000, # 2.0 HACK per ALGO (100% up)
    
    # Trading limits
    "max_trade_size_algo": 5_000_000_000,  # 5K ALGO max per trade
    "min_trade_size_algo": 1_000_000,      # 1 ALGO minimum per trade
    
    # Volatility targeting for demo
    "target_volatility": 0.03,  # 3% daily volatility
    "max_volatility": 0.10,     # 10% maximum volatility
    
    # Rebalancing sensitivity
    "rebalance_threshold": 0.02,  # 2% volatility change triggers rebalance
    "min_rebalance_interval": 60  # 1 minute minimum between rebalances
}

# Token Distribution Strategy
HACK_DISTRIBUTION = {
    # Pool liquidity
    "amm_pool": {
        "amount": 100_000_000_000,  # 100K HACK tokens
        "percentage": 10.0
    },
    
    # Demo trading wallets
    "demo_wallets": {
        "amount": 500_000_000_000,  # 500K HACK tokens  
        "percentage": 50.0,
        "wallet_allocation": {
            "retail_wallets": 300_000_000_000,  # 300K HACK (15 wallets)
            "whale_wallets": 200_000_000_000     # 200K HACK (5 wallets)
        }
    },
    
    # Reserve for additional demos
    "reserve": {
        "amount": 400_000_000_000,  # 400K HACK tokens
        "percentage": 40.0,
        "purpose": "Additional liquidity and future demos"
    }
}

# Wallet Funding Strategy
WALLET_FUNDING = {
    "retail_traders": {
        "count": 15,
        "algo_balance": 1_000_000_000,    # 1K ALGO each
        "hack_balance": 20_000_000_000,   # 20K HACK each
        "trading_style": "frequent_small"
    },
    
    "whale_traders": {
        "count": 5, 
        "algo_balance": 10_000_000_000,   # 10K ALGO each
        "hack_balance": 40_000_000_000,   # 40K HACK each
        "trading_style": "infrequent_large"
    }
}


def get_hack_token_config() -> Dict[str, Any]:
    """Get HACK token configuration for ASA creation"""
    return HACK_TOKEN_SPEC.copy()


def get_pool_config() -> Dict[str, Any]:
    """Get ALGO-HACK pool configuration"""
    return ALGO_HACK_POOL_CONFIG.copy()


def get_demo_parameters() -> Dict[str, Any]:
    """Get demo-specific parameters"""
    return DEMO_PARAMETERS.copy()


def get_distribution_config() -> Dict[str, Any]:
    """Get token distribution strategy"""
    return HACK_DISTRIBUTION.copy()


def get_wallet_funding_config() -> Dict[str, Any]:
    """Get wallet funding strategy"""
    return WALLET_FUNDING.copy()
