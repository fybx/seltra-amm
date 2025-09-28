'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import algosdk from 'algosdk';
import { useWallet } from './WalletProvider';
import { PoolState, SwapParams, LiquidityParams, TransactionResult } from '@/types';
import { getContractConfig } from '@/utils/config';

interface ContractContextType {
  poolState: PoolState | null;
  isLoading: boolean;
  refreshPoolState: () => Promise<void>;
  executeSwap: (params: SwapParams) => Promise<TransactionResult>;
  addLiquidity: (params: LiquidityParams) => Promise<TransactionResult>;
  removeLiquidity: (lpTokens: number, rangeId: number) => Promise<TransactionResult>;
}

const ContractContext = createContext<ContractContextType | undefined>(undefined);

export const useContract = () => {
  const context = useContext(ContractContext);
  if (!context) {
    throw new Error('useContract must be used within a ContractProvider');
  }
  return context;
};

interface ContractProviderProps {
  children: ReactNode;
}

export const ContractProvider: React.FC<ContractProviderProps> = ({ children }) => {
  const { wallet, algodClient, peraWallet } = useWallet();
  const [poolState, setPoolState] = useState<PoolState | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const contractConfig = getContractConfig();

  useEffect(() => {
    if (algodClient) {
      refreshPoolState();
    }
  }, [algodClient]);

  const parseGlobalState = (globalState: any[], key: string): number | null => {
    const item = globalState.find(item =>
      Buffer.from(item.key, 'base64').toString() === key
    );
    return item ? item.value.uint : null;
  };

  const refreshPoolState = async () => {
    if (!algodClient) return;

    setIsLoading(true);
    try {
      // Try to get real contract state, fallback to simulated state
      let poolData: PoolState;

      try {
        const appInfo = await algodClient.getApplicationByID(contractConfig.poolAppId).do();
        const globalState = appInfo.params.globalState || [];

        // Parse global state to extract pool information
        poolData = {
          appId: contractConfig.poolAppId,
          assetX: contractConfig.assetXId,
          assetY: contractConfig.assetYId,
          currentPrice: parseGlobalState(globalState || [], 'current_price') || 100_000_000, // 100 HACK per ALGO (scaled)
          totalLiquidity: parseGlobalState(globalState || [], 'total_liquidity') || 1_000_000_000, // 1000 units (scaled)
          feeRate: parseGlobalState(globalState || [], 'current_fee_rate') || 30, // 0.3%
          ranges: [
            {
              id: 1,
              lower: parseGlobalState(globalState || [], 'range1_lower') || 90_000_000, // 90 HACK per ALGO (scaled)
              upper: parseGlobalState(globalState || [], 'range1_upper') || 110_000_000, // 110 HACK per ALGO (scaled)
              liquidity: parseGlobalState(globalState || [], 'range1_liquidity') || 500_000_000,
              isActive: true
            },
            {
              id: 2,
              lower: parseGlobalState(globalState || [], 'range2_lower') || 80_000_000, // 80 HACK per ALGO (scaled)
              upper: parseGlobalState(globalState || [], 'range2_upper') || 120_000_000, // 120 HACK per ALGO (scaled)
              liquidity: parseGlobalState(globalState || [], 'range2_liquidity') || 300_000_000,
              isActive: true
            },
            {
              id: 3,
              lower: parseGlobalState(globalState || [], 'range3_lower') || 70_000_000, // 70 HACK per ALGO (scaled)
              upper: parseGlobalState(globalState || [], 'range3_upper') || 130_000_000, // 130 HACK per ALGO (scaled)
              liquidity: parseGlobalState(globalState || [], 'range3_liquidity') || 200_000_000,
              isActive: true
            }
          ]
        };
      } catch (contractError) {
        // Contract doesn't exist yet, use simulated pool state
        console.log('Contract not deployed yet, using simulated pool state');
        poolData = {
          appId: contractConfig.poolAppId,
          assetX: contractConfig.assetXId,
          assetY: contractConfig.assetYId,
          currentPrice: 100_000_000, // 100 HACK per ALGO (scaled)
          totalLiquidity: 1_000_000_000, // 1000 units (scaled)
          feeRate: 30, // 0.3%
          ranges: [
            {
              id: 1,
              lower: 90_000_000, // 90 HACK per ALGO (scaled)
              upper: 110_000_000, // 110 HACK per ALGO (scaled)
              liquidity: 500_000_000,
              isActive: true
            },
            {
              id: 2,
              lower: 80_000_000, // 80 HACK per ALGO (scaled)
              upper: 120_000_000, // 120 HACK per ALGO (scaled)
              liquidity: 300_000_000,
              isActive: true
            },
            {
              id: 3,
              lower: 70_000_000, // 70 HACK per ALGO (scaled)
              upper: 130_000_000, // 130 HACK per ALGO (scaled)
              liquidity: 200_000_000,
              isActive: true
            }
          ]
        };
      }

      setPoolState(poolData);
    } catch (error) {
      console.error('Error fetching pool state:', error);
    } finally {
      setIsLoading(false);
    }
  };



  const executeSwap = async (params: SwapParams): Promise<TransactionResult> => {
    if (!wallet.isConnected || !wallet.address || !algodClient || !peraWallet) {
      return { success: false, error: 'Wallet not connected' };
    }

    try {
      const suggestedParams = await algodClient.getTransactionParams().do();
      const transactions: algosdk.Transaction[] = [];

      // Determine if this is ALGO -> HACK or HACK -> ALGO
      const isAlgoToHack = params.assetIn === 0; // ALGO has asset ID 0

      if (isAlgoToHack) {
        // ALGO -> HACK swap: Send ALGO payment to contract
        const paymentTxn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
          sender: wallet.address,
          receiver: algosdk.getApplicationAddress(contractConfig.poolAppId),
          amount: params.amountIn,
          suggestedParams
        });
        transactions.push(paymentTxn);
      } else {
        // HACK -> ALGO swap: Send HACK asset to contract
        const assetTransferTxn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
          sender: wallet.address,
          receiver: algosdk.getApplicationAddress(contractConfig.poolAppId),
          amount: params.amountIn,
          assetIndex: params.assetIn,
          suggestedParams
        });
        transactions.push(assetTransferTxn);
      }

      // Create application call transaction for swap
      const appCallTxn = algosdk.makeApplicationCallTxnFromObject({
        sender: wallet.address,
        appIndex: contractConfig.poolAppId,
        onComplete: algosdk.OnApplicationComplete.NoOpOC,
        appArgs: [
          new Uint8Array(Buffer.from('swap')),
          algosdk.encodeUint64(params.assetIn),
          algosdk.encodeUint64(params.assetOut),
          algosdk.encodeUint64(params.amountIn),
          algosdk.encodeUint64(params.minAmountOut),
          algosdk.encodeUint64(params.deadline)
        ],
        foreignAssets: [params.assetIn, params.assetOut].filter(id => id !== 0),
        suggestedParams
      });
      transactions.push(appCallTxn);

      // Group transactions
      const groupedTxns = algosdk.assignGroupID(transactions);

      // Prepare transactions for signing
      const txnsToSign = groupedTxns.map(txn => ({ txn, signers: [wallet.address!] }));

      // Sign and send transaction group
      const signedTxns = await peraWallet.signTransaction([txnsToSign]);
      const response = await algodClient.sendRawTransaction(signedTxns).do();
      const txId = response.txid;

      // Wait for confirmation
      await algosdk.waitForConfirmation(algodClient, txId, 4);

      // Refresh pool state and wallet balance
      await refreshPoolState();

      return { success: true, txId };
    } catch (error) {
      console.error('Swap error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  };

  const addLiquidity = async (params: LiquidityParams): Promise<TransactionResult> => {
    if (!wallet.isConnected || !wallet.address || !algodClient || !peraWallet) {
      return { success: false, error: 'Wallet not connected' };
    }

    try {
      const suggestedParams = await algodClient.getTransactionParams().do();
      
      const appCallTxn = algosdk.makeApplicationCallTxnFromObject({
        sender: wallet.address,
        appIndex: contractConfig.poolAppId,
        onComplete: algosdk.OnApplicationComplete.NoOpOC,
        appArgs: [
          new Uint8Array(Buffer.from('add_liquidity')),
          algosdk.encodeUint64(params.assetX),
          algosdk.encodeUint64(params.assetY),
          algosdk.encodeUint64(params.amountXDesired),
          algosdk.encodeUint64(params.amountYDesired),
          algosdk.encodeUint64(params.amountXMin),
          algosdk.encodeUint64(params.amountYMin),
          algosdk.encodeUint64(params.rangeId),
          algosdk.encodeUint64(params.deadline)
        ],
        foreignAssets: [params.assetX, params.assetY].filter(id => id !== 0),
        suggestedParams
      });

      const signedTxns = await peraWallet.signTransaction([[{ txn: appCallTxn, signers: [wallet.address] }]]);
      const response = await algodClient.sendRawTransaction(signedTxns[0]).do();
      const txId = response.txid;

      await algosdk.waitForConfirmation(algodClient, txId, 4);
      await refreshPoolState();
      
      return { success: true, txId };
    } catch (error) {
      console.error('Add liquidity error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  };

  const removeLiquidity = async (lpTokens: number, rangeId: number): Promise<TransactionResult> => {
    if (!wallet.isConnected || !wallet.address || !algodClient || !peraWallet) {
      return { success: false, error: 'Wallet not connected' };
    }

    try {
      const suggestedParams = await algodClient.getTransactionParams().do();
      
      const appCallTxn = algosdk.makeApplicationCallTxnFromObject({
        sender: wallet.address,
        appIndex: contractConfig.poolAppId,
        onComplete: algosdk.OnApplicationComplete.NoOpOC,
        appArgs: [
          new Uint8Array(Buffer.from('remove_liquidity')),
          algosdk.encodeUint64(lpTokens),
          algosdk.encodeUint64(rangeId)
        ],
        suggestedParams
      });

      const signedTxns = await peraWallet.signTransaction([[{ txn: appCallTxn, signers: [wallet.address] }]]);
      const response = await algodClient.sendRawTransaction(signedTxns[0]).do();
      const txId = response.txid;

      await algosdk.waitForConfirmation(algodClient, txId, 4);
      await refreshPoolState();
      
      return { success: true, txId };
    } catch (error) {
      console.error('Remove liquidity error:', error);
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  };

  return (
    <ContractContext.Provider value={{
      poolState,
      isLoading,
      refreshPoolState,
      executeSwap,
      addLiquidity,
      removeLiquidity
    }}>
      {children}
    </ContractContext.Provider>
  );
};
