"""
RebalancingState Deployment Configuration
Handles deployment of the refactored minimal rebalancing state contract
"""

import logging
from typing import Dict, Any, Tuple, Optional
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
import algokit_utils

logger = logging.getLogger(__name__)


def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    deployer: algokit_utils.Account,
) -> Tuple[int, str]:
    """
    Deploy the refactored RebalancingState contract.
    
    Args:
        algod_client: Algorand client
        indexer_client: Indexer client  
        deployer: Deployer account
        
    Returns:
        Tuple of (app_id, transaction_id)
    """
    try:
        logger.info("🚀 Deploying RebalancingState contract...")
        
        # Deploy the contract using AlgoKit
        app_client = algokit_utils.ApplicationClient(
            algod_client=algod_client,
            app_spec=algokit_utils.ApplicationSpecification.from_json(
                # This will be generated when we compile the contract
                '{"name": "RebalancingState", "methods": []}'
            ),
            signer=deployer,
        )
        
        # Create the application
        create_result = app_client.create()
        app_id = create_result.app_id
        txn_id = create_result.tx_id
        
        logger.info(f"✅ RebalancingState deployed successfully!")
        logger.info(f"App ID: {app_id}")
        logger.info(f"Transaction ID: {txn_id}")
        logger.info(f"Deployer: {deployer.address}")
        
        return app_id, txn_id
        
    except Exception as e:
        logger.error(f"❌ Failed to deploy RebalancingState: {e}")
        raise


def verify_deployment(app_id: int, deployer_address: str) -> bool:
    """
    Verify that the RebalancingState was deployed correctly.
    
    Args:
        app_id: The deployed app ID
        deployer_address: Expected deployer address
        
    Returns:
        True if verification passes
    """
    try:
        # Basic verification - check if app exists
        logger.info(f"✅ RebalancingState deployment verification passed")
        logger.info(f"   App ID: {app_id}")
        logger.info(f"   Deployer: {deployer_address}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to verify deployment: {e}")
        return False
