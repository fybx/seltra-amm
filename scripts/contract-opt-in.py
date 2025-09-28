#!/usr/bin/env python3
"""
Opt-in contract to HACK token
"""

import os
import sys
import json
import algosdk
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction
from algosdk.transaction import ApplicationCallTxn, AssetTransferTxn

def main():
    print("🔄 Contract Asset Opt-in")
    print("=" * 30)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Algorand client
    algod_address = "https://testnet-api.algonode.cloud"
    algod_token = ""
    algod_client = algod.AlgodClient(algod_token, algod_address)
    
    # Account setup
    mnemonic_phrase = os.getenv('DEPLOYER_MNEMONIC')
    private_key = mnemonic.to_private_key(mnemonic_phrase)
    address = account.address_from_private_key(private_key)
    
    print(f"📋 Using account: {address}")
    
    # Contract IDs (latest)
    app_id = 746545814
    hack_asset_id = 746545813
    
    print(f"🔗 Pool App ID: {app_id}")
    print(f"🪙 HACK Asset ID: {hack_asset_id}")
    
    # Opt-in contract to HACK token via application call
    print("\n🔄 Opting contract into HACK token via app call...")
    try:
        params = algod_client.suggested_params()

        # Create application call transaction with foreign assets
        app_call_txn = ApplicationCallTxn(
            sender=address,
            sp=params,
            index=app_id,
            on_complete=transaction.OnComplete.NoOpOC,
            app_args=["opt_in"],
            foreign_assets=[hack_asset_id]  # Include asset in foreign assets
        )

        signed_txn = app_call_txn.sign(private_key)
        tx_id = algod_client.send_transaction(signed_txn)
        confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id, 4)

        print(f"✅ Contract opt-in successful!")
        print(f"📝 Transaction ID: {tx_id}")
        print(f"🔗 Explorer: https://testnet.algoexplorer.io/tx/{tx_id}")

    except Exception as e:
        print(f"❌ Contract opt-in failed: {e}")
        
        # Try funding the contract with HACK tokens directly
        print("\n🔄 Trying to fund contract with HACK tokens...")
        try:
            fund_txn = AssetTransferTxn(
                sender=address,
                sp=params,
                receiver=algosdk.logic.get_application_address(app_id),
                amt=10000000000,  # 10B HACK tokens
                index=hack_asset_id
            )
            
            signed_txn = fund_txn.sign(private_key)
            tx_id = algod_client.send_transaction(signed_txn)
            confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id, 4)
            
            print(f"✅ Contract funding successful!")
            print(f"📝 Transaction ID: {tx_id}")
            
        except Exception as e2:
            print(f"❌ Contract funding failed: {e2}")

if __name__ == "__main__":
    main()
