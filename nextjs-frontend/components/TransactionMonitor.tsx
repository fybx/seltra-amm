'use client';

import React, { useState, useEffect } from 'react';
import { useWallet } from '@/providers/WalletProvider';

interface Transaction {
  id: string;
  type: 'swap' | 'add_liquidity' | 'remove_liquidity' | 'opt_in';
  status: 'pending' | 'confirmed' | 'failed';
  timestamp: number;
  details: {
    fromAsset?: string;
    toAsset?: string;
    fromAmount?: string;
    toAmount?: string;
    range?: number;
    amount?: string;
  };
  txId?: string;
}

const TransactionMonitor: React.FC = () => {
  const { wallet } = useWallet();
  const [transactions, setTransactions] = useState<Transaction[]>([
    // Demo transaction for testing
    {
      id: 'LRHS7JP4TNPC4XGB32C2YCV6CZ3ZDE3FZU7PPKCBJ3L6EWQKIRLQ',
      type: 'swap',
      status: 'confirmed',
      timestamp: Date.now() - 60000, // 1 minute ago
      details: {
        fromAsset: 'ALGO',
        toAsset: 'HACK',
        fromAmount: '1.5',
        toAmount: '450'
      },
      txId: 'LRHS7JP4TNPC4XGB32C2YCV6CZ3ZDE3FZU7PPKCBJ3L6EWQKIRLQ'
    }
  ]);
  const [isExpanded, setIsExpanded] = useState(true); // Show by default for demo

  // Add transaction to monitor
  const addTransaction = (tx: Omit<Transaction, 'timestamp'>) => {
    const newTx: Transaction = {
      ...tx,
      timestamp: Date.now()
    };
    setTransactions(prev => [newTx, ...prev.slice(0, 9)]); // Keep last 10 transactions
  };

  // Update transaction status
  const updateTransaction = (id: string, updates: Partial<Transaction>) => {
    setTransactions(prev => 
      prev.map(tx => tx.id === id ? { ...tx, ...updates } : tx)
    );
  };

  // Format timestamp
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('tr-TR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  // Get status color
  const getStatusColor = (status: Transaction['status']) => {
    switch (status) {
      case 'pending': return '#FFD700';
      case 'confirmed': return '#00C851';
      case 'failed': return '#FF4444';
      default: return '#ccc';
    }
  };

  // Get transaction icon
  const getTransactionIcon = (type: Transaction['type']) => {
    switch (type) {
      case 'swap': return '🔄';
      case 'add_liquidity': return '➕';
      case 'remove_liquidity': return '➖';
      case 'opt_in': return '✅';
      default: return '📝';
    }
  };

  // Get transaction description
  const getTransactionDescription = (tx: Transaction) => {
    switch (tx.type) {
      case 'swap':
        return `${tx.details.fromAmount} ${tx.details.fromAsset} → ${tx.details.toAmount} ${tx.details.toAsset}`;
      case 'add_liquidity':
        return `Add Liquidity Range ${tx.details.range}: ${tx.details.amount}`;
      case 'remove_liquidity':
        return `Remove Liquidity Range ${tx.details.range}: ${tx.details.amount}`;
      case 'opt_in':
        return 'HACK Token Opt-in';
      default:
        return 'Unknown Transaction';
    }
  };

  if (!wallet.isConnected || transactions.length === 0) {
    return null;
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      zIndex: 1000,
      background: 'white',
      borderRadius: '12px',
      boxShadow: '0 8px 32px rgba(0, 102, 255, 0.2)',
      border: '2px solid #0066FF',
      minWidth: '320px',
      maxWidth: '400px'
    }}>
      {/* Header */}
      <div 
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          padding: '16px',
          background: 'linear-gradient(135deg, #0066FF 0%, #004BB5 100%)',
          color: 'white',
          borderRadius: '10px 10px 0 0',
          cursor: 'pointer',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}
      >
        <div style={{ fontWeight: 'bold', fontSize: '16px' }}>
          Transaction Monitor ({transactions.length})
        </div>
        <div style={{ 
          transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: 'transform 0.3s ease'
        }}>
          ▼
        </div>
      </div>

      {/* Transaction List */}
      {isExpanded && (
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {transactions.map((tx, index) => (
            <div 
              key={tx.id}
              style={{
                padding: '12px 16px',
                borderBottom: index < transactions.length - 1 ? '1px solid #eee' : 'none',
                background: index % 2 === 0 ? '#f9f9f9' : 'white'
              }}
            >
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'flex-start',
                marginBottom: '8px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '16px' }}>{getTransactionIcon(tx.type)}</span>
                  <div>
                    <div style={{ fontWeight: 'bold', fontSize: '14px', color: '#333' }}>
                      {tx.type.replace('_', ' ').toUpperCase()}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {formatTime(tx.timestamp)}
                    </div>
                  </div>
                </div>
                <div style={{
                  padding: '4px 8px',
                  borderRadius: '12px',
                  background: getStatusColor(tx.status),
                  color: tx.status === 'pending' ? '#333' : 'white',
                  fontSize: '12px',
                  fontWeight: 'bold'
                }}>
                  {tx.status.toUpperCase()}
                </div>
              </div>
              
              <div style={{ fontSize: '13px', color: '#555', marginBottom: '8px' }}>
                {getTransactionDescription(tx)}
              </div>
              
              {tx.txId && (
                <div style={{ fontSize: '11px', color: '#888', fontFamily: 'monospace' }}>
                  TX: {tx.txId.substring(0, 20)}...
                  <a 
                    href={`https://testnet.algoexplorer.io/tx/${tx.txId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ 
                      color: '#0066FF', 
                      textDecoration: 'none',
                      marginLeft: '8px'
                    }}
                  >
                    View
                  </a>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Real-time Status Indicator */}
      <div style={{
        padding: '8px 16px',
        background: '#f0f8ff',
        borderRadius: '0 0 10px 10px',
        fontSize: '12px',
        color: '#0066FF',
        textAlign: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: '#00C851',
            animation: 'pulse 2s infinite'
          }} />
          Real-time Monitoring Active
        </div>
      </div>

      <style jsx>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `}</style>
    </div>
  );
};

// Export both component and helper functions for use in other components
export const useTransactionMonitor = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);

  const addTransaction = (tx: Omit<Transaction, 'timestamp'>) => {
    const newTx: Transaction = {
      ...tx,
      timestamp: Date.now()
    };
    setTransactions(prev => [newTx, ...prev.slice(0, 9)]);
  };

  const updateTransaction = (id: string, updates: Partial<Transaction>) => {
    setTransactions(prev => 
      prev.map(tx => tx.id === id ? { ...tx, ...updates } : tx)
    );
  };

  return { transactions, addTransaction, updateTransaction };
};

export default TransactionMonitor;
