'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { PeraWalletConnect } from '@perawallet/connect';
import algosdk from 'algosdk';
import { WalletState, NetworkConfig } from '@/types';
import { getNetworkConfig } from '@/utils/config';

interface WalletContextType {
  wallet: WalletState;
  peraWallet: PeraWalletConnect | null;
  connectWallet: () => Promise<void>;
  disconnectWallet: () => void;
  refreshBalance: () => Promise<void>;
  algodClient: algosdk.Algodv2 | null;
}

const WalletContext = createContext<WalletContextType | undefined>(undefined);

export const useWallet = () => {
  const context = useContext(WalletContext);
  if (!context) {
    throw new Error('useWallet must be used within a WalletProvider');
  }
  return context;
};

interface WalletProviderProps {
  children: ReactNode;
}

export const WalletProvider: React.FC<WalletProviderProps> = ({ children }) => {
  const [wallet, setWallet] = useState<WalletState>({
    isConnected: false,
    address: null,
    balance: 0,
    assetBalances: {}
  });

  const [peraWallet, setPeraWallet] = useState<PeraWalletConnect | null>(null);
  const [algodClient, setAlgodClient] = useState<algosdk.Algodv2 | null>(null);

  useEffect(() => {
    // Initialize Pera Wallet
    const wallet = new PeraWalletConnect({
      chainId: getNetworkConfig().network === 'testnet' ? 416002 : 416001
    });
    setPeraWallet(wallet);

    // Initialize Algod client
    const config = getNetworkConfig();
    const client = new algosdk.Algodv2(config.algodToken, config.algodAddress, '');
    setAlgodClient(client);

    // Check for existing connection
    wallet.reconnectSession().then((accounts) => {
      if (accounts.length > 0) {
        setWallet(prev => ({
          ...prev,
          isConnected: true,
          address: accounts[0]
        }));
        refreshBalanceForAddress(accounts[0], client);
      }
    }).catch(console.error);

    // Listen for disconnect events
    wallet.connector?.on('disconnect', () => {
      setWallet({
        isConnected: false,
        address: null,
        balance: 0,
        assetBalances: {}
      });
    });

    return () => {
      wallet.disconnect();
    };
  }, []);

  const refreshBalanceForAddress = async (address: string, client: algosdk.Algodv2) => {
    try {
      const accountInfo = await client.accountInformation(address).do();
      
      const assetBalances: Record<string, number> = {};
      accountInfo.assets?.forEach((asset: any) => {
        assetBalances[asset['asset-id']] = asset.amount;
      });

      setWallet(prev => ({
        ...prev,
        balance: Number(accountInfo.amount),
        assetBalances
      }));
    } catch (error) {
      console.error('Error fetching balance:', error);
    }
  };

  const connectWallet = async () => {
    if (!peraWallet) return;

    try {
      const accounts = await peraWallet.connect();
      if (accounts.length > 0) {
        setWallet(prev => ({
          ...prev,
          isConnected: true,
          address: accounts[0]
        }));
        
        if (algodClient) {
          await refreshBalanceForAddress(accounts[0], algodClient);
        }
      }
    } catch (error) {
      console.error('Error connecting wallet:', error);
    }
  };

  const disconnectWallet = () => {
    if (peraWallet) {
      peraWallet.disconnect();
    }
    setWallet({
      isConnected: false,
      address: null,
      balance: 0,
      assetBalances: {}
    });
  };

  const refreshBalance = async () => {
    if (wallet.address && algodClient) {
      await refreshBalanceForAddress(wallet.address, algodClient);
    }
  };

  return (
    <WalletContext.Provider value={{
      wallet,
      peraWallet,
      connectWallet,
      disconnectWallet,
      refreshBalance,
      algodClient
    }}>
      {children}
    </WalletContext.Provider>
  );
};
