#!/usr/bin/env python3
"""
Test script for onchain swap functionality
Tests ALGO -> HACK and HACK -> ALGO swaps
"""

import os
import sys
import json
import base64
import algosdk
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction
from algosdk.transaction import ApplicationCallTxn, PaymentTxn, AssetTransferTxn

def main():
    print("🧪 Testing Onchain Swap Functionality")
    print("=" * 50)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Algorand client
    algod_address = "https://testnet-api.algonode.cloud"
    algod_token = ""
    algod_client = algod.AlgodClient(algod_token, algod_address)
    
    # Account setup
    mnemonic_phrase = os.getenv('DEPLOYER_MNEMONIC')
    if not mnemonic_phrase:
        print("❌ DEPLOYER_MNEMONIC not found in environment")
        return
    
    private_key = mnemonic.to_private_key(mnemonic_phrase)
    address = account.address_from_private_key(private_key)
    
    print(f"📋 Using account: {address}")
    
    # Contract IDs (use latest deployed)
    app_id = 746545814  # Latest working contract
    hack_asset_id = 746545813  # Latest HACK token
    
    print(f"🔗 Pool App ID: {app_id}")
    print(f"🪙 HACK Asset ID: {hack_asset_id}")
    
    # Check account balance
    account_info = algod_client.account_info(address)
    algo_balance = account_info['amount'] / 1e6
    print(f"💰 ALGO Balance: {algo_balance:.6f}")
    
    # Check HACK balance
    hack_balance = 0
    for asset in account_info.get('assets', []):
        if asset['asset-id'] == hack_asset_id:
            hack_balance = asset['amount']
            break
    print(f"🎯 HACK Balance: {hack_balance}")
    
    # Test 1: Opt-in to HACK token if needed
    if hack_balance == 0 and not any(asset['asset-id'] == hack_asset_id for asset in account_info.get('assets', [])):
        print("\n🔄 Opting in to HACK token...")
        try:
            params = algod_client.suggested_params()
            opt_in_txn = AssetTransferTxn(
                sender=address,
                sp=params,
                receiver=address,
                amt=0,
                index=hack_asset_id
            )
            signed_txn = opt_in_txn.sign(private_key)
            tx_id = algod_client.send_transaction(signed_txn)
            transaction.wait_for_confirmation(algod_client, tx_id, 4)
            print("✅ HACK token opt-in successful")
        except Exception as e:
            print(f"❌ Opt-in failed: {e}")
            return
    
    # Test 2: ALGO -> HACK swap
    print("\n🔄 Testing ALGO -> HACK swap...")
    try:
        params = algod_client.suggested_params()
        swap_amount = 100000  # 0.1 ALGO
        
        # Create payment transaction (ALGO to contract)
        payment_txn = PaymentTxn(
            sender=address,
            sp=params,
            receiver=algosdk.logic.get_application_address(app_id),
            amt=swap_amount
        )
        
        # Create application call transaction
        app_call_txn = ApplicationCallTxn(
            sender=address,
            sp=params,
            index=app_id,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=["swap", 0, hack_asset_id, swap_amount],  # ALGO -> HACK
            foreign_assets=[hack_asset_id]  # Include HACK asset in foreign assets
        )
        
        # Group transactions
        transactions = [payment_txn, app_call_txn]
        gid = transaction.calculate_group_id(transactions)
        for txn in transactions:
            txn.group = gid
        
        # Sign transactions
        signed_txns = [txn.sign(private_key) for txn in transactions]
        
        # Send transaction group
        tx_id = algod_client.send_transactions(signed_txns)
        confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id, 4)
        
        print(f"✅ ALGO -> HACK swap successful!")
        print(f"📝 Transaction ID: {tx_id}")
        print(f"🔗 Explorer: https://testnet.algoexplorer.io/tx/{tx_id}")
        
    except Exception as e:
        print(f"❌ ALGO -> HACK swap failed: {e}")
    
    # Check balances after swap
    print("\n📊 Checking balances after swap...")
    account_info = algod_client.account_info(address)
    new_algo_balance = account_info['amount'] / 1e6
    new_hack_balance = 0
    for asset in account_info.get('assets', []):
        if asset['asset-id'] == hack_asset_id:
            new_hack_balance = asset['amount']
            break
    
    print(f"💰 New ALGO Balance: {new_algo_balance:.6f} (change: {new_algo_balance - algo_balance:.6f})")
    print(f"🎯 New HACK Balance: {new_hack_balance} (change: {new_hack_balance - hack_balance})")
    
    print("\n🎉 Onchain swap test completed!")

if __name__ == "__main__":
    main()
