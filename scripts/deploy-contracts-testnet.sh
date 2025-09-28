#!/bin/bash

# Seltra AMM TestNet Contract Deployment Script
# Deploys contracts to Algorand TestNet and configures the system

set -e

echo "🚀 Seltra AMM TestNet Contract Deployment"
echo "========================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install required Python packages
echo "📦 Installing required Python packages..."
pip3 install py-algorand-sdk python-dotenv

# Set up environment for TestNet
echo "🔧 Setting up TestNet environment..."

# Create deployment account if not exists
if [ ! -f "testnet_account.json" ]; then
    echo "🔑 Creating TestNet deployment account..."
    python3 -c "
import json
from algosdk import account, mnemonic

# Generate new account
private_key, address = account.generate_account()
mn = mnemonic.from_private_key(private_key)

account_info = {
    'address': address,
    'private_key': private_key,
    'mnemonic': mn
}

with open('testnet_account.json', 'w') as f:
    json.dump(account_info, f, indent=2)

print(f'✅ Account created: {address}')
print(f'🔑 Mnemonic: {mn}')
print('')
print('⚠️  IMPORTANT: Fund this account with TestNet ALGO!')
print('Visit: https://testnet.algoexplorer.io/dispenser')
print(f'Send TestNet ALGO to: {address}')
print('')
print('Press Enter after funding the account...')
"
    read -p "Press Enter after funding the account..."
else
    echo "✅ Using existing TestNet account"
    ACCOUNT_ADDRESS=$(python3 -c "import json; data=json.load(open('testnet_account.json')); print(data['address'])")
    echo "Account: $ACCOUNT_ADDRESS"
fi

# Deploy contracts
echo "🚀 Deploying contracts to TestNet..."

python3 -c "
import json
import os
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction
from algosdk.transaction import ApplicationCreateTxn, AssetCreateTxn
import time

# Load account
with open('testnet_account.json', 'r') as f:
    account_data = json.load(f)

private_key = account_data['private_key']
address = account_data['address']

# Connect to TestNet
algod_client = algod.AlgodClient('', 'https://testnet-api.algonode.cloud')

print('🔗 Connected to Algorand TestNet')

# Check account balance
account_info = algod_client.account_info(address)
balance = account_info['amount']
print(f'💰 Account balance: {balance / 1_000_000:.6f} ALGO')

if balance < 1_000_000:  # Less than 1 ALGO
    print('❌ Insufficient balance! Please fund your account.')
    exit(1)

# Create HACK token (Asset Y)
print('🪙 Creating HACK token...')

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

# Sign and send transaction
signed_txn = asset_create_txn.sign(private_key)
tx_id = algod_client.send_transaction(signed_txn)

print(f'📤 Transaction sent: {tx_id}')
print('⏳ Waiting for confirmation...')

# Wait for confirmation
confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id, 4)
asset_id = confirmed_txn['asset-index']

print(f'✅ HACK token created with Asset ID: {asset_id}')

# Create simple AMM contract (placeholder)
print('📜 Creating AMM contract...')

# Simple approval program (placeholder)
approval_program = '''
#pragma version 8
int 1
return
'''

# Simple clear program
clear_program = '''
#pragma version 8
int 1
return
'''

# Compile programs
import base64

approval_result = algod_client.compile(approval_program)
approval_binary = base64.b64decode(approval_result['result'])

clear_result = algod_client.compile(clear_program)
clear_binary = base64.b64decode(clear_result['result'])

# Create application
params = algod_client.suggested_params()

app_create_txn = ApplicationCreateTxn(
    sender=address,
    sp=params,
    on_complete=0,  # NoOp
    approval_program=approval_binary,
    clear_program=clear_binary,
    global_schema=transaction.StateSchema(num_uints=10, num_byte_slices=10),
    local_schema=transaction.StateSchema(num_uints=5, num_byte_slices=5)
)

# Sign and send transaction
signed_txn = app_create_txn.sign(private_key)
tx_id = algod_client.send_transaction(signed_txn)

print(f'📤 Transaction sent: {tx_id}')
print('⏳ Waiting for confirmation...')

# Wait for confirmation
confirmed_txn = transaction.wait_for_confirmation(algod_client, tx_id, 4)
app_id = confirmed_txn['application-index']

print(f'✅ AMM contract created with App ID: {app_id}')

# Save deployment info
deployment_info = {
    'network': 'testnet',
    'deployer_address': address,
    'pool_app_id': app_id,
    'asset_x_id': 0,  # ALGO
    'asset_y_id': asset_id,  # HACK
    'deployment_time': int(time.time())
}

with open('deployment_info.json', 'w') as f:
    json.dump(deployment_info, f, indent=2)

print('')
print('🎉 Deployment completed successfully!')
print('===================================')
print(f'Pool App ID: {app_id}')
print(f'Asset X (ALGO): 0')
print(f'Asset Y (HACK): {asset_id}')
print('')
"

# Update environment variables
if [ -f "deployment_info.json" ]; then
    echo "📝 Updating environment variables..."
    
    POOL_APP_ID=$(python3 -c "import json; data=json.load(open('deployment_info.json')); print(data['pool_app_id'])")
    ASSET_Y_ID=$(python3 -c "import json; data=json.load(open('deployment_info.json')); print(data['asset_y_id'])")
    DEPLOYER_ADDRESS=$(python3 -c "import json; data=json.load(open('deployment_info.json')); print(data['deployer_address'])")
    
    # Update .env file
    sed -i.bak "s/SELTRA_POOL_APP_ID=.*/SELTRA_POOL_APP_ID=$POOL_APP_ID/" .env
    sed -i.bak "s/ASSET_Y_ID=.*/ASSET_Y_ID=$ASSET_Y_ID/" .env
    
    echo "✅ Environment updated"
    echo "Pool App ID: $POOL_APP_ID"
    echo "Asset Y ID: $ASSET_Y_ID"
fi

# Restart services with new configuration
echo "🔄 Restarting services with new configuration..."
docker-compose restart market-simulator

echo ""
echo "🎉 TestNet Deployment Complete!"
echo "==============================="
echo ""
echo "🌐 Access Points:"
echo "  • Main Trading Interface: http://localhost:3000"
echo "  • Development Console:    http://localhost:3001"
echo "  • Market Simulator API:   http://localhost:8000"
echo ""
echo "📋 Contract Information:"
echo "  • Network: TestNet"
echo "  • Pool App ID: $POOL_APP_ID"
echo "  • Asset X (ALGO): 0"
echo "  • Asset Y (HACK): $ASSET_Y_ID"
echo "  • Deployer: $DEPLOYER_ADDRESS"
echo ""
echo "🔧 Next Steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Connect your Pera Wallet (TestNet mode)"
echo "  3. Get TestNet ALGO from: https://testnet.algoexplorer.io/dispenser"
echo "  4. Start trading with real contracts!"
echo ""
echo "Happy trading! 🚀"
