"""
HACK Token Package
Provides HACK ASA token deployment and configuration for Algorand hackathon demo.
"""

from .token_config import (
    HACK_TOKEN_SPEC,
    ALGO_HACK_POOL_CONFIG, 
    DEMO_PARAMETERS,
    HACK_DISTRIBUTION,
    WALLET_FUNDING,
    get_hack_token_config,
    get_pool_config,
    get_demo_parameters,
    get_distribution_config,
    get_wallet_funding_config
)

from .deploy_config import HACKTokenDeployer, deploy

__all__ = [
    # Token specifications
    'HACK_TOKEN_SPEC',
    'ALGO_HACK_POOL_CONFIG',
    'DEMO_PARAMETERS',
    'HACK_DISTRIBUTION',
    'WALLET_FUNDING',
    
    # Configuration functions
    'get_hack_token_config',
    'get_pool_config',
    'get_demo_parameters',  
    'get_distribution_config',
    'get_wallet_funding_config',
    
    # Deployment
    'HACKTokenDeployer',
    'deploy'
]
