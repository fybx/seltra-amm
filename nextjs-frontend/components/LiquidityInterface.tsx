'use client';

import React, { useState } from 'react';
import { useWallet } from '@/providers/WalletProvider';
import { useContract } from '@/providers/ContractProvider';
import { LiquidityParams } from '@/types';
import { getContractConfig, formatAlgoAmount, formatHackAmount, parseAlgoAmount, parseHackAmount } from '@/utils/config';

const LiquidityInterface: React.FC = () => {
  const { wallet } = useWallet();
  const { poolState, addLiquidity, removeLiquidity } = useContract();
  const [mode, setMode] = useState<'add' | 'remove'>('add');
  const [algoAmount, setAlgoAmount] = useState('');
  const [hackAmount, setHackAmount] = useState('');
  const [selectedRange, setSelectedRange] = useState(1);
  const [lpTokens, setLpTokens] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<string | null>(null);

  const contractConfig = getContractConfig();

  const handleAddLiquidity = async () => {
    if (!wallet.isConnected || !algoAmount || !hackAmount) return;

    setIsProcessing(true);
    setResult(null);

    try {
      const params: LiquidityParams = {
        assetX: contractConfig.assetXId,
        assetY: contractConfig.assetYId,
        amountXDesired: parseAlgoAmount(algoAmount),
        amountYDesired: parseHackAmount(hackAmount),
        amountXMin: parseAlgoAmount((parseFloat(algoAmount) * 0.95).toString()), // 5% slippage
        amountYMin: parseHackAmount((parseFloat(hackAmount) * 0.95).toString()),
        rangeId: selectedRange,
        deadline: Math.floor(Date.now() / 1000) + 300 // 5 minutes
      };

      const txResult = await addLiquidity(params);
      
      if (txResult.success) {
        setResult(`Liquidity added successfully! Transaction ID: ${txResult.txId}`);
        setAlgoAmount('');
        setHackAmount('');
      } else {
        setResult(`Failed to add liquidity: ${txResult.error}`);
      }
    } catch (error) {
      setResult(`Failed to add liquidity: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRemoveLiquidity = async () => {
    if (!wallet.isConnected || !lpTokens) return;

    setIsProcessing(true);
    setResult(null);

    try {
      const txResult = await removeLiquidity(parseFloat(lpTokens), selectedRange);
      
      if (txResult.success) {
        setResult(`Liquidity removed successfully! Transaction ID: ${txResult.txId}`);
        setLpTokens('');
      } else {
        setResult(`Failed to remove liquidity: ${txResult.error}`);
      }
    } catch (error) {
      setResult(`Failed to remove liquidity: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const getAlgoBalance = (): string => {
    return formatAlgoAmount(wallet.balance);
  };

  const getHackBalance = (): string => {
    const hackBalance = wallet.assetBalances[contractConfig.assetYId.toString()] || 0;
    return formatHackAmount(hackBalance);
  };

  const getRangeInfo = (rangeId: number) => {
    if (!poolState) return null;
    const range = poolState.ranges.find(r => r.id === rangeId);
    if (!range) return null;

    const lowerPrice = range.lower / 1e18;
    const upperPrice = range.upper / 1e18;
    const currentPrice = poolState.currentPrice / 1e18;
    
    let rangeType = '';
    if (rangeId === 1) rangeType = 'Tight (±5%)';
    else if (rangeId === 2) rangeType = 'Medium (±15%)';
    else if (rangeId === 3) rangeType = 'Wide (±30%)';

    return {
      type: rangeType,
      lower: lowerPrice,
      upper: upperPrice,
      current: currentPrice,
      liquidity: range.liquidity,
      isActive: range.isActive
    };
  };

  return (
    <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div className="card-header">
        <h2 className="card-title">Liquidity Management</h2>
        <p className="card-subtitle">Add or remove liquidity from concentrated ranges</p>
      </div>

      {/* Mode Selection */}
      <div style={{ 
        display: 'flex', 
        marginBottom: '24px',
        border: '2px solid #E9ECEF',
        borderRadius: '8px',
        overflow: 'hidden'
      }}>
        <button
          onClick={() => setMode('add')}
          style={{
            flex: 1,
            padding: '12px',
            border: 'none',
            background: mode === 'add' ? '#0066FF' : 'white',
            color: mode === 'add' ? 'white' : '#6C757D',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Add Liquidity
        </button>
        <button
          onClick={() => setMode('remove')}
          style={{
            flex: 1,
            padding: '12px',
            border: 'none',
            background: mode === 'remove' ? '#0066FF' : 'white',
            color: mode === 'remove' ? 'white' : '#6C757D',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Remove Liquidity
        </button>
      </div>

      {/* Range Selection */}
      <div style={{ marginBottom: '24px' }}>
        <label style={{ 
          fontSize: '14px', 
          fontWeight: '600',
          display: 'block',
          marginBottom: '12px'
        }}>
          Select Liquidity Range
        </label>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {[1, 2, 3].map((rangeId) => {
            const rangeInfo = getRangeInfo(rangeId);
            if (!rangeInfo) return null;

            return (
              <div
                key={rangeId}
                onClick={() => setSelectedRange(rangeId)}
                style={{
                  padding: '16px',
                  border: selectedRange === rangeId ? '2px solid #0066FF' : '2px solid #E9ECEF',
                  borderRadius: '8px',
                  background: selectedRange === rangeId ? '#F0F7FF' : 'white',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  marginBottom: '8px'
                }}>
                  <span style={{ fontWeight: '600', fontSize: '16px' }}>
                    Range {rangeId}: {rangeInfo.type}
                  </span>
                  <span style={{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: '600',
                    background: rangeInfo.isActive ? '#D4EDDA' : '#F8D7DA',
                    color: rangeInfo.isActive ? '#155724' : '#721C24'
                  }}>
                    {rangeInfo.isActive ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div style={{ fontSize: '14px', color: '#6C757D' }}>
                  <div>Price Range: {rangeInfo.lower.toFixed(6)} - {rangeInfo.upper.toFixed(6)} ALGO</div>
                  <div>Current Price: {rangeInfo.current.toFixed(6)} ALGO</div>
                  <div>Liquidity: {formatAlgoAmount(rangeInfo.liquidity)} ALGO</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {mode === 'add' ? (
        <>
          {/* Add Liquidity Form */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '8px'
            }}>
              <label style={{ fontSize: '14px', fontWeight: '600' }}>ALGO Amount</label>
              <span style={{ fontSize: '12px', color: '#6C757D' }}>
                Balance: {getAlgoBalance()} ALGO
              </span>
            </div>
            <input
              type="number"
              value={algoAmount}
              onChange={(e) => setAlgoAmount(e.target.value)}
              placeholder="0.0"
              className="input"
              style={{ marginBottom: '16px' }}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '8px'
            }}>
              <label style={{ fontSize: '14px', fontWeight: '600' }}>HACK Amount</label>
              <span style={{ fontSize: '12px', color: '#6C757D' }}>
                Balance: {getHackBalance()} HACK
              </span>
            </div>
            <input
              type="number"
              value={hackAmount}
              onChange={(e) => setHackAmount(e.target.value)}
              placeholder="0.0"
              className="input"
            />
          </div>

          <button
            onClick={handleAddLiquidity}
            disabled={!wallet.isConnected || !algoAmount || !hackAmount || isProcessing}
            className="btn-primary"
            style={{ width: '100%', fontSize: '16px', padding: '16px' }}
          >
            {isProcessing ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <div className="spinner"></div>
                Adding Liquidity...
              </span>
            ) : !wallet.isConnected ? (
              'Connect Wallet'
            ) : (
              'Add Liquidity'
            )}
          </button>
        </>
      ) : (
        <>
          {/* Remove Liquidity Form */}
          <div style={{ marginBottom: '24px' }}>
            <label style={{ 
              fontSize: '14px', 
              fontWeight: '600',
              display: 'block',
              marginBottom: '8px'
            }}>
              LP Tokens to Remove
            </label>
            <input
              type="number"
              value={lpTokens}
              onChange={(e) => setLpTokens(e.target.value)}
              placeholder="0.0"
              className="input"
            />
          </div>

          <button
            onClick={handleRemoveLiquidity}
            disabled={!wallet.isConnected || !lpTokens || isProcessing}
            className="btn-primary"
            style={{ width: '100%', fontSize: '16px', padding: '16px' }}
          >
            {isProcessing ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <div className="spinner"></div>
                Removing Liquidity...
              </span>
            ) : !wallet.isConnected ? (
              'Connect Wallet'
            ) : (
              'Remove Liquidity'
            )}
          </button>
        </>
      )}

      {/* Result Message */}
      {result && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          borderRadius: '8px',
          background: result.includes('successfully') ? '#D4EDDA' : '#F8D7DA',
          color: result.includes('successfully') ? '#155724' : '#721C24',
          fontSize: '14px',
          wordBreak: 'break-all'
        }}>
          {result}
        </div>
      )}
    </div>
  );
};

export default LiquidityInterface;
