'use client';

import React, { useState, useEffect } from 'react';
import { useWallet } from '@/providers/WalletProvider';
import { getContractConfig } from '@/utils/config';
import algosdk from 'algosdk';

interface AssetOptInProps {
  onOptInComplete?: () => void;
}

const AssetOptIn: React.FC<AssetOptInProps> = ({ onOptInComplete }) => {
  const { wallet, peraWallet } = useWallet();
  const [isOptedIn, setIsOptedIn] = useState(false);
  const [isOptingIn, setIsOptingIn] = useState(false);
  const [isChecking, setIsChecking] = useState(true);
  const contractConfig = getContractConfig();

  const checkOptInStatus = async () => {
    if (!wallet.isConnected || !wallet.address) {
      setIsChecking(false);
      return;
    }

    try {
      const algodClient = new algosdk.Algodv2('', 'https://testnet-api.algonode.cloud', '');
      const accountInfo = await algodClient.accountInformation(wallet.address).do();
      
      // Check if account is opted into HACK token
      const hackAssetId = contractConfig.assetYId;
      const isOptedIntoHack = accountInfo.assets?.some((asset: any) => asset['asset-id'] === hackAssetId);
      
      setIsOptedIn(!!isOptedIntoHack);
    } catch (error) {
      console.error('Error checking opt-in status:', error);
    } finally {
      setIsChecking(false);
    }
  };

  const handleOptIn = async () => {
    if (!wallet.isConnected || !wallet.address || !peraWallet) return;

    setIsOptingIn(true);
    try {
      const algodClient = new algosdk.Algodv2('', 'https://testnet-api.algonode.cloud', '');
      const suggestedParams = await algodClient.getTransactionParams().do();
      
      // Create asset opt-in transaction
      const optInTxn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
        sender: wallet.address,
        receiver: wallet.address,
        amount: 0,
        assetIndex: contractConfig.assetYId,
        suggestedParams
      });

      // Sign and send transaction
      const signedTxns = await peraWallet.signTransaction([[{ txn: optInTxn, signers: [wallet.address] }]]);
      const response = await algodClient.sendRawTransaction(signedTxns[0]).do();
      
      // Wait for confirmation
      await algosdk.waitForConfirmation(algodClient, response.txid, 4);
      
      setIsOptedIn(true);
      onOptInComplete?.();
    } catch (error) {
      console.error('Opt-in error:', error);
    } finally {
      setIsOptingIn(false);
    }
  };

  useEffect(() => {
    checkOptInStatus();
  }, [wallet.isConnected, wallet.address]);

  if (!wallet.isConnected) {
    return null;
  }

  if (isChecking) {
    return (
      <div style={{
        padding: '16px',
        background: 'linear-gradient(135deg, #0066FF 0%, #004BB5 100%)',
        borderRadius: '12px',
        color: 'white',
        textAlign: 'center',
        margin: '16px 0'
      }}>
        <div style={{ fontSize: '14px' }}>Checking HACK token opt-in status...</div>
      </div>
    );
  }

  if (isOptedIn) {
    return (
      <div style={{
        padding: '12px',
        background: 'linear-gradient(135deg, #00C851 0%, #007E33 100%)',
        borderRadius: '8px',
        color: 'white',
        textAlign: 'center',
        margin: '16px 0',
        fontSize: '14px'
      }}>
        ✅ HACK Token Opt-in Complete
      </div>
    );
  }

  return (
    <div style={{
      padding: '16px',
      background: 'linear-gradient(135deg, #FFD700 0%, #FFA000 100%)',
      borderRadius: '12px',
      color: '#333',
      margin: '16px 0'
    }}>
      <div style={{ marginBottom: '12px', fontWeight: 'bold' }}>
        HACK Token Opt-in Required
      </div>
      <div style={{ fontSize: '14px', marginBottom: '16px', lineHeight: '1.4' }}>
        To receive HACK tokens from swaps, you need to opt-in to the HACK token first.
        This is a one-time setup required by Algorand.
      </div>
      <button
        onClick={handleOptIn}
        disabled={isOptingIn}
        style={{
          width: '100%',
          padding: '12px',
          background: isOptingIn ? '#ccc' : 'linear-gradient(135deg, #0066FF 0%, #004BB5 100%)',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontSize: '16px',
          fontWeight: 'bold',
          cursor: isOptingIn ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s ease'
        }}
      >
        {isOptingIn ? 'Opting In...' : 'Opt-in to HACK Token'}
      </button>
    </div>
  );
};

export default AssetOptIn;
