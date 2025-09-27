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
class WalletProfile:
    """Trader wallet profile with behavior characteristics."""
    private_key: str
    address: str
    mnemonic_phrase: str
    pattern: TradingPattern
    balance_algo: int = 1000000  # 1 ALGO in microAlgos
    trade_frequency: float = 1.0  # trades per minute
    avg_trade_size: float = 100.0  # average trade size in ALGO
    volatility_sensitivity: float = 1.0  # how much volatility affects behavior


@dataclass
class TransactionPlan:
    """Planned transaction with timing and parameters."""
    wallet: WalletProfile
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
        market_simulator=None
    ):
        """
        Initialize the blockchain transaction simulator.
        
        Args:
            algod_address: Algorand node address
            algod_token: Algorand node token
            num_wallets: Number of wallets to create for simulation
        """
        self.algod_address = algod_address
        self.algod_token = algod_token
        self.num_wallets = num_wallets
        self.market_simulator = market_simulator
        
        # Initialize Algorand client
        self.algod_client = algod.AlgodClient(algod_token, algod_address)
        
        # Simulation state
        self.wallets: List[WalletProfile] = []
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
        
        # Asset IDs (will be set when connecting to blockchain)
        self.asset_x_id = None  # ETH-like asset
        self.asset_y_id = None  # USDC-like asset
        self.pool_app_id = None  # Seltra pool application
        
    async def initialize(self):
        """Initialize the simulator - create wallets and connect to blockchain."""
        logger.info("Initializing Algorand Transaction Simulator...")
        
        # Test connection to Algorand node
        try:
            status = self.algod_client.status()
            logger.info(f"Connected to Algorand node - Round: {status.get('last-round', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to connect to Algorand node: {e}")
            raise
        
        # Create wallets
        await self._create_wallets()
        
        # TODO: Fund wallets from faucet (in a real scenario)
        # TODO: Create test assets if they don't exist
        
        logger.info(f"Simulation initialized with {len(self.wallets)} wallets")
    
    async def _create_wallets(self):
        """Create wallets with different trading profiles."""
        self.wallets.clear()
        
        current_config = self.pattern_config[self.current_pattern]
        whale_count = max(1, int(self.num_wallets * current_config["whale_ratio"]))
        
        for i in range(self.num_wallets):
            # Generate new account
            private_key, address = account.generate_account()
            mnemonic_phrase = mnemonic.from_private_key(private_key)
            
            # Assign trading pattern
            if i < whale_count:
                pattern = TradingPattern.WHALE
                balance = 10000000  # 10 ALGO
                trade_freq = 0.2    # Less frequent but larger trades
                avg_size = 1000.0   # 1000 ALGO average
                volatility_sens = 0.5  # Less reactive to volatility
            else:
                pattern = TradingPattern.RETAIL
                balance = 1000000   # 1 ALGO
                trade_freq = current_config["base_frequency"]
                avg_size = random.uniform(10, 100)  # 10-100 ALGO
                volatility_sens = 1.0 + random.uniform(-0.3, 0.7)  # Varied sensitivity
            
            wallet = WalletProfile(
                private_key=private_key,
                address=address,
                mnemonic_phrase=mnemonic_phrase,
                pattern=pattern,
                balance_algo=balance,
                trade_frequency=trade_freq,
                avg_trade_size=avg_size,
                volatility_sensitivity=volatility_sens
            )
            
            self.wallets.append(wallet)
        
        logger.info(f"Created {len(self.wallets)} wallets ({whale_count} whales, {self.num_wallets - whale_count} retail)")
    
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
        
        for wallet in self.wallets:
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
    
    async def _create_transaction_plan(self, wallet: WalletProfile, current_time: float) -> Optional[TransactionPlan]:
        """Create a specific transaction plan for a wallet."""
        # Choose transaction type based on wallet pattern
        tx_types = [TransactionType.SWAP, TransactionType.ADD_LIQUIDITY, TransactionType.REMOVE_LIQUIDITY]
        
        if wallet.pattern == TradingPattern.WHALE:
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
        wallet: WalletProfile
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
        """Execute a single transaction plan."""
        try:
            # For now, simulate transaction execution without actual blockchain calls
            # This allows testing the logic before the contracts are deployed
            
            execution_time = random.uniform(0.5, 2.0)  # Simulate network delay
            await asyncio.sleep(execution_time)
            
            # Simulate occasional failures (network issues, insufficient funds, etc.)
            failure_rate = 0.05  # 5% failure rate
            if random.random() < failure_rate:
                logger.debug(f"Simulated transaction failure for {plan.wallet.address[:8]}...")
                return False
            
            logger.debug(f"Executed {plan.tx_type.value} of size {plan.size:.2f} from {plan.wallet.address[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Transaction execution error: {e}")
            return False
    
    def set_trading_pattern(self, pattern: str):
        """Set the current trading pattern."""
        try:
            new_pattern = TradingPattern(pattern)
            if new_pattern != self.current_pattern:
                self.current_pattern = new_pattern
                logger.info(f"Changed trading pattern to: {pattern}")
                
                # Recreate wallets with new pattern
                asyncio.create_task(self._create_wallets())
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
            "active_wallets": len(self.wallets),
            "pending_transactions": len(self.transaction_queue),
        }
    
    def get_wallet_info(self) -> List[Dict]:
        """Get information about all wallets."""
        return [
            {
                "address": wallet.address,
                "pattern": wallet.pattern.value,
                "balance_algo": wallet.balance_algo / 1000000,  # Convert to ALGO
                "trade_frequency": wallet.trade_frequency,
                "avg_trade_size": wallet.avg_trade_size,
                "volatility_sensitivity": wallet.volatility_sensitivity
            }
            for wallet in self.wallets
        ]
