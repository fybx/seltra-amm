"""
Algorand Blockchain Transaction Simulator

Simulates realistic trading patterns on the local Algorand blockchain
with different market regimes (volatile vs normal).
"""

import asyncio
import random
import time
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum

from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn, ApplicationCallTxn, AssetTransferTxn
from algosdk.atomic_transaction_composer import AtomicTransactionComposer
from algosdk.encoding import encode_address

from .contract_client import SeltraPoolClient, TransactionResult
from .wallet_manager import WalletManager, ManagedWallet, FundingConfig

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Types of transactions to simulate."""
    SWAP = "swap"
    ADD_LIQUIDITY = "add_liquidity" 
    REMOVE_LIQUIDITY = "remove_liquidity"
    PAYMENT = "payment"


class TradingPattern(Enum):
    """Trading behavior patterns."""
    NORMAL = "normal"
    VOLATILE = "volatile"
    WHALE = "whale"
    RETAIL = "retail"


@dataclass
class TransactionPlan:
    """Planned transaction with timing and parameters."""
    wallet: ManagedWallet
    tx_type: TransactionType
    size: float
    target_time: float
    parameters: Dict


class AlgorandTransactionSimulator:
    """
    Simulates realistic Algorand blockchain transactions for testing the Seltra AMM.
    """
    
    def __init__(
        self,
        algod_address: str = "http://localhost:4001",
        algod_token: str = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        num_wallets: int = 20,
        market_simulator=None,
        pool_app_id: Optional[int] = None,
        asset_x_id: Optional[int] = None,
        asset_y_id: Optional[int] = None,
        faucet_private_key: Optional[str] = None
    ):
        """
        Initialize the blockchain transaction simulator.
        
        Args:
            algod_address: Algorand node address
            algod_token: Algorand node token
            num_wallets: Number of wallets to create for simulation
            market_simulator: Market simulator for volatility data
            pool_app_id: Seltra pool application ID
            asset_x_id: Asset X ID
            asset_y_id: Asset Y ID
            faucet_private_key: Private key for funding wallets
        """
        self.algod_address = algod_address
        self.algod_token = algod_token
        self.num_wallets = num_wallets
        self.market_simulator = market_simulator
        
        # Initialize Algorand client
        self.algod_client = algod.AlgodClient(algod_token, algod_address)

        # Initialize contract client (only if we have contract IDs)
        if pool_app_id and asset_y_id:
            self.pool_client = SeltraPoolClient(
                self.algod_client,
                pool_app_id,
                asset_x_id,
                asset_y_id
            )
            logger.info(f"🔗 Connected to deployed contracts (Pool: {pool_app_id}, Assets: {asset_x_id}/{asset_y_id})")
        else:
            self.pool_client = None
            if pool_app_id or asset_y_id:
                logger.warning("⚠️  Contract IDs provided but incomplete - running in simulation-only mode")
            else:
                logger.info("🔧 Running in simulation-only mode (no contracts deployed yet)")
        
        # Initialize wallet manager
        funding_config = None
        if faucet_private_key:
            funding_config = FundingConfig(
                faucet_private_key=faucet_private_key,
                faucet_address=account.address_from_private_key(faucet_private_key),
                initial_algo_amount=5_000_000_000,  # 5,000 ALGO
                initial_asset_x_amount=10_000_000_000,  # 10,000 tokens
                initial_asset_y_amount=10_000_000_000,  # 10,000 tokens  
                min_algo_balance=1_000_000_000  # 1,000 ALGO refill threshold
            )
        
        self.wallet_manager = WalletManager(
            self.algod_client,
            self.pool_client,
            funding_config
        )
        
        # Simulation state
        self.transaction_queue: List[TransactionPlan] = []
        self.is_running = False
        self.current_pattern = TradingPattern.NORMAL
        
        # Statistics
        self.total_transactions = 0
        self.successful_transactions = 0
        self.failed_transactions = 0
        self.start_time = time.time()
        
        # Pattern parameters
        self.pattern_config = {
            TradingPattern.NORMAL: {
                "base_frequency": 0.5,  # 0.5 transactions per minute per wallet
                "size_variance": 0.3,   # 30% variance in trade sizes
                "burst_probability": 0.1,  # 10% chance of transaction bursts
                "whale_ratio": 0.05,    # 5% of wallets are whales
            },
            TradingPattern.VOLATILE: {
                "base_frequency": 2.0,   # 2 transactions per minute per wallet
                "size_variance": 0.8,    # 80% variance in trade sizes
                "burst_probability": 0.3,  # 30% chance of transaction bursts
                "whale_ratio": 0.15,     # 15% of wallets are whales
            }
        }
        
        
    async def initialize(self):
        """Initialize the simulator - create wallets and connect to blockchain."""
        logger.info("Initializing Algorand Transaction Simulator...")
        
        # Test connection to Algorand node
        if not await self.pool_client.connect():
            raise RuntimeError("Failed to connect to Algorand node")
        
        # Load existing wallets or create new ones
        existing_wallets = await self.wallet_manager.load_existing_wallets()
        
        if existing_wallets == 0:
            logger.info("Creating new wallets...")
            current_config = self.pattern_config[self.current_pattern]
            whale_ratio = current_config.get("whale_ratio", 0.15)
            
            await self.wallet_manager.create_wallets(self.num_wallets, whale_ratio)
        
        # Fund wallets if faucet is available
        if self.wallet_manager.funding_config:
            logger.info("Funding wallets...")
            funded_count = await self.wallet_manager.fund_all_wallets()
            logger.info(f"Successfully funded {funded_count} wallets")
        
        # Update initial wallet balances
        await self.wallet_manager.update_wallet_balances()
        
        logger.info(f"Simulation initialized with {len(self.wallet_manager.wallets)} wallets")
    
    
    async def start_simulation(self):
        """Start the transaction simulation."""
        if self.is_running:
            logger.warning("Simulation is already running")
            return
        
        self.is_running = True
        self.start_time = time.time()
        logger.info("Starting blockchain transaction simulation...")
        
        try:
            # Main simulation loop
            while self.is_running:
                await self._simulation_tick()
                await asyncio.sleep(5)  # Update every 5 seconds
        
        except asyncio.CancelledError:
            logger.info("Simulation cancelled")
            raise
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            raise
        finally:
            self.is_running = False
    
    def stop_simulation(self):
        """Stop the transaction simulation."""
        self.is_running = False
        logger.info("Stopping blockchain transaction simulation...")
    
    async def _simulation_tick(self):
        """Process one simulation tick - generate and execute transactions."""
        current_time = time.time()
        
        # Generate new transaction plans
        await self._generate_transaction_plans(current_time)
        
        # Execute ready transactions
        ready_transactions = [
            plan for plan in self.transaction_queue 
            if plan.target_time <= current_time
        ]
        
        if ready_transactions:
            await self._execute_transactions(ready_transactions)
            
            # Remove executed transactions
            self.transaction_queue = [
                plan for plan in self.transaction_queue 
                if plan.target_time > current_time
            ]
    
    async def _generate_transaction_plans(self, current_time: float):
        """Generate transaction plans based on current market conditions."""
        current_config = self.pattern_config[self.current_pattern]
        
        for wallet in self.wallet_manager.wallets.values():
            # Calculate transaction probability for this wallet
            base_prob = wallet.trade_frequency / 60.0 * 5  # Per 5-second tick
            
            # Adjust for volatility sensitivity - get real volatility from market simulator
            if self.market_simulator:
                market_volatility = self.market_simulator.get_current_volatility()
            else:
                market_volatility = 0.02  # Fallback
            
            volatility_multiplier = 1.0 + (market_volatility - 0.02) * wallet.volatility_sensitivity
            
            effective_prob = base_prob * volatility_multiplier
            
            # Check if this wallet should make a transaction
            if random.random() < effective_prob:
                plan = await self._create_transaction_plan(wallet, current_time)
                if plan:
                    self.transaction_queue.append(plan)
    
    async def _create_transaction_plan(self, wallet: ManagedWallet, current_time: float) -> Optional[TransactionPlan]:
        """Create a specific transaction plan for a wallet."""
        # Choose transaction type based on wallet pattern
        tx_types = [TransactionType.SWAP, TransactionType.ADD_LIQUIDITY, TransactionType.REMOVE_LIQUIDITY]
        
        if wallet.pattern == "whale":
            # Whales prefer swaps and liquidity provision
            tx_type = random.choices(
                tx_types, 
                weights=[0.6, 0.3, 0.1]  # 60% swap, 30% add liquidity, 10% remove
            )[0]
        else:
            # Retail traders mostly swap
            tx_type = random.choices(
                tx_types,
                weights=[0.8, 0.15, 0.05]  # 80% swap, 15% add, 5% remove
            )[0]
        
        # Calculate transaction size with randomization
        current_config = self.pattern_config[self.current_pattern]
        size_variance = current_config["size_variance"]
        
        size_multiplier = 1.0 + random.uniform(-size_variance, size_variance)
        tx_size = wallet.avg_trade_size * size_multiplier
        tx_size = max(1.0, tx_size)  # Minimum 1 ALGO
        
        # Schedule transaction (add some randomness to execution time)
        execution_delay = random.uniform(0, 30)  # 0-30 seconds delay
        target_time = current_time + execution_delay
        
        # Create transaction parameters based on type
        parameters = await self._generate_transaction_parameters(tx_type, tx_size, wallet)
        
        return TransactionPlan(
            wallet=wallet,
            tx_type=tx_type,
            size=tx_size,
            target_time=target_time,
            parameters=parameters
        )
    
    async def _generate_transaction_parameters(
        self, 
        tx_type: TransactionType, 
        size: float, 
        wallet: ManagedWallet
    ) -> Dict:
        """Generate specific parameters for a transaction type."""
        if tx_type == TransactionType.SWAP:
            # Randomly choose swap direction
            swap_x_for_y = random.choice([True, False])
            return {
                "swap_x_for_y": swap_x_for_y,
                "amount_in": int(size * 1000000),  # Convert to microAlgos
                "min_amount_out": 0,  # Will be calculated
                "slippage_tolerance": 0.005  # 0.5% slippage tolerance
            }
        
        elif tx_type == TransactionType.ADD_LIQUIDITY:
            return {
                "amount_x": int(size * 1000000 * 0.5),  # Half in asset X
                "amount_y": int(size * 1000000 * 0.5),  # Half in asset Y
                "price_lower": 0,  # Will be calculated based on current price
                "price_upper": 0,  # Will be calculated based on current price
                "concentration_factor": random.uniform(0.8, 1.5)  # Range concentration
            }
        
        elif tx_type == TransactionType.REMOVE_LIQUIDITY:
            return {
                "liquidity_amount": int(size * 1000000),
                "min_amount_x": 0,  # Will be calculated
                "min_amount_y": 0,  # Will be calculated
            }
        
        return {}
    
    async def _execute_transactions(self, transaction_plans: List[TransactionPlan]):
        """Execute a batch of transaction plans."""
        logger.info(f"Executing {len(transaction_plans)} transactions...")
        
        for plan in transaction_plans:
            try:
                success = await self._execute_single_transaction(plan)
                if success:
                    self.successful_transactions += 1
                else:
                    self.failed_transactions += 1
                
                self.total_transactions += 1
                
            except Exception as e:
                logger.error(f"Transaction execution failed: {e}")
                self.failed_transactions += 1
                self.total_transactions += 1
    
    async def _execute_single_transaction(self, plan: TransactionPlan) -> bool:
        """Execute a single transaction plan on the real blockchain."""
        try:
            result: TransactionResult = None
            
            if plan.tx_type == TransactionType.SWAP:
                result = await self._execute_swap_transaction(plan)
            elif plan.tx_type == TransactionType.ADD_LIQUIDITY:
                result = await self._execute_add_liquidity_transaction(plan)
            elif plan.tx_type == TransactionType.REMOVE_LIQUIDITY:
                result = await self._execute_remove_liquidity_transaction(plan)
            else:
                logger.error(f"Unknown transaction type: {plan.tx_type}")
                return False
            
            # Update wallet statistics
            self.wallet_manager.update_wallet_stats(
                plan.wallet.address,
                result.success,
                plan.size if result.success else 0
            )
            
            if result.success:
                logger.debug(
                    f"✅ {plan.tx_type.value} of {plan.size:.2f} ALGO from {plan.wallet.address[:8]}... "
                    f"(TxnID: {result.txn_id[:8]}... | Time: {result.execution_time:.2f}s)"
                )
            else:
                logger.warning(
                    f"❌ {plan.tx_type.value} failed from {plan.wallet.address[:8]}... "
                    f"Error: {result.error_message}"
                )
            
            return result.success
            
        except Exception as e:
            logger.error(f"Transaction execution error: {e}")
            # Update wallet statistics for failed transaction
            self.wallet_manager.update_wallet_stats(plan.wallet.address, False, 0)
            return False
    
    async def _execute_swap_transaction(self, plan: TransactionPlan) -> TransactionResult:
        """Execute a swap transaction using the pool contract."""
        params = plan.parameters
        
        # Determine swap direction and amounts
        if params.get("swap_x_for_y", True):
            asset_in_id = self.pool_client.asset_x_id or 0
            asset_out_id = self.pool_client.asset_y_id or 0
        else:
            asset_in_id = self.pool_client.asset_y_id or 0
            asset_out_id = self.pool_client.asset_x_id or 0
        
        amount_in = int(plan.size * 1_000_000)  # Convert to microunits
        min_amount_out = int(amount_in * (1 - params.get("slippage_tolerance", 0.005)))
        
        return await self.pool_client.execute_swap(
            private_key=plan.wallet.private_key,
            asset_in_id=asset_in_id,
            asset_out_id=asset_out_id,
            amount_in=amount_in,
            min_amount_out=min_amount_out
        )
    
    async def _execute_add_liquidity_transaction(self, plan: TransactionPlan) -> TransactionResult:
        """Execute an add liquidity transaction using the pool contract."""
        params = plan.parameters
        
        amount_x_desired = params.get("amount_x", int(plan.size * 1_000_000 * 0.5))
        amount_y_desired = params.get("amount_y", int(plan.size * 1_000_000 * 0.5))
        
        # Set minimum amounts with some slippage tolerance
        amount_x_min = int(amount_x_desired * 0.95)  # 5% slippage
        amount_y_min = int(amount_y_desired * 0.95)
        
        # Choose range based on concentration factor
        concentration = params.get("concentration_factor", 1.0)
        if concentration < 0.9:
            range_id = 3  # Wide range
        elif concentration < 1.1:
            range_id = 2  # Medium range 
        else:
            range_id = 1  # Tight range
        
        return await self.pool_client.add_liquidity(
            private_key=plan.wallet.private_key,
            amount_x_desired=amount_x_desired,
            amount_y_desired=amount_y_desired,
            amount_x_min=amount_x_min,
            amount_y_min=amount_y_min,
            range_id=range_id
        )
    
    async def _execute_remove_liquidity_transaction(self, plan: TransactionPlan) -> TransactionResult:
        """Execute a remove liquidity transaction using the pool contract."""
        params = plan.parameters
        
        lp_token_amount = params.get("liquidity_amount", int(plan.size * 1_000_000))
        
        # Set minimum amounts (with slippage tolerance)
        amount_x_min = params.get("min_amount_x", 0)
        amount_y_min = params.get("min_amount_y", 0)
        
        # Default to medium range if not specified
        range_id = 2
        
        return await self.pool_client.remove_liquidity(
            private_key=plan.wallet.private_key,
            lp_token_amount=lp_token_amount,
            amount_x_min=amount_x_min,
            amount_y_min=amount_y_min,
            range_id=range_id
        )
    
    def set_trading_pattern(self, pattern: str):
        """Set the current trading pattern."""
        try:
            new_pattern = TradingPattern(pattern)
            if new_pattern != self.current_pattern:
                self.current_pattern = new_pattern
                logger.info(f"Changed trading pattern to: {pattern}")
                
                # Update pattern configuration - wallet manager handles the specifics
                # Could recreate wallets if needed, but for now just update pattern
        except ValueError:
            logger.error(f"Invalid trading pattern: {pattern}")
    
    def get_metrics(self) -> Dict:
        """Get simulation metrics."""
        uptime = time.time() - self.start_time
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "total_transactions": self.total_transactions,
            "successful_transactions": self.successful_transactions,
            "failed_transactions": self.failed_transactions,
            "success_rate": (
                self.successful_transactions / max(1, self.total_transactions) * 100
            ),
            "transactions_per_minute": (
                self.total_transactions / max(1, uptime / 60)
            ),
            "current_pattern": self.current_pattern.value,
            "active_wallets": len(self.wallet_manager.wallets),
            "pending_transactions": len(self.transaction_queue),
        }
    
    def get_wallet_info(self) -> List[Dict]:
        """Get information about all wallets."""
        return self.wallet_manager.get_wallet_info()
    
    async def cleanup(self):
        """Clean up resources and save state."""
        logger.info("Cleaning up blockchain simulator...")
        if self.wallet_manager:
            await self.wallet_manager.cleanup()
