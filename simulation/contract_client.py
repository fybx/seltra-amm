"""
Seltra Pool Contract Client

Client for interacting with deployed Seltra AMM pool contracts on Algorand.
Handles real blockchain transactions for swaps and liquidity operations.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal

from algosdk import account, mnemonic, encoding
from algosdk.v2client import algod
from algosdk.transaction import (
    PaymentTxn, 
    ApplicationCallTxn, 
    AssetTransferTxn,
    AssetCreateTxn,
    wait_for_confirmation
)
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    TransactionWithSigner,
    AccountTransactionSigner
)
from algosdk.abi import Contract
from algosdk.error import AlgodHTTPError

logger = logging.getLogger(__name__)


@dataclass
class AssetInfo:
    """Information about an ASA token."""
    id: int
    name: str
    unit_name: str
    decimals: int
    total_supply: int
    creator: str


@dataclass
class PoolInfo:
    """Information about a Seltra pool."""
    app_id: int
    asset_x_id: int
    asset_y_id: int
    current_price: int  # Fixed point
    total_liquidity: int
    is_initialized: bool


@dataclass
class TransactionResult:
    """Result of a blockchain transaction."""
    success: bool
    txn_id: Optional[str] = None
    confirmed_round: Optional[int] = None
    error_message: Optional[str] = None
    gas_used: Optional[int] = None
    execution_time: Optional[float] = None


class SeltraPoolClient:
    """
    Client for interacting with Seltra AMM pool contracts.
    
    Handles contract deployment, asset creation, and all pool operations.
    """
    
    def __init__(
        self,
        algod_client: algod.AlgodClient,
        pool_app_id: Optional[int] = None,
        asset_x_id: Optional[int] = None,
        asset_y_id: Optional[int] = None
    ):
        """
        Initialize the pool client.
        
        Args:
            algod_client: Algorand client instance
            pool_app_id: Existing pool application ID
            asset_x_id: First asset ID in the pair
            asset_y_id: Second asset ID in the pair
        """
        self.algod_client = algod_client
        self.pool_app_id = pool_app_id
        self.asset_x_id = asset_x_id  
        self.asset_y_id = asset_y_id
        
        # Contract ABI (simplified - in production would load from JSON)
        self.contract_abi = None  # Will be loaded when contract is available
        
        # Cache for pool info
        self._pool_info_cache: Optional[PoolInfo] = None
        self._cache_timestamp = 0
        self.cache_duration = 30  # 30 seconds cache
        
    async def connect(self) -> bool:
        """Test connection to Algorand node."""
        try:
            status = self.algod_client.status()
            logger.info(f"Connected to Algorand node - Round: {status.get('last-round', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Algorand node: {e}")
            return False
    
    async def create_test_assets(
        self, 
        creator_private_key: str,
        asset_x_config: Dict[str, Any],
        asset_y_config: Dict[str, Any]
    ) -> Tuple[int, int]:
        """
        Create test ASA tokens for the pool.
        
        Args:
            creator_private_key: Private key of asset creator
            asset_x_config: Config for asset X (e.g., ETH-like)
            asset_y_config: Config for asset Y (e.g., USDC-like)
            
        Returns:
            Tuple of (asset_x_id, asset_y_id)
        """
        creator_address = account.address_from_private_key(creator_private_key)
        
        try:
            # Get suggested parameters
            params = self.algod_client.suggested_params()
            
            # Create Asset X
            asset_x_txn = AssetCreateTxn(
                sender=creator_address,
                sp=params,
                total=asset_x_config["total_supply"],
                default_frozen=False,
                unit_name=asset_x_config["unit_name"],
                asset_name=asset_x_config["name"],
                manager=creator_address,
                reserve=creator_address,
                freeze=creator_address,
                clawback=creator_address,
                decimals=asset_x_config["decimals"]
            )
            
            # Sign and send
            signed_txn = asset_x_txn.sign(creator_private_key)
            txn_id_x = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            result_x = wait_for_confirmation(self.algod_client, txn_id_x, 4)
            asset_x_id = result_x['asset-index']
            
            logger.info(f"Created asset X ({asset_x_config['name']}): {asset_x_id}")
            
            # Create Asset Y
            params = self.algod_client.suggested_params()  # Refresh params
            asset_y_txn = AssetCreateTxn(
                sender=creator_address,
                sp=params,
                total=asset_y_config["total_supply"],
                default_frozen=False,
                unit_name=asset_y_config["unit_name"],
                asset_name=asset_y_config["name"],
                manager=creator_address,
                reserve=creator_address,
                freeze=creator_address,
                clawback=creator_address,
                decimals=asset_y_config["decimals"]
            )
            
            signed_txn = asset_y_txn.sign(creator_private_key)
            txn_id_y = self.algod_client.send_transaction(signed_txn)
            
            result_y = wait_for_confirmation(self.algod_client, txn_id_y, 4)
            asset_y_id = result_y['asset-index']
            
            logger.info(f"Created asset Y ({asset_y_config['name']}): {asset_y_id}")
            
            # Update client state
            self.asset_x_id = asset_x_id
            self.asset_y_id = asset_y_id
            
            return asset_x_id, asset_y_id
            
        except Exception as e:
            logger.error(f"Failed to create test assets: {e}")
            raise
    
    async def deploy_pool_contract(self, deployer_private_key: str) -> int:
        """
        Deploy the Seltra pool contract.
        
        Args:
            deployer_private_key: Private key for deployment
            
        Returns:
            Application ID of deployed contract
        """
        # Note: This would require the compiled contract TEAL code
        # For now, we'll assume the contract is already deployed
        # In a real scenario, we'd need to:
        # 1. Compile the contract.py to TEAL
        # 2. Create ApplicationCreateTxn
        # 3. Deploy and get app_id
        
        raise NotImplementedError("Contract deployment requires compiled TEAL code")
    
    async def initialize_pool(
        self,
        private_key: str,
        initial_price: int  # Fixed point price
    ) -> TransactionResult:
        """
        Initialize the pool with assets and starting price.
        
        Args:
            private_key: Private key of initializer
            initial_price: Starting price in fixed point format
            
        Returns:
            Transaction result
        """
        if not self.pool_app_id:
            return TransactionResult(False, error_message="Pool app ID not set")
        
        if not self.asset_x_id or not self.asset_y_id:
            return TransactionResult(False, error_message="Asset IDs not set")
        
        start_time = time.time()
        
        try:
            sender_address = account.address_from_private_key(private_key)
            params = self.algod_client.suggested_params()
            
            # Create application call transaction
            # Note: This is simplified - real implementation would use ATC
            app_call_txn = ApplicationCallTxn(
                sender=sender_address,
                sp=params,
                index=self.pool_app_id,
                on_complete=0,  # NoOp
                app_args=[
                    "initialize_pool".encode(),
                    self.asset_x_id.to_bytes(8, 'big'),
                    self.asset_y_id.to_bytes(8, 'big'), 
                    initial_price.to_bytes(8, 'big')
                ],
                foreign_assets=[self.asset_x_id, self.asset_y_id]
            )
            
            # Sign and send
            signed_txn = app_call_txn.sign(private_key)
            txn_id = self.algod_client.send_transaction(signed_txn)
            
            # Wait for confirmation
            result = wait_for_confirmation(self.algod_client, txn_id, 4)
            
            execution_time = time.time() - start_time
            
            logger.info(f"Pool initialized successfully - TxnID: {txn_id}")
            
            return TransactionResult(
                success=True,
                txn_id=txn_id,
                confirmed_round=result['confirmed-round'],
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Pool initialization failed: {e}")
            
            return TransactionResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def execute_swap(
        self,
        private_key: str,
        asset_in_id: int,
        asset_out_id: int,
        amount_in: int,
        min_amount_out: int,
        deadline: Optional[int] = None
    ) -> TransactionResult:
        """
        Execute a token swap through the pool.
        
        Args:
            private_key: Private key of swapper
            asset_in_id: Input asset ID
            asset_out_id: Output asset ID
            amount_in: Input amount (in base units)
            min_amount_out: Minimum output amount (slippage protection)
            deadline: Transaction deadline timestamp
            
        Returns:
            Transaction result with swap details
        """
        if not self.pool_app_id:
            return TransactionResult(False, error_message="Pool app ID not set")
        
        start_time = time.time()
        
        try:
            sender_address = account.address_from_private_key(private_key)
            params = self.algod_client.suggested_params()
            
            # Set deadline if not provided
            if not deadline:
                deadline = int(time.time()) + 3600  # 1 hour from now
            
            # Create atomic transaction composer for complex transactions
            atc = AtomicTransactionComposer()
            signer = AccountTransactionSigner(private_key)
            
            # Asset transfer transaction (user -> pool)
            asset_transfer_txn = AssetTransferTxn(
                sender=sender_address,
                sp=params,
                receiver=self.get_pool_address(),  # Pool contract address
                amt=amount_in,
                index=asset_in_id
            )
            
            atc.add_transaction(TransactionWithSigner(asset_transfer_txn, signer))
            
            # Application call for swap
            app_call_txn = ApplicationCallTxn(
                sender=sender_address,
                sp=params,
                index=self.pool_app_id,
                on_complete=0,  # NoOp
                app_args=[
                    "swap".encode(),
                    asset_in_id.to_bytes(8, 'big'),
                    asset_out_id.to_bytes(8, 'big'),
                    amount_in.to_bytes(8, 'big'),
                    min_amount_out.to_bytes(8, 'big'),
                    deadline.to_bytes(8, 'big')
                ],
                foreign_assets=[asset_in_id, asset_out_id],
                foreign_apps=[self.pool_app_id]
            )
            
            atc.add_transaction(TransactionWithSigner(app_call_txn, signer))
            
            # Execute transaction group
            result = atc.execute(self.algod_client, 4)
            
            execution_time = time.time() - start_time
            
            logger.info(f"Swap executed successfully - Group ID: {result.tx_ids[0]}")
            
            return TransactionResult(
                success=True,
                txn_id=result.tx_ids[0],
                confirmed_round=result.confirmed_round,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Swap execution failed: {e}")
            
            return TransactionResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def add_liquidity(
        self,
        private_key: str,
        amount_x_desired: int,
        amount_y_desired: int,
        amount_x_min: int,
        amount_y_min: int,
        range_id: int,
        deadline: Optional[int] = None
    ) -> TransactionResult:
        """
        Add liquidity to a specific range in the pool.
        
        Args:
            private_key: Private key of liquidity provider
            amount_x_desired: Desired amount of asset X
            amount_y_desired: Desired amount of asset Y
            amount_x_min: Minimum amount of asset X
            amount_y_min: Minimum amount of asset Y
            range_id: Range ID (1=tight, 2=medium, 3=wide)
            deadline: Transaction deadline
            
        Returns:
            Transaction result
        """
        if not self.pool_app_id:
            return TransactionResult(False, error_message="Pool app ID not set")
        
        start_time = time.time()
        
        try:
            sender_address = account.address_from_private_key(private_key)
            params = self.algod_client.suggested_params()
            
            if not deadline:
                deadline = int(time.time()) + 3600
            
            # Create atomic transaction composer
            atc = AtomicTransactionComposer()
            signer = AccountTransactionSigner(private_key)
            
            # Asset transfer X
            if amount_x_desired > 0:
                transfer_x_txn = AssetTransferTxn(
                    sender=sender_address,
                    sp=params,
                    receiver=self.get_pool_address(),
                    amt=amount_x_desired,
                    index=self.asset_x_id
                )
                atc.add_transaction(TransactionWithSigner(transfer_x_txn, signer))
            
            # Asset transfer Y  
            if amount_y_desired > 0:
                transfer_y_txn = AssetTransferTxn(
                    sender=sender_address,
                    sp=params,
                    receiver=self.get_pool_address(),
                    amt=amount_y_desired,
                    index=self.asset_y_id
                )
                atc.add_transaction(TransactionWithSigner(transfer_y_txn, signer))
            
            # Application call for add_liquidity
            app_call_txn = ApplicationCallTxn(
                sender=sender_address,
                sp=params,
                index=self.pool_app_id,
                on_complete=0,
                app_args=[
                    "add_liquidity".encode(),
                    self.asset_x_id.to_bytes(8, 'big'),
                    self.asset_y_id.to_bytes(8, 'big'),
                    amount_x_desired.to_bytes(8, 'big'),
                    amount_y_desired.to_bytes(8, 'big'),
                    amount_x_min.to_bytes(8, 'big'),
                    amount_y_min.to_bytes(8, 'big'),
                    range_id.to_bytes(8, 'big'),
                    deadline.to_bytes(8, 'big')
                ],
                foreign_assets=[self.asset_x_id, self.asset_y_id]
            )
            
            atc.add_transaction(TransactionWithSigner(app_call_txn, signer))
            
            # Execute
            result = atc.execute(self.algod_client, 4)
            
            execution_time = time.time() - start_time
            
            logger.info(f"Liquidity added successfully - Group ID: {result.tx_ids[0]}")
            
            return TransactionResult(
                success=True,
                txn_id=result.tx_ids[0],
                confirmed_round=result.confirmed_round,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Add liquidity failed: {e}")
            
            return TransactionResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    async def remove_liquidity(
        self,
        private_key: str,
        lp_token_amount: int,
        amount_x_min: int,
        amount_y_min: int,
        range_id: int,
        deadline: Optional[int] = None
    ) -> TransactionResult:
        """
        Remove liquidity from a specific range.
        
        Args:
            private_key: Private key of liquidity provider
            lp_token_amount: Amount of LP tokens to burn
            amount_x_min: Minimum asset X to receive
            amount_y_min: Minimum asset Y to receive
            range_id: Range ID
            deadline: Transaction deadline
            
        Returns:
            Transaction result
        """
        if not self.pool_app_id:
            return TransactionResult(False, error_message="Pool app ID not set")
        
        start_time = time.time()
        
        try:
            sender_address = account.address_from_private_key(private_key)
            params = self.algod_client.suggested_params()
            
            if not deadline:
                deadline = int(time.time()) + 3600
            
            # Application call for remove_liquidity
            app_call_txn = ApplicationCallTxn(
                sender=sender_address,
                sp=params,
                index=self.pool_app_id,
                on_complete=0,
                app_args=[
                    "remove_liquidity".encode(),
                    lp_token_amount.to_bytes(8, 'big'),
                    amount_x_min.to_bytes(8, 'big'),
                    amount_y_min.to_bytes(8, 'big'),
                    range_id.to_bytes(8, 'big'),
                    deadline.to_bytes(8, 'big')
                ],
                foreign_assets=[self.asset_x_id, self.asset_y_id]
            )
            
            signed_txn = app_call_txn.sign(private_key)
            txn_id = self.algod_client.send_transaction(signed_txn)
            
            result = wait_for_confirmation(self.algod_client, txn_id, 4)
            
            execution_time = time.time() - start_time
            
            logger.info(f"Liquidity removed successfully - TxnID: {txn_id}")
            
            return TransactionResult(
                success=True,
                txn_id=txn_id,
                confirmed_round=result['confirmed-round'],
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Remove liquidity failed: {e}")
            
            return TransactionResult(
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def get_pool_address(self) -> str:
        """Get the pool contract address."""
        if not self.pool_app_id:
            raise ValueError("Pool app ID not set")
        
        # Convert app ID to address
        return encoding.encode_address(encoding.checksum(b"appID" + self.pool_app_id.to_bytes(8, "big")))
    
    async def get_pool_info(self, force_refresh: bool = False) -> Optional[PoolInfo]:
        """
        Get current pool information with caching.
        
        Args:
            force_refresh: Skip cache and fetch fresh data
            
        Returns:
            Pool information or None if unavailable
        """
        current_time = time.time()
        
        # Return cached data if valid
        if (not force_refresh and 
            self._pool_info_cache and 
            current_time - self._cache_timestamp < self.cache_duration):
            return self._pool_info_cache
        
        try:
            if not self.pool_app_id:
                return None
            
            # Fetch application info
            app_info = self.algod_client.application_info(self.pool_app_id)
            
            # Parse global state (simplified - would need proper parsing)
            global_state = app_info.get('params', {}).get('global-state', [])
            
            # Extract pool data from global state
            # Note: This is simplified - real implementation would parse the state properly
            pool_info = PoolInfo(
                app_id=self.pool_app_id,
                asset_x_id=self.asset_x_id or 0,
                asset_y_id=self.asset_y_id or 0,
                current_price=0,  # Would parse from state
                total_liquidity=0,  # Would parse from state
                is_initialized=True  # Would check from state
            )
            
            # Update cache
            self._pool_info_cache = pool_info
            self._cache_timestamp = current_time
            
            return pool_info
            
        except Exception as e:
            logger.error(f"Failed to get pool info: {e}")
            return None
    
    async def get_asset_balance(self, address: str, asset_id: int) -> int:
        """
        Get asset balance for an address.
        
        Args:
            address: Account address
            asset_id: Asset ID (0 for ALGO)
            
        Returns:
            Balance in base units
        """
        try:
            if asset_id == 0:
                # ALGO balance
                account_info = self.algod_client.account_info(address)
                return account_info.get('amount', 0)
            else:
                # ASA balance
                account_info = self.algod_client.account_info(address)
                assets = account_info.get('assets', [])
                
                for asset in assets:
                    if asset.get('asset-id') == asset_id:
                        return asset.get('amount', 0)
                
                return 0
                
        except Exception as e:
            logger.error(f"Failed to get asset balance: {e}")
            return 0
