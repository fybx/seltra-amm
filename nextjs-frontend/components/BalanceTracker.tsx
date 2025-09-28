'use client';

import React, { useState, useEffect } from 'react';
import { useWallet } from '@/providers/WalletProvider';
import { getContractConfig, formatAlgoAmount, formatHackAmount } from '@/utils/config';
import algosdk from 'algosdk';

interface Balance {
  algo: number;
  hack: number;
  lastUpdated: number;
}

interface BalanceTrackerProps {
  onBalanceUpdate?: (balance: Balance) => void;
}

const BalanceTracker: React.FC<BalanceTrackerProps> = ({ onBalanceUpdate }) => {
  const { wallet } = useWallet();
  const [balance, setBalance] = useState<Balance>({ algo: 4.0, hack: 450, lastUpdated: Date.now() });
  const [isLoading, setIsLoading] = useState(false);
  const [history, setHistory] = useState<Balance[]>([
    // Demo data for testing
    { algo: 8.5, hack: 0, lastUpdated: Date.now() - 300000 },
    { algo: 7.0, hack: 150, lastUpdated: Date.now() - 240000 },
    { algo: 7.0, hack: 150, lastUpdated: Date.now() - 180000 },
    { algo: 5.5, hack: 300, lastUpdated: Date.now() - 120000 },
    { algo: 5.5, hack: 300, lastUpdated: Date.now() - 60000 },
    { algo: 4.0, hack: 450, lastUpdated: Date.now() }
  ]);
  const contractConfig = getContractConfig();

  const fetchBalance = async () => {
    if (!wallet.isConnected || !wallet.address) return;

    setIsLoading(true);
    try {
      const algodClient = new algosdk.Algodv2('', 'https://testnet-api.algonode.cloud', '');
      const accountInfo = await algodClient.accountInformation(wallet.address).do();
      
      // Get ALGO balance
      const algoBalance = Number(accountInfo.amount) / 1_000_000; // Convert microAlgos to Algos

      // Get HACK balance
      let hackBalance = 0;
      const hackAsset = accountInfo.assets?.find((asset: any) => asset['asset-id'] === contractConfig.assetYId);
      if (hackAsset) {
        hackBalance = Number(hackAsset.amount) / 1_000_000; // Assuming 6 decimals for HACK
      }

      const newBalance: Balance = {
        algo: algoBalance,
        hack: hackBalance,
        lastUpdated: Date.now()
      };

      setBalance(newBalance);
      setHistory(prev => [...prev.slice(-19), newBalance]); // Keep last 20 entries
      onBalanceUpdate?.(newBalance);
    } catch (error) {
      console.error('Error fetching balance:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-refresh balance every 10 seconds
  useEffect(() => {
    if (wallet.isConnected) {
      fetchBalance();
      const interval = setInterval(fetchBalance, 10000);
      return () => clearInterval(interval);
    }
  }, [wallet.isConnected, wallet.address]);

  // Manual refresh
  const handleRefresh = () => {
    fetchBalance();
  };

  if (!wallet.isConnected) {
    return null;
  }

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('tr-TR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      boxShadow: '0 4px 16px rgba(0, 102, 255, 0.1)',
      border: '2px solid #0066FF',
      margin: '16px 0'
    }}>
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px'
      }}>
        <h3 style={{ 
          margin: 0, 
          color: '#0066FF', 
          fontSize: '18px',
          fontWeight: 'bold'
        }}>
          Wallet Balance
        </h3>
        <button
          onClick={handleRefresh}
          disabled={isLoading}
          style={{
            background: isLoading ? '#ccc' : 'linear-gradient(135deg, #FFD700 0%, #FFA000 100%)',
            border: 'none',
            borderRadius: '8px',
            padding: '8px 12px',
            color: '#333',
            fontSize: '12px',
            fontWeight: 'bold',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s ease'
          }}
        >
          {isLoading ? '🔄' : '↻'} Refresh
        </button>
      </div>

      {/* Balance Display */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
        {/* ALGO Balance */}
        <div style={{
          background: 'linear-gradient(135deg, #0066FF 0%, #004BB5 100%)',
          borderRadius: '12px',
          padding: '16px',
          color: 'white',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '8px' }}>ALGO</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '4px' }}>
            {formatAlgoAmount(balance.algo)}
          </div>
          <div style={{ fontSize: '12px', opacity: 0.7 }}>
            ${(balance.algo * 0.25).toFixed(2)} USD
          </div>
        </div>

        {/* HACK Balance */}
        <div style={{
          background: 'linear-gradient(135deg, #FFD700 0%, #FFA000 100%)',
          borderRadius: '12px',
          padding: '16px',
          color: '#333',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '14px', opacity: 0.8, marginBottom: '8px' }}>HACK</div>
          <div style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '4px' }}>
            {formatHackAmount(balance.hack)}
          </div>
          <div style={{ fontSize: '12px', opacity: 0.7 }}>
            ${(balance.hack * 0.001).toFixed(4)} USD
          </div>
        </div>
      </div>

      {/* Balance History Chart */}
      {history.length > 1 && (
        <div style={{ marginBottom: '16px' }}>
          <div style={{ 
            fontSize: '14px', 
            fontWeight: 'bold', 
            color: '#333', 
            marginBottom: '12px' 
          }}>
            Balance History (Last {history.length} Updates)
          </div>
          
          {/* Simple Chart */}
          <div style={{ 
            height: '80px', 
            background: '#f8f9fa', 
            borderRadius: '8px', 
            padding: '8px',
            position: 'relative',
            overflow: 'hidden'
          }}>
            {/* ALGO Line */}
            <svg width="100%" height="100%" style={{ position: 'absolute', top: 0, left: 0 }}>
              <polyline
                points={history.map((h, i) => {
                  const maxAlgo = Math.max(...history.map(h => h.algo || 0)) || 1;
                  const normalizedY = isNaN(h.algo) ? 50 : 100 - ((h.algo || 0) / maxAlgo * 80);
                  const normalizedX = history.length > 1 ? (i / (history.length - 1)) * 100 : 50;
                  return `${normalizedX},${normalizedY}`;
                }).join(' ')}
                fill="none"
                stroke="#0066FF"
                strokeWidth="2"
              />
              <polyline
                points={history.map((h, i) => {
                  const maxHack = Math.max(...history.map(h => h.hack || 0)) || 1;
                  const normalizedY = isNaN(h.hack) ? 50 : 100 - ((h.hack || 0) / maxHack * 80);
                  const normalizedX = history.length > 1 ? (i / (history.length - 1)) * 100 : 50;
                  return `${normalizedX},${normalizedY}`;
                }).join(' ')}
                fill="none"
                stroke="#FFD700"
                strokeWidth="2"
              />
            </svg>
            
            {/* Legend */}
            <div style={{ 
              position: 'absolute', 
              top: '8px', 
              right: '8px',
              fontSize: '10px'
            }}>
              <div style={{ color: '#0066FF' }}>— ALGO</div>
              <div style={{ color: '#FFD700' }}>— HACK</div>
            </div>
          </div>
        </div>
      )}

      {/* Last Update */}
      <div style={{ 
        fontSize: '12px', 
        color: '#666', 
        textAlign: 'center',
        borderTop: '1px solid #eee',
        paddingTop: '12px'
      }}>
        Last updated: {balance.lastUpdated ? formatTime(balance.lastUpdated) : 'Never'}
      </div>

      {/* Portfolio Value */}
      <div style={{
        background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
        borderRadius: '8px',
        padding: '12px',
        marginTop: '12px',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>
          Total Portfolio Value
        </div>
        <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333' }}>
          ${((balance.algo * 0.25) + (balance.hack * 0.001)).toFixed(2)} USD
        </div>
      </div>
    </div>
  );
};

export default BalanceTracker;
