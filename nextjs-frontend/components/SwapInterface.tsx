'use client';

import React, { useState, useEffect } from 'react';
import { useWallet } from '@/providers/WalletProvider';
import { useContract } from '@/providers/ContractProvider';
import { SwapParams } from '@/types';
import { getContractConfig, formatAlgoAmount, formatHackAmount, parseAlgoAmount, parseHackAmount } from '@/utils/config';

const SwapInterface: React.FC = () => {
  const { wallet } = useWallet();
  const { poolState, executeSwap } = useContract();
  const [fromAsset, setFromAsset] = useState<'ALGO' | 'HACK'>('ALGO');
  const [toAsset, setToAsset] = useState<'ALGO' | 'HACK'>('HACK');
  const [fromAmount, setFromAmount] = useState('');
  const [toAmount, setToAmount] = useState('');
  const [slippage, setSlippage] = useState('1.0');
  const [isSwapping, setIsSwapping] = useState(false);
  const [swapResult, setSwapResult] = useState<string | null>(null);

  const contractConfig = getContractConfig();

  useEffect(() => {
    if (fromAmount && poolState) {
      calculateToAmount();
    }
  }, [fromAmount, fromAsset, toAsset, poolState]);

  const calculateToAmount = () => {
    if (!fromAmount || !poolState) return;

    try {
      const inputAmount = parseFloat(fromAmount);
      if (isNaN(inputAmount) || inputAmount <= 0) {
        setToAmount('');
        return;
      }

      // Simple price calculation based on current pool price
      // In a real implementation, this would use the actual AMM formula
      const currentPrice = poolState.currentPrice / 1e6; // Convert from scaled value (100 HACK per ALGO)
      
      let outputAmount: number;
      if (fromAsset === 'ALGO') {
        outputAmount = inputAmount * currentPrice;
      } else {
        outputAmount = inputAmount / currentPrice;
      }

      // Apply fee
      const feeRate = poolState.feeRate / 10000; // Convert from basis points
      outputAmount = outputAmount * (1 - feeRate);

      setToAmount(outputAmount.toFixed(6));
    } catch (error) {
      console.error('Error calculating output amount:', error);
      setToAmount('');
    }
  };

  const handleSwapAssets = () => {
    setFromAsset(toAsset);
    setToAsset(fromAsset);
    setFromAmount(toAmount);
    setToAmount(fromAmount);
  };

  const handleSwap = async () => {
    if (!wallet.isConnected || !fromAmount || !toAmount) return;

    setIsSwapping(true);
    setSwapResult(null);

    try {
      const slippageMultiplier = 1 - (parseFloat(slippage) / 100);
      const minAmountOut = parseFloat(toAmount) * slippageMultiplier;

      const swapParams: SwapParams = {
        assetIn: fromAsset === 'ALGO' ? contractConfig.assetXId : contractConfig.assetYId,
        assetOut: toAsset === 'ALGO' ? contractConfig.assetXId : contractConfig.assetYId,
        amountIn: fromAsset === 'ALGO' ? parseAlgoAmount(fromAmount) : parseHackAmount(fromAmount),
        minAmountOut: toAsset === 'ALGO' ? parseAlgoAmount(minAmountOut.toString()) : parseHackAmount(minAmountOut.toString()),
        deadline: Math.floor(Date.now() / 1000) + 300 // 5 minutes
      };

      const result = await executeSwap(swapParams);
      
      if (result.success) {
        setSwapResult(`Swap successful! Transaction ID: ${result.txId}`);
        setFromAmount('');
        setToAmount('');
      } else {
        setSwapResult(`Swap failed: ${result.error}`);
      }
    } catch (error) {
      setSwapResult(`Swap failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSwapping(false);
    }
  };

  const getBalance = (asset: 'ALGO' | 'HACK'): string => {
    if (asset === 'ALGO') {
      return formatAlgoAmount(wallet.balance);
    } else {
      const hackBalance = wallet.assetBalances[contractConfig.assetYId.toString()] || 0;
      return formatHackAmount(hackBalance);
    }
  };

  const canSwap = wallet.isConnected && fromAmount && toAmount && !isSwapping && poolState;

  return (
    <div className="card" style={{ maxWidth: '480px', margin: '0 auto' }}>
      <div className="card-header">
        <h2 className="card-title">Swap Tokens</h2>
        <p className="card-subtitle">Exchange ALGO and HACK tokens with dynamic liquidity</p>
      </div>

      {/* From Token */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '8px'
        }}>
          <label style={{ fontSize: '14px', fontWeight: '600' }}>From</label>
          <span style={{ fontSize: '12px', color: '#6C757D' }}>
            Balance: {getBalance(fromAsset)} {fromAsset}
          </span>
        </div>
        <div style={{ 
          display: 'flex', 
          border: '2px solid #E9ECEF',
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <input
            type="number"
            value={fromAmount}
            onChange={(e) => setFromAmount(e.target.value)}
            placeholder="0.0"
            style={{
              flex: 1,
              padding: '16px',
              border: 'none',
              fontSize: '18px',
              outline: 'none'
            }}
          />
          <div style={{
            display: 'flex',
            alignItems: 'center',
            padding: '0 16px',
            background: '#F8F9FA',
            borderLeft: '1px solid #E9ECEF'
          }}>
            <span style={{ fontWeight: '600', fontSize: '16px' }}>{fromAsset}</span>
          </div>
        </div>
      </div>

      {/* Swap Button */}
      <div style={{ display: 'flex', justifyContent: 'center', margin: '16px 0' }}>
        <button
          onClick={handleSwapAssets}
          style={{
            background: 'white',
            border: '2px solid #0066FF',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px',
            color: '#0066FF'
          }}
        >
          ↕
        </button>
      </div>

      {/* To Token */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '8px'
        }}>
          <label style={{ fontSize: '14px', fontWeight: '600' }}>To</label>
          <span style={{ fontSize: '12px', color: '#6C757D' }}>
            Balance: {getBalance(toAsset)} {toAsset}
          </span>
        </div>
        <div style={{ 
          display: 'flex', 
          border: '2px solid #E9ECEF',
          borderRadius: '8px',
          overflow: 'hidden'
        }}>
          <input
            type="number"
            value={toAmount}
            readOnly
            placeholder="0.0"
            style={{
              flex: 1,
              padding: '16px',
              border: 'none',
              fontSize: '18px',
              outline: 'none',
              background: '#F8F9FA'
            }}
          />
          <div style={{
            display: 'flex',
            alignItems: 'center',
            padding: '0 16px',
            background: '#F8F9FA',
            borderLeft: '1px solid #E9ECEF'
          }}>
            <span style={{ fontWeight: '600', fontSize: '16px' }}>{toAsset}</span>
          </div>
        </div>
      </div>

      {/* Slippage Settings */}
      <div style={{ marginBottom: '24px' }}>
        <label style={{ 
          fontSize: '14px', 
          fontWeight: '600',
          display: 'block',
          marginBottom: '8px'
        }}>
          Slippage Tolerance
        </label>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['0.5', '1.0', '2.0'].map((value) => (
            <button
              key={value}
              onClick={() => setSlippage(value)}
              style={{
                padding: '8px 16px',
                border: slippage === value ? '2px solid #0066FF' : '2px solid #E9ECEF',
                borderRadius: '6px',
                background: slippage === value ? '#F0F7FF' : 'white',
                color: slippage === value ? '#0066FF' : '#6C757D',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600'
              }}
            >
              {value}%
            </button>
          ))}
          <input
            type="number"
            value={slippage}
            onChange={(e) => setSlippage(e.target.value)}
            style={{
              width: '80px',
              padding: '8px',
              border: '2px solid #E9ECEF',
              borderRadius: '6px',
              textAlign: 'center',
              fontSize: '14px'
            }}
            step="0.1"
            min="0.1"
            max="50"
          />
        </div>
      </div>

      {/* Swap Button */}
      <button
        onClick={handleSwap}
        disabled={!canSwap}
        className="btn-primary"
        style={{ 
          width: '100%',
          fontSize: '18px',
          padding: '16px'
        }}
      >
        {isSwapping ? (
          <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <div className="spinner"></div>
            Swapping...
          </span>
        ) : !wallet.isConnected ? (
          'Connect Wallet'
        ) : !poolState ? (
          'Loading Pool...'
        ) : (
          'Swap'
        )}
      </button>

      {/* Result Message */}
      {swapResult && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          borderRadius: '8px',
          background: swapResult.includes('successful') ? '#D4EDDA' : '#F8D7DA',
          color: swapResult.includes('successful') ? '#155724' : '#721C24',
          fontSize: '14px',
          wordBreak: 'break-all'
        }}>
          {swapResult}
        </div>
      )}

      {/* Pool Info */}
      {poolState && (
        <div style={{
          marginTop: '24px',
          padding: '16px',
          background: '#F8F9FA',
          borderRadius: '8px',
          fontSize: '14px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span>Current Price:</span>
            <span style={{ fontWeight: '600' }}>
              1 HACK = {(poolState.currentPrice / 1e18).toFixed(6)} ALGO
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span>Fee Rate:</span>
            <span style={{ fontWeight: '600' }}>{(poolState.feeRate / 100).toFixed(2)}%</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Total Liquidity:</span>
            <span style={{ fontWeight: '600' }}>
              {formatAlgoAmount(poolState.totalLiquidity)} ALGO
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default SwapInterface;
