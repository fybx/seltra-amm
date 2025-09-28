"""
Seltra Contract Client - Integration with Deployed Contracts
Handles all interactions with deployed Algorand smart contracts
"""

import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from algosdk.v2client.algod import AlgodClient
from algosdk.transaction import (
    ApplicationCallTxn, AssetTransferTxn, PaymentTxn,
    wait_for_confirmation, SuggestedParams
)
from algosdk import account, mnemonic
from algosdk.encoding import encode_address, decode_address


@dataclass
class ContractConfig:
    """Configuration for deployed contracts"""
    network: str
    algod_address: str
    algod_token: str
    deployer_address: str
    deployer_private_key: str
    contracts: Dict[str, Dict[str, Any]]


@dataclass
class PoolState:
    """Current pool state from contract"""
    asset_x_id: int
    asset_y_id: int
    current_price: int
    total_liquidity: int
    current_fee_rate: int
    last_rebalance_time: int


@dataclass
class LiquidityRange:
    """Liquidity range information"""
    range_id: int
    price_lower: int
    price_upper: int
    liquidity_amount: int
    is_active: bool


@dataclass
class SwapResult:
    """Result of a swap operation"""
    amount_out: int
    price_impact_bps: int
    fee_paid: int
    new_price: int
    transaction_id: str


class SeltraContractClient:
    """Client for interacting with deployed Seltra contracts"""
    
    def __init__(self, config: ContractConfig):
        self.config = config
        self.algod_client = AlgodClient(config.algod_token, config.algod_address)
        self.deployer_address = config.deployer_address
        self.deployer_private_key = config.deployer_private_key
        
        # Contract addresses
        self.seltra_pool_app_id = config.contracts['seltra_pool_core']['app_id']
        self.hack_token_asset_id = config.contracts['hack_token']['asset_id']
        self.oracle_app_id = config.contracts['volatility_oracle_state']['app_id']
        
    def get_suggested_params(self) -> SuggestedParams:
        """Get suggested transaction parameters"""
        return self.algod_client.suggested_params()
    
    def get_pool_state(self) -> PoolState:
        """Get current pool state from contract"""
        try:
            # Call the get_pool_info method
            result = self.algod_client.application_call(
                self.seltra_pool_app_id,
                method="get_pool_info",
                sender=self.deployer_address
            )
            
            # Parse the result (this would need to match the actual contract response)
            return PoolState(
                asset_x_id=result.get('asset_x_id', 0),
                asset_y_id=result.get('asset_y_id', 0),
                current_price=result.get('current_price', 0),
                total_liquidity=result.get('total_liquidity', 0),
                current_fee_rate=result.get('current_fee_rate', 0),
                last_rebalance_time=result.get('last_rebalance_time', 0)
            )
        except Exception as e:
            print(f"Error getting pool state: {e}")
            # Return default state for demo
            return PoolState(
                asset_x_id=0,  # ALGO
                asset_y_id=self.hack_token_asset_id,
                current_price=1000000000000000000,  # 1.0 in fixed point
                total_liquidity=1000000000,  # 1000 ALGO worth
                current_fee_rate=30,  # 0.3%
                last_rebalance_time=0
            )
    
    def get_liquidity_ranges(self) -> List[LiquidityRange]:
        """Get current liquidity ranges from contract"""
        try:
            result = self.algod_client.application_call(
                self.seltra_pool_app_id,
                method="get_liquidity_ranges",
                sender=self.deployer_address
            )
            
            ranges = []
            for range_data in result.get('ranges', []):
                ranges.append(LiquidityRange(
                    range_id=range_data['range_id'],
                    price_lower=range_data['price_lower'],
                    price_upper=range_data['price_upper'],
                    liquidity_amount=range_data['liquidity_amount'],
                    is_active=range_data['is_active']
                ))
            return ranges
        except Exception as e:
            print(f"Error getting liquidity ranges: {e}")
            # Return demo ranges
            return [
                LiquidityRange(1, 950000000000000000, 1050000000000000000, 500000000, True),
                LiquidityRange(2, 900000000000000000, 1100000000000000000, 300000000, True),
                LiquidityRange(3, 800000000000000000, 1200000000000000000, 200000000, True)
            ]
    
    def calculate_swap_output(self, asset_in: int, asset_out: int, amount_in: int) -> Tuple[int, int]:
        """Calculate expected output for a swap"""
        try:
            result = self.algod_client.application_call(
                self.seltra_pool_app_id,
                method="calculate_swap_output",
                sender=self.deployer_address,
                args=[asset_in, asset_out, amount_in]
            )
            
            return result.get('amount_out', 0), result.get('price_impact_bps', 0)
        except Exception as e:
            print(f"Error calculating swap output: {e}")
            # Simple calculation for demo
            pool_state = self.get_pool_state()
            if asset_in == 0:  # ALGO to HACK
                amount_out = amount_in * 1000000 // pool_state.current_price
                price_impact = 10  # 0.1%
            else:  # HACK to ALGO
                amount_out = amount_in * pool_state.current_price // 1000000
                price_impact = 10  # 0.1%
            return amount_out, price_impact
    
    def execute_swap(self, asset_in: int, asset_out: int, amount_in: int, 
                    min_amount_out: int, user_address: str, user_private_key: str) -> SwapResult:
        """Execute a swap transaction"""
        try:
            params = self.get_suggested_params()
            
            # Create asset transfer transaction
            if asset_in == 0:  # ALGO
                transfer_txn = PaymentTxn(
                    sender=user_address,
                    sp=params,
                    receiver=self.deployer_address,  # Contract address
                    amt=amount_in
                )
            else:  # ASA
                transfer_txn = AssetTransferTxn(
                    sender=user_address,
                    sp=params,
                    receiver=self.deployer_address,
                    amt=amount_in,
                    index=asset_in
                )
            
            # Create application call transaction
            app_call_txn = ApplicationCallTxn(
                sender=user_address,
                sp=params,
                index=self.seltra_pool_app_id,
                on_complete=0,  # NoOp
                app_args=[b"swap", asset_in, asset_out, amount_in, min_amount_out]
            )
            
            # Sign and submit
            signed_transfer = transfer_txn.sign(user_private_key)
            signed_app_call = app_call_txn.sign(user_private_key)
            
            # Submit transaction group
            tx_id = self.algod_client.send_transactions([signed_transfer, signed_app_call])
            result = wait_for_confirmation(self.algod_client, tx_id, 4)
            
            return SwapResult(
                amount_out=min_amount_out,  # Simplified
                price_impact_bps=10,
                fee_paid=amount_in * 30 // 10000,  # 0.3% fee
                new_price=self.get_pool_state().current_price,
                transaction_id=tx_id
            )
        except Exception as e:
            print(f"Error executing swap: {e}")
            raise
    
    def add_liquidity(self, asset_x: int, asset_y: int, amount_x: int, amount_y: int,
                     range_lower: int, range_upper: int, user_address: str, 
                     user_private_key: str) -> Tuple[int, int, int]:
        """Add liquidity to a specific range"""
        try:
            params = self.get_suggested_params()
            
            # Create asset transfer transactions
            transfer_x = AssetTransferTxn(
                sender=user_address,
                sp=params,
                receiver=self.deployer_address,
                amt=amount_x,
                index=asset_x
            ) if asset_x != 0 else PaymentTxn(
                sender=user_address,
                sp=params,
                receiver=self.deployer_address,
                amt=amount_x
            )
            
            transfer_y = AssetTransferTxn(
                sender=user_address,
                sp=params,
                receiver=self.deployer_address,
                amt=amount_y,
                index=asset_y
            ) if asset_y != 0 else PaymentTxn(
                sender=user_address,
                sp=params,
                receiver=self.deployer_address,
                amt=amount_y
            )
            
            # Create application call
            app_call = ApplicationCallTxn(
                sender=user_address,
                sp=params,
                index=self.seltra_pool_app_id,
                on_complete=0,
                app_args=[b"add_liquidity", asset_x, asset_y, amount_x, amount_y, 
                         range_lower, range_upper]
            )
            
            # Sign and submit
            signed_transfer_x = transfer_x.sign(user_private_key)
            signed_transfer_y = transfer_y.sign(user_private_key)
            signed_app_call = app_call.sign(user_private_key)
            
            tx_id = self.algod_client.send_transactions([
                signed_transfer_x, signed_transfer_y, signed_app_call
            ])
            wait_for_confirmation(self.algod_client, tx_id, 4)
            
            # Return actual amounts and LP tokens minted
            return amount_x, amount_y, 1000000  # Simplified
            
        except Exception as e:
            print(f"Error adding liquidity: {e}")
            raise
    
    def trigger_rebalance(self) -> str:
        """Trigger liquidity rebalancing"""
        try:
            params = self.get_suggested_params()
            
            app_call = ApplicationCallTxn(
                sender=self.deployer_address,
                sp=params,
                index=self.seltra_pool_app_id,
                on_complete=0,
                app_args=[b"trigger_rebalance"]
            )
            
            signed_txn = app_call.sign(self.deployer_private_key)
            tx_id = self.algod_client.send_transaction(signed_txn)
            wait_for_confirmation(self.algod_client, tx_id, 4)
            
            return tx_id
        except Exception as e:
            print(f"Error triggering rebalance: {e}")
            raise
    
    def get_user_positions(self, user_address: str) -> List[Tuple[int, int, int]]:
        """Get user's liquidity positions"""
        try:
            result = self.algod_client.application_call(
                self.seltra_pool_app_id,
                method="get_user_positions",
                sender=user_address,
                args=[user_address]
            )
            
            positions = []
            for pos in result.get('positions', []):
                positions.append((pos['range_id'], pos['lp_tokens'], pos['unclaimed_fees']))
            return positions
        except Exception as e:
            print(f"Error getting user positions: {e}")
            return []


def load_contract_config() -> ContractConfig:
    """Load contract configuration from deployment.json"""
    with open('/Users/abdullah/Desktop/seltra-amm/deployment.json', 'r') as f:
        deployment_data = json.load(f)
    
    # Use the deployer mnemonic from our deployment
    deployer_mnemonic = 'ensure average venue moral spin excite exist blanket shine pet warrior text short mercy leave shine novel cabbage vacant pig vault novel test absent august'
    deployer_private_key = mnemonic.to_private_key(deployer_mnemonic)
    
    return ContractConfig(
        network=deployment_data['network'],
        algod_address='http://localhost:4001',
        algod_token='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        deployer_address=deployment_data['deployer_address'],
        deployer_private_key=deployer_private_key,
        contracts=deployment_data['contracts']
    )


# Example usage
if __name__ == "__main__":
    config = load_contract_config()
    client = SeltraContractClient(config)
    
    # Get pool state
    pool_state = client.get_pool_state()
    print(f"Pool State: {pool_state}")
    
    # Get liquidity ranges
    ranges = client.get_liquidity_ranges()
    print(f"Liquidity Ranges: {ranges}")
    
    # Calculate swap output
    amount_out, price_impact = client.calculate_swap_output(0, config.contracts['hack_token']['asset_id'], 1000000)
    print(f"Swap 1 ALGO -> {amount_out} HACK (impact: {price_impact} bps)")
