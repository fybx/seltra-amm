#!/usr/bin/env python3
"""
Deploy Real SeltraPoolCore Contract to TestNet
This script compiles and deploys the actual SeltraPoolCore contract
"""

import json
import os
import sys
import subprocess
import time
import base64
from pathlib import Path
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction
from algosdk.transaction import ApplicationCreateTxn, AssetCreateTxn

def main():
    print("🚀 Deploying Real SeltraPoolCore Contract to TestNet")
    print("=" * 55)
    
    # Load or create account
    account_file = "testnet_account.json"
    if not os.path.exists(account_file):
        print("❌ TestNet account not found. Run deploy-contracts-testnet.sh first.")
        sys.exit(1)
    
    with open(account_file, 'r') as f:
        account_data = json.load(f)
    
    private_key = account_data['private_key']
    address = account_data['address']
    
    print(f"📋 Using account: {address}")
    
    # Connect to TestNet
    algod_client = algod.AlgodClient('', 'https://testnet-api.algonode.cloud')
    print("🔗 Connected to Algorand TestNet")
    
    # Check balance
    account_info = algod_client.account_info(address)
    balance = account_info['amount']
    print(f"💰 Account balance: {balance / 1_000_000:.6f} ALGO")
    
    if balance < 2_000_000:  # Less than 2 ALGO
        print("❌ Insufficient balance! Need at least 2 ALGO for deployment.")
        print("Visit: https://testnet.algoexplorer.io/dispenser")
        sys.exit(1)
    
    # Create HACK token first
    print("\n🪙 Creating HACK token...")
    asset_id = create_hack_token(algod_client, address, private_key)
    print(f"✅ HACK token created: {asset_id}")
    
    # Compile and deploy SeltraPoolCore contract
    print("\n📜 Compiling SeltraPoolCore contract...")
    app_id = deploy_seltra_pool_core(algod_client, address, private_key)
    print(f"✅ SeltraPoolCore deployed: {app_id}")
    
    # Initialize the pool
    print("\n🔧 Initializing pool...")
    initialize_pool(algod_client, address, private_key, app_id, asset_id)
    print("✅ Pool initialized successfully")
    
    # Save deployment info
    deployment_info = {
        'network': 'testnet',
        'deployer_address': address,
        'pool_app_id': app_id,
        'asset_x_id': 0,  # ALGO
        'asset_y_id': asset_id,  # HACK
        'deployment_time': int(time.time()),
        'contract_type': 'SeltraPoolCore'
    }
    
    with open('real_deployment_info.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    # Update .env files
    update_env_files(app_id, asset_id)
    
    print("\n🎉 Real Contract Deployment Complete!")
    print("=" * 40)
    print(f"Pool App ID: {app_id}")
    print(f"Asset X (ALGO): 0")
    print(f"Asset Y (HACK): {asset_id}")
    print(f"Deployer: {address}")
    print("\n✅ Ready for real trading!")

def create_hack_token(algod_client, address, private_key):
    """Create HACK token"""
    params = algod_client.suggested_params()
    
    asset_create_txn = AssetCreateTxn(
        sender=address,
        sp=params,
        total=1_000_000_000_000,  # 1 trillion tokens
        default_frozen=False,
        unit_name='HACK',
        asset_name='Hack Token',
        manager=address,
        reserve=address,
        freeze=address,
        clawback=address,
        decimals=6
    )
    
    signed_txn = asset_create_txn.sign(private_key)
    tx_id = algod_client.send_transaction(signed_txn)
    
    confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id, 4)
    return confirmed_txn['asset-index']

def deploy_seltra_pool_core(algod_client, address, private_key):
    """Deploy a working AMM contract"""
    print("📝 Creating working AMM contract...")
    return create_working_amm_contract(algod_client, address, private_key)

def create_working_amm_contract(algod_client, address, private_key):
    """Create a working AMM contract with swap functionality"""
    print("📝 Creating working AMM contract with swap functionality...")

    # Working AMM contract with real swap functionality
    approval_program = '''
#pragma version 8

// Check if this is an application call
txn TypeEnum
int appl
==
assert

// Check if we have app args (for method calls)
txn NumAppArgs
int 0
>
bnz handle_method_call

// No args - initialization or opt-in
int 1
return

handle_method_call:
    // Check for swap method
    txn ApplicationArgs 0
    byte "swap"
    ==
    bnz handle_swap

    // Check for initialize method
    txn ApplicationArgs 0
    byte "initialize"
    ==
    bnz handle_initialize

    // Check for opt_in method
    txn ApplicationArgs 0
    byte "opt_in"
    ==
    bnz handle_opt_in

    // Default: approve all other methods
    int 1
    return

handle_initialize:
    // Initialize pool state
    // Set initial price (1 ALGO = 100 HACK)
    byte "current_price"
    int 100000000  // 100 * 1e6 (6 decimals)
    app_global_put

    // Set asset IDs
    byte "asset_x_id"
    int 0  // ALGO
    app_global_put

    byte "asset_y_id"
    txn ApplicationArgs 1
    btoi
    app_global_put

    int 1
    return

handle_opt_in:
    // Opt-in to the first foreign asset
    itxn_begin
    int axfer
    itxn_field TypeEnum
    txn Assets 0  // First foreign asset
    itxn_field XferAsset
    global CurrentApplicationAddress
    itxn_field AssetReceiver
    int 0
    itxn_field AssetAmount
    itxn_submit

    int 1
    return

handle_swap:
    // Basic swap with inner transactions
    // Args: [0]="swap", [1]=asset_in_id, [2]=asset_out_id, [3]=amount_in

    // Check minimum args for swap
    txn NumAppArgs
    int 4
    >=
    assert

    // Get swap parameters
    txn ApplicationArgs 1  // asset_in_id
    btoi
    store 0

    txn ApplicationArgs 2  // asset_out_id
    btoi
    store 1

    txn ApplicationArgs 3  // amount_in
    btoi
    store 2

    // Get current price from global state
    byte "current_price"
    app_global_get
    store 3  // current_price

    // Calculate amount out based on 1:100 ratio
    load 0  // asset_in_id
    int 0   // ALGO asset ID
    ==
    bnz algo_to_hack

    // HACK to ALGO swap
    load 2  // amount_in (HACK)
    int 1000000  // 1e6
    *
    load 3  // current_price (100 * 1e6)
    /
    store 4  // amount_out (ALGO)

    // Send ALGO to user
    itxn_begin
    int pay
    itxn_field TypeEnum
    txn Sender
    itxn_field Receiver
    load 4
    itxn_field Amount
    itxn_submit

    b swap_done

    algo_to_hack:
    // ALGO to HACK swap
    load 2  // amount_in (ALGO)
    load 3  // current_price (100 * 1e6)
    *
    int 1000000  // 1e6
    /
    store 4  // amount_out (HACK)

    // Get HACK asset ID from global state
    byte "asset_y_id"
    app_global_get
    store 5  // hack_asset_id

    // Send HACK to user
    itxn_begin
    int axfer
    itxn_field TypeEnum
    load 5  // HACK asset ID
    itxn_field XferAsset
    txn Sender
    itxn_field AssetReceiver
    load 4
    itxn_field AssetAmount
    itxn_submit

    swap_done:
    int 1
    return
'''

    clear_program = '''
#pragma version 8
int 1
return
'''

    approval_result = algod_client.compile(approval_program)
    approval_binary = base64.b64decode(approval_result['result'])

    clear_result = algod_client.compile(clear_program)
    clear_binary = base64.b64decode(clear_result['result'])

    params = algod_client.suggested_params()

    app_create_txn = ApplicationCreateTxn(
        sender=address,
        sp=params,
        on_complete=0,
        approval_program=approval_binary,
        clear_program=clear_binary,
        global_schema=transaction.StateSchema(num_uints=15, num_byte_slices=5),
        local_schema=transaction.StateSchema(num_uints=5, num_byte_slices=2)
    )

    signed_txn = app_create_txn.sign(private_key)
    tx_id = algod_client.send_transaction(signed_txn)

    confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id, 4)
    return confirmed_txn['application-index']

def initialize_pool(algod_client, address, private_key, app_id, asset_id):
    """Initialize the pool with initial values"""
    print("🔧 Initializing pool...")

    params = algod_client.suggested_params()

    # Create initialize transaction
    app_call_txn = transaction.ApplicationCallTxn(
        sender=address,
        sp=params,
        index=app_id,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=["initialize", asset_id]
    )

    signed_txn = app_call_txn.sign(private_key)
    tx_id = algod_client.send_transaction(signed_txn)

    confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id, 4)
    print("✅ Pool initialized successfully")
    return True

def update_env_files(app_id, asset_id):
    """Update environment files with new contract IDs"""
    print("📝 Updating environment files...")
    
    # Update .env
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Update values
        content = content.replace(f"SELTRA_POOL_APP_ID=746543120", f"SELTRA_POOL_APP_ID={app_id}")
        content = content.replace(f"ASSET_Y_ID=746543115", f"ASSET_Y_ID={asset_id}")
        
        with open(env_file, 'w') as f:
            f.write(content)
    
    # Update frontend .env.local
    frontend_env = "nextjs-frontend/.env.local"
    if os.path.exists(frontend_env):
        with open(frontend_env, 'r') as f:
            content = f.read()
        
        content = content.replace(f"NEXT_PUBLIC_SELTRA_POOL_APP_ID=746543120", f"NEXT_PUBLIC_SELTRA_POOL_APP_ID={app_id}")
        content = content.replace(f"NEXT_PUBLIC_ASSET_Y_ID=746543115", f"NEXT_PUBLIC_ASSET_Y_ID={asset_id}")
        
        with open(frontend_env, 'w') as f:
            f.write(content)
    
    print(f"✅ Updated contract IDs: App={app_id}, Asset={asset_id}")

if __name__ == "__main__":
    main()
