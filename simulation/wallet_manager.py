"""
Wallet Manager for Real Algorand Accounts

Manages creation, funding, and tracking of real Algorand wallets
for the blockchain simulation system.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
import json
import os

from algosdk import account, mnemonic, encoding
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn, AssetTransferTxn, wait_for_confirmation
from algosdk.error import AlgodHTTPError

from .contract_client import SeltraPoolClient

logger = logging.getLogger(__name__)


@dataclass
class ManagedWallet:
    """A managed wallet with trading characteristics."""
    address: str
    private_key: str
    mnemonic_phrase: str
    
    # Trading profile
    pattern: str  # "whale" or "retail"
    trade_frequency: float  # trades per minute
    avg_trade_size: float  # average trade size in ALGO
    volatility_sensitivity: float  # reaction to volatility
    
    # Balances (cached)
    algo_balance: int = 0  # microALGOs
    asset_x_balance: int = 0
    asset_y_balance: int = 0
    
    # Statistics
    total_transactions: int = 0
    successful_transactions: int = 0
    total_volume: float = 0.0
    
    # Last update timestamp
    last_balance_update: float = 0


@dataclass
class FundingConfig:
    """Configuration for wallet funding."""
    faucet_private_key: str
    faucet_address: str
    initial_algo_amount: int  # microALGOs
    initial_asset_x_amount: int
    initial_asset_y_amount: int
    min_algo_balance: int  # Refill threshold


class WalletManager:
    """
    Manages real Algorand wallets for simulation.
    
    Features:
    - Creates and funds real wallets
    - Tracks balances and trading activity
    - Handles wallet backup and recovery
    - Provides wallet analytics
    """
    
    def __init__(
        self,
        algod_client: algod.AlgodClient,
        pool_client: SeltraPoolClient,
        funding_config: Optional[FundingConfig] = None,
        wallet_storage_path: str = "simulation_wallets.json"
    ):
        """
        Initialize wallet manager.
        
        Args:
            algod_client: Algorand client
            pool_client: Pool contract client
            funding_config: Configuration for wallet funding
            wallet_storage_path: Path to store wallet data
        """
        self.algod_client = algod_client
        self.pool_client = pool_client
        self.funding_config = funding_config
        self.wallet_storage_path = wallet_storage_path
        
        # Managed wallets
        self.wallets: Dict[str, ManagedWallet] = {}
        
        # Trading patterns configuration
        self.pattern_config = {
            "whale": {
                "base_frequency": 0.2,  # Lower frequency
                "avg_trade_size_range": (1000, 5000),  # ALGO
                "volatility_sensitivity": 0.5,  # Less reactive
                "algo_funding": 50_000_000_000,  # 50,000 ALGO
                "asset_funding_multiplier": 100
            },
            "retail": {
                "base_frequency": 1.0,  # Higher frequency
                "avg_trade_size_range": (10, 200),  # ALGO
                "volatility_sensitivity": 1.0,  # More reactive
                "algo_funding": 5_000_000_000,  # 5,000 ALGO
                "asset_funding_multiplier": 10
            }
        }
        
    async def load_existing_wallets(self) -> int:
        """
        Load existing wallets from storage.
        
        Returns:
            Number of wallets loaded
        """
        if not os.path.exists(self.wallet_storage_path):
            logger.info("No existing wallet file found")
            return 0
        
        try:
            with open(self.wallet_storage_path, 'r') as f:
                wallet_data = json.load(f)
            
            for address, data in wallet_data.items():
                wallet = ManagedWallet(**data)
                self.wallets[address] = wallet
            
            logger.info(f"Loaded {len(self.wallets)} existing wallets")
            return len(self.wallets)
            
        except Exception as e:
            logger.error(f"Failed to load existing wallets: {e}")
            return 0
    
    async def save_wallets(self) -> bool:
        """
        Save wallets to persistent storage.
        
        Returns:
            True if saved successfully
        """
        try:
            wallet_data = {}
            for address, wallet in self.wallets.items():
                wallet_data[address] = asdict(wallet)
            
            with open(self.wallet_storage_path, 'w') as f:
                json.dump(wallet_data, f, indent=2)
            
            logger.info(f"Saved {len(self.wallets)} wallets to {self.wallet_storage_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save wallets: {e}")
            return False
    
    async def create_wallets(
        self, 
        num_wallets: int,
        whale_ratio: float = 0.15
    ) -> List[ManagedWallet]:
        """
        Create a set of new wallets with different patterns.
        
        Args:
            num_wallets: Total number of wallets to create
            whale_ratio: Ratio of whale wallets (0.0 to 1.0)
            
        Returns:
            List of created wallets
        """
        whale_count = max(1, int(num_wallets * whale_ratio))
        retail_count = num_wallets - whale_count
        
        created_wallets = []
        
        logger.info(f"Creating {num_wallets} wallets ({whale_count} whales, {retail_count} retail)")
        
        # Create whale wallets
        for i in range(whale_count):
            wallet = await self._create_single_wallet("whale")
            created_wallets.append(wallet)
            self.wallets[wallet.address] = wallet
        
        # Create retail wallets
        for i in range(retail_count):
            wallet = await self._create_single_wallet("retail")
            created_wallets.append(wallet)
            self.wallets[wallet.address] = wallet
        
        # Save to storage
        await self.save_wallets()
        
        logger.info(f"Successfully created {len(created_wallets)} wallets")
        return created_wallets
    
    async def _create_single_wallet(self, pattern: str) -> ManagedWallet:
        """Create a single wallet with specified pattern."""
        import random
        
        # Generate new Algorand account
        private_key, address = account.generate_account()
        mnemonic_phrase = mnemonic.from_private_key(private_key)
        
        config = self.pattern_config[pattern]
        
        # Randomize trade characteristics
        trade_frequency = config["base_frequency"] * random.uniform(0.7, 1.3)
        avg_trade_size = random.uniform(*config["avg_trade_size_range"])
        volatility_sensitivity = config["volatility_sensitivity"] * random.uniform(0.8, 1.2)
        
        wallet = ManagedWallet(
            address=address,
            private_key=private_key,
            mnemonic_phrase=mnemonic_phrase,
            pattern=pattern,
            trade_frequency=trade_frequency,
            avg_trade_size=avg_trade_size,
            volatility_sensitivity=volatility_sensitivity
        )
        
        logger.debug(f"Created {pattern} wallet: {address[:12]}...")
        return wallet
    
    async def fund_wallet(self, wallet: ManagedWallet) -> bool:
        """
        Fund a wallet with initial ALGO and ASA tokens.
        
        Args:
            wallet: Wallet to fund
            
        Returns:
            True if funding successful
        """
        if not self.funding_config:
            logger.warning("No funding configuration available")
            return False
        
        try:
            config = self.pattern_config[wallet.pattern]
            
            # Fund with ALGO
            algo_amount = config["algo_funding"]
            success = await self._send_algo(
                self.funding_config.faucet_private_key,
                wallet.address,
                algo_amount
            )
            
            if not success:
                logger.error(f"Failed to fund wallet {wallet.address[:12]}... with ALGO")
                return False
            
            # Opt-in to ASA tokens if they exist
            if self.pool_client.asset_x_id:
                await self._opt_in_to_asset(wallet, self.pool_client.asset_x_id)
                
                # Fund with asset X
                asset_x_amount = self.funding_config.initial_asset_x_amount * config["asset_funding_multiplier"]
                await self._send_asset(
                    self.funding_config.faucet_private_key,
                    wallet.address,
                    self.pool_client.asset_x_id,
                    asset_x_amount
                )
            
            if self.pool_client.asset_y_id:
                await self._opt_in_to_asset(wallet, self.pool_client.asset_y_id)
                
                # Fund with asset Y
                asset_y_amount = self.funding_config.initial_asset_y_amount * config["asset_funding_multiplier"]
                await self._send_asset(
                    self.funding_config.faucet_private_key,
                    wallet.address,
                    self.pool_client.asset_y_id,
                    asset_y_amount
                )
            
            logger.info(f"Successfully funded wallet {wallet.address[:12]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fund wallet {wallet.address[:12]}...: {e}")
            return False
    
    async def fund_all_wallets(self) -> int:
        """
        Fund all managed wallets.
        
        Returns:
            Number of successfully funded wallets
        """
        if not self.funding_config:
            logger.error("Cannot fund wallets without funding configuration")
            return 0
        
        success_count = 0
        
        for wallet in self.wallets.values():
            if await self.fund_wallet(wallet):
                success_count += 1
            
            # Small delay to avoid overwhelming the network
            await asyncio.sleep(0.5)
        
        logger.info(f"Successfully funded {success_count}/{len(self.wallets)} wallets")
        return success_count
    
    async def _send_algo(self, sender_private_key: str, receiver: str, amount: int) -> bool:
        """Send ALGO from sender to receiver."""
        try:
            sender_address = account.address_from_private_key(sender_private_key)
            params = self.algod_client.suggested_params()
            
            txn = PaymentTxn(
                sender=sender_address,
                sp=params,
                receiver=receiver,
                amt=amount
            )
            
            signed_txn = txn.sign(sender_private_key)
            txn_id = self.algod_client.send_transaction(signed_txn)
            
            wait_for_confirmation(self.algod_client, txn_id, 4)
            logger.debug(f"Sent {amount} microALGOs to {receiver[:12]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send ALGO: {e}")
            return False
    
    async def _send_asset(
        self, 
        sender_private_key: str, 
        receiver: str, 
        asset_id: int, 
        amount: int
    ) -> bool:
        """Send ASA tokens from sender to receiver."""
        try:
            sender_address = account.address_from_private_key(sender_private_key)
            params = self.algod_client.suggested_params()
            
            txn = AssetTransferTxn(
                sender=sender_address,
                sp=params,
                receiver=receiver,
                amt=amount,
                index=asset_id
            )
            
            signed_txn = txn.sign(sender_private_key)
            txn_id = self.algod_client.send_transaction(signed_txn)
            
            wait_for_confirmation(self.algod_client, txn_id, 4)
            logger.debug(f"Sent {amount} of asset {asset_id} to {receiver[:12]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send asset: {e}")
            return False
    
    async def _opt_in_to_asset(self, wallet: ManagedWallet, asset_id: int) -> bool:
        """Opt wallet into an ASA token."""
        try:
            params = self.algod_client.suggested_params()
            
            # Asset opt-in transaction (send 0 amount to self)
            txn = AssetTransferTxn(
                sender=wallet.address,
                sp=params,
                receiver=wallet.address,
                amt=0,
                index=asset_id
            )
            
            signed_txn = txn.sign(wallet.private_key)
            txn_id = self.algod_client.send_transaction(signed_txn)
            
            wait_for_confirmation(self.algod_client, txn_id, 4)
            logger.debug(f"Wallet {wallet.address[:12]}... opted into asset {asset_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to opt-in to asset {asset_id}: {e}")
            return False
    
    async def update_wallet_balances(self, addresses: Optional[List[str]] = None) -> int:
        """
        Update cached balances for wallets.
        
        Args:
            addresses: Specific addresses to update, or None for all
            
        Returns:
            Number of wallets updated successfully
        """
        if addresses is None:
            addresses = list(self.wallets.keys())
        
        updated_count = 0
        current_time = time.time()
        
        for address in addresses:
            if address not in self.wallets:
                continue
            
            wallet = self.wallets[address]
            
            try:
                # Update ALGO balance
                wallet.algo_balance = await self.pool_client.get_asset_balance(address, 0)
                
                # Update ASA balances
                if self.pool_client.asset_x_id:
                    wallet.asset_x_balance = await self.pool_client.get_asset_balance(
                        address, self.pool_client.asset_x_id
                    )
                
                if self.pool_client.asset_y_id:
                    wallet.asset_y_balance = await self.pool_client.get_asset_balance(
                        address, self.pool_client.asset_y_id
                    )
                
                wallet.last_balance_update = current_time
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update balance for {address[:12]}...: {e}")
        
        logger.debug(f"Updated balances for {updated_count} wallets")
        return updated_count
    
    async def check_and_refill_wallets(self) -> int:
        """
        Check wallet balances and refill if needed.
        
        Returns:
            Number of wallets refilled
        """
        if not self.funding_config:
            return 0
        
        refilled_count = 0
        
        for wallet in self.wallets.values():
            # Check if ALGO balance is below threshold
            if wallet.algo_balance < self.funding_config.min_algo_balance:
                config = self.pattern_config[wallet.pattern]
                refill_amount = config["algo_funding"] // 4  # Refill with 1/4 of initial amount
                
                success = await self._send_algo(
                    self.funding_config.faucet_private_key,
                    wallet.address,
                    refill_amount
                )
                
                if success:
                    wallet.algo_balance += refill_amount
                    refilled_count += 1
                    logger.info(f"Refilled wallet {wallet.address[:12]}... with {refill_amount} microALGOs")
                
                # Small delay between refills
                await asyncio.sleep(0.2)
        
        return refilled_count
    
    def get_wallet_by_pattern(self, pattern: str) -> List[ManagedWallet]:
        """Get all wallets matching a specific pattern."""
        return [wallet for wallet in self.wallets.values() if wallet.pattern == pattern]
    
    def get_whale_wallets(self) -> List[ManagedWallet]:
        """Get all whale wallets."""
        return self.get_wallet_by_pattern("whale")
    
    def get_retail_wallets(self) -> List[ManagedWallet]:
        """Get all retail wallets."""
        return self.get_wallet_by_pattern("retail")
    
    def get_wallet_info(self) -> List[Dict[str, Any]]:
        """Get information about all wallets for API responses."""
        wallet_info = []
        
        for wallet in self.wallets.values():
            info = {
                "address": wallet.address,
                "pattern": wallet.pattern,
                "algo_balance": wallet.algo_balance / 1_000_000,  # Convert to ALGO
                "asset_x_balance": wallet.asset_x_balance,
                "asset_y_balance": wallet.asset_y_balance,
                "trade_frequency": wallet.trade_frequency,
                "avg_trade_size": wallet.avg_trade_size,
                "volatility_sensitivity": wallet.volatility_sensitivity,
                "total_transactions": wallet.total_transactions,
                "successful_transactions": wallet.successful_transactions,
                "success_rate": (
                    wallet.successful_transactions / max(1, wallet.total_transactions) * 100
                ),
                "total_volume": wallet.total_volume,
                "last_balance_update": wallet.last_balance_update
            }
            wallet_info.append(info)
        
        return wallet_info
    
    def update_wallet_stats(
        self, 
        address: str, 
        transaction_success: bool, 
        volume: float = 0.0
    ):
        """Update wallet transaction statistics."""
        if address not in self.wallets:
            return
        
        wallet = self.wallets[address]
        wallet.total_transactions += 1
        
        if transaction_success:
            wallet.successful_transactions += 1
        
        if volume > 0:
            wallet.total_volume += volume
    
    async def cleanup(self):
        """Clean up resources and save wallet state."""
        await self.save_wallets()
        logger.info("Wallet manager cleanup completed")
