"""
HACK Token Deployment Configuration
Handles deployment of the HACK ASA token to Algorand network
"""

import logging
from typing import Dict, Any, Tuple, Optional
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from algosdk.transaction import AssetCreateTxn, wait_for_confirmation
from algosdk.account import address_from_private_key
import algokit_utils

from .token_config import get_hack_token_config, get_distribution_config

logger = logging.getLogger(__name__)


class HACKTokenDeployer:
    """
    Handles deployment and management of the HACK ASA token.
    
    Features:
    - ASA creation with proper metadata
    - Distribution to demo wallets
    - Configuration validation
    - Network compatibility
    """
    
    def __init__(
        self, 
        algod_client: AlgodClient,
        indexer_client: Optional[IndexerClient] = None
    ):
        self.algod_client = algod_client
        self.indexer_client = indexer_client
        self.token_config = get_hack_token_config()
        self.distribution_config = get_distribution_config()
        
    async def deploy_hack_token(
        self, 
        creator_account: algokit_utils.Account
    ) -> Tuple[int, str]:
        """
        Deploy the HACK ASA token to Algorand network.
        
        Args:
            creator_account: Account that will create and manage the token
            
        Returns:
            Tuple of (asset_id, transaction_id)
            
        Raises:
            Exception: If deployment fails
        """
        try:
            logger.info("🚀 Deploying HACK ASA token...")
            
            # Validate configuration
            self._validate_config()
            
            # Get suggested parameters
            params = self.algod_client.suggested_params()
            
            # Set management addresses to creator address
            creator_address = creator_account.address
            
            # Create ASA transaction
            asset_create_txn = AssetCreateTxn(
                sender=creator_address,
                sp=params,
                total=self.token_config["total_supply"],
                default_frozen=self.token_config["default_frozen"],
                unit_name=self.token_config["unit_name"],
                asset_name=self.token_config["name"],
                manager=creator_address,  # Can modify token properties
                reserve=creator_address,  # Can mint/burn tokens
                freeze=creator_address,   # Can freeze accounts
                clawback=creator_address, # Can clawback tokens
                url=self.token_config["url"],
                decimals=self.token_config["decimals"]
            )
            
            # Sign transaction
            signed_txn = asset_create_txn.sign(creator_account.private_key)
            
            # Submit transaction
            txn_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            result = wait_for_confirmation(self.algod_client, txn_id, 4)
            asset_id = result['asset-index']
            
            logger.info(f"✅ HACK token created successfully!")
            logger.info(f"Asset ID: {asset_id}")
            logger.info(f"Transaction ID: {txn_id}")
            logger.info(f"Creator: {creator_address}")
            
            # Log token details
            self._log_token_details(asset_id, creator_address)
            
            return asset_id, txn_id
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy HACK token: {e}")
            raise
    
    def _validate_config(self) -> None:
        """Validate token configuration before deployment"""
        required_fields = ["name", "unit_name", "decimals", "total_supply", "url"]
        
        for field in required_fields:
            if field not in self.token_config:
                raise ValueError(f"Missing required field: {field}")
                
        # Validate numeric values
        if self.token_config["decimals"] < 0 or self.token_config["decimals"] > 19:
            raise ValueError("Decimals must be between 0 and 19")
            
        if self.token_config["total_supply"] <= 0:
            raise ValueError("Total supply must be positive")
            
        # Validate supply matches specifications
        expected_supply = 1_000_000_000_000  # 1M HACK tokens in microunits
        if self.token_config["total_supply"] != expected_supply:
            logger.warning(f"Total supply ({self.token_config['total_supply']}) doesn't match spec ({expected_supply})")
    
    def _log_token_details(self, asset_id: int, creator_address: str) -> None:
        """Log detailed token information"""
        logger.info("📋 HACK Token Details:")
        logger.info(f"  Name: {self.token_config['name']}")
        logger.info(f"  Unit Name: {self.token_config['unit_name']}")
        logger.info(f"  Asset ID: {asset_id}")
        logger.info(f"  Total Supply: {self.token_config['total_supply']:,} microHACK")
        logger.info(f"  Decimals: {self.token_config['decimals']}")
        logger.info(f"  URL: {self.token_config['url']}")
        logger.info(f"  Creator: {creator_address}")
        logger.info(f"  Manager: {creator_address}")
        logger.info(f"  Reserve: {creator_address}")
        
        # Log distribution amounts
        logger.info("💰 Token Distribution Plan:")
        for key, dist in self.distribution_config.items():
            amount = dist["amount"]
            percentage = dist["percentage"]
            human_readable = amount // 1_000_000  # Convert to whole tokens
            logger.info(f"  {key.replace('_', ' ').title()}: {human_readable:,} HACK ({percentage}%)")
    
    async def get_asset_info(self, asset_id: int) -> Dict[str, Any]:
        """
        Get information about the HACK token asset.
        
        Args:
            asset_id: The asset ID to query
            
        Returns:
            Asset information dictionary
        """
        try:
            asset_info = self.algod_client.asset_info(asset_id)
            return asset_info
        except Exception as e:
            logger.error(f"Failed to get asset info for {asset_id}: {e}")
            return {}
    
    def verify_deployment(self, asset_id: int, creator_address: str) -> bool:
        """
        Verify that the HACK token was deployed correctly.
        
        Args:
            asset_id: The deployed asset ID
            creator_address: Expected creator address
            
        Returns:
            True if verification passes
        """
        try:
            asset_info = self.algod_client.asset_info(asset_id)
            params = asset_info["params"]
            
            # Verify basic parameters
            checks = [
                params["name"] == self.token_config["name"],
                params["unit-name"] == self.token_config["unit_name"],
                params["decimals"] == self.token_config["decimals"],
                params["total"] == self.token_config["total_supply"],
                params["creator"] == creator_address,
                params["manager"] == creator_address,
                params["reserve"] == creator_address,
            ]
            
            if all(checks):
                logger.info("✅ HACK token deployment verification passed")
                return True
            else:
                logger.error("❌ HACK token deployment verification failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to verify deployment: {e}")
            return False


def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    deployer: algokit_utils.Account,
) -> Tuple[int, str]:
    """
    Main deployment function for HACK token.
    
    Args:
        algod_client: Algorand client
        indexer_client: Indexer client  
        deployer: Deployer account
        
    Returns:
        Tuple of (asset_id, transaction_id)
    """
    deployer_instance = HACKTokenDeployer(algod_client, indexer_client)
    
    # Deploy token (convert async method to sync)
    # Since deploy_hack_token is async but we need sync, let's create a sync version
    asset_id, txn_id = _deploy_hack_token_sync(deployer_instance, deployer)
    
    # Verify deployment
    if deployer_instance.verify_deployment(asset_id, deployer.address):
        logger.info(f"🎉 HACK token deployment completed successfully")
        logger.info(f"   Asset ID: {asset_id}")
        logger.info(f"   Ready for ALGO-HACK pool creation")
    else:
        logger.error("❌ HACK token deployment verification failed")
    
    return asset_id, txn_id


def _deploy_hack_token_sync(deployer_instance: HACKTokenDeployer, deployer: algokit_utils.Account) -> Tuple[int, str]:
    """Synchronous wrapper for the async deploy_hack_token method."""
    try:
        # Get suggested parameters
        params = deployer_instance.algod_client.suggested_params()
        
        # Set management addresses to creator address
        creator_address = deployer.address
        
        # Create ASA transaction
        from algosdk.transaction import AssetCreateTxn, wait_for_confirmation
        asset_create_txn = AssetCreateTxn(
            sender=creator_address,
            sp=params,
            total=deployer_instance.token_config["total_supply"],
            default_frozen=deployer_instance.token_config["default_frozen"],
            unit_name=deployer_instance.token_config["unit_name"],
            asset_name=deployer_instance.token_config["name"],
            manager=creator_address,  # Can modify token properties
            reserve=creator_address,  # Can mint/burn tokens
            freeze=creator_address,   # Can freeze accounts
            clawback=creator_address, # Can clawback tokens
            url=deployer_instance.token_config["url"],
            decimals=deployer_instance.token_config["decimals"]
        )
        
        # Sign transaction
        signed_txn = asset_create_txn.sign(deployer.private_key)
        
        # Submit transaction
        txn_id = deployer_instance.algod_client.send_transaction(signed_txn)
        
        # Wait for confirmation
        result = wait_for_confirmation(deployer_instance.algod_client, txn_id, 4)
        asset_id = result['asset-index']
        
        logger.info(f"✅ HACK token created successfully!")
        logger.info(f"Asset ID: {asset_id}")
        logger.info(f"Transaction ID: {txn_id}")
        logger.info(f"Creator: {creator_address}")
        
        # Log token details
        deployer_instance._log_token_details(asset_id, creator_address)
        
        return asset_id, txn_id
        
    except Exception as e:
        logger.error(f"❌ Failed to deploy HACK token: {e}")
        raise
