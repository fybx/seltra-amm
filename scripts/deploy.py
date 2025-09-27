#!/usr/bin/env python3
"""
Seltra AMM Contract Deployment Script
Based on NEW Algorand Developer Portal: https://dev.algorand.co/getting-started/introduction/
"""

import os
import sys
from pathlib import Path
from algokit_utils import (
    ApplicationClient,
    ApplicationSpecification,
    get_algod_client,
    get_indexer_client,
    get_account,
    get_localnet_default_account,
    is_localnet,
)
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from algosdk.account import generate_account
from algosdk.mnemonic import to_private_key
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def get_client_config():
    """Get client configuration from environment"""
    return {
        "algod_client": get_algod_client(),
        "indexer_client": get_indexer_client(),
    }

def create_test_account():
    """Create a test account for deployment"""
    if is_localnet():
        # Use AlgoKit LocalNet default account
        account = get_localnet_default_account()
        print(f"🔑 Using AlgoKit LocalNet default account:")
        print(f"Address: {account.address}")
        return account.private_key, account.address, None
    else:
        # Generate new account for testnet
        private_key, address = generate_account()
        mnemonic = to_private_key(private_key)
        
        print(f"🔑 Generated test account:")
        print(f"Address: {address}")
        print(f"Private Key: {private_key}")
        print(f"Mnemonic: {mnemonic}")
        
        return private_key, address, mnemonic

def deploy_contract(contract_path: str, client_config: dict):
    """Deploy a smart contract"""
    try:
        # Load contract specification
        with open(contract_path, 'r') as f:
            contract_spec = json.load(f)
        
        app_spec = ApplicationSpecification.from_json(contract_spec)
        
        # Create application client
        app_client = ApplicationClient(
            algod_client=client_config["algod_client"],
            app_spec=app_spec,
        )
        
        # Deploy the application
        print(f"🚀 Deploying contract: {contract_path}")
        app_id, tx_id = app_client.create()
        
        print(f"✅ Contract deployed successfully!")
        print(f"App ID: {app_id}")
        print(f"Transaction ID: {tx_id}")
        
        return app_id, tx_id
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return None, None

def main():
    """Main deployment function"""
    print("🚀 Seltra AMM Contract Deployment")
    print("=" * 50)
    
    # Check if contracts directory exists
    contracts_dir = project_root / "contracts"
    if not contracts_dir.exists():
        print("❌ Contracts directory not found!")
        print("Please create contracts first.")
        return
    
    # Get client configuration
    try:
        client_config = get_client_config()
        print("✅ Connected to Algorand network")
    except Exception as e:
        print(f"❌ Failed to connect to Algorand network: {e}")
        print("Make sure your development environment is running!")
        return
    
    # Create test account if needed
    if not os.getenv("TEST_WALLET_ADDRESS"):
        print("\n🔑 Creating test account...")
        private_key, address, mnemonic = create_test_account()
        
        print("\n⚠️  IMPORTANT: Save these credentials!")
        print("Add them to your .env file:")
        print(f"TEST_WALLET_ADDRESS={address}")
        print(f"TEST_WALLET_PRIVATE_KEY={private_key}")
        print(f"TEST_WALLET_MNEMONIC={mnemonic}")
        print("\nPress Enter to continue...")
        input()
    
    # Deploy contracts
    contract_files = list(contracts_dir.glob("*.json"))
    
    if not contract_files:
        print("❌ No contract files found in contracts/ directory")
        print("Please create contracts first using AlgoKit.")
        return
    
    deployed_contracts = []
    
    for contract_file in contract_files:
        print(f"\n📄 Processing: {contract_file.name}")
        app_id, tx_id = deploy_contract(str(contract_file), client_config)
        
        if app_id:
            deployed_contracts.append({
                "name": contract_file.stem,
                "app_id": app_id,
                "tx_id": tx_id,
                "file": contract_file.name
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Deployment Summary")
    print("=" * 50)
    
    if deployed_contracts:
        for contract in deployed_contracts:
            print(f"✅ {contract['name']}: App ID {contract['app_id']}")
        
        print(f"\n🎉 Successfully deployed {len(deployed_contracts)} contracts!")
        
        # Save deployment info
        deployment_info = {
            "network": "testnet",
            "deployment_time": str(pd.Timestamp.now()),
            "contracts": deployed_contracts
        }
        
        with open("deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        print("📄 Deployment info saved to deployment_info.json")
        
    else:
        print("❌ No contracts were deployed successfully")
    
    print("\n📚 Next steps:")
    print("1. Test your deployed contracts")
    print("2. Update frontend with contract addresses")
    print("3. Run simulation environment")

if __name__ == "__main__":
    main()
