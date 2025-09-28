import { NetworkConfig, ContractConfig } from '@/types';

export const getNetworkConfig = (): NetworkConfig => {
  return {
    algodAddress: process.env.NEXT_PUBLIC_ALGOD_ADDRESS || 'https://testnet-api.algonode.cloud',
    algodToken: process.env.NEXT_PUBLIC_ALGOD_TOKEN || '',
    indexerAddress: process.env.NEXT_PUBLIC_INDEXER_ADDRESS || 'https://testnet-idx.algonode.cloud',
    network: (process.env.NEXT_PUBLIC_NETWORK as 'localnet' | 'testnet' | 'mainnet') || 'testnet'
  };
};

export const getContractConfig = (): ContractConfig => {
  return {
    poolAppId: parseInt(process.env.NEXT_PUBLIC_SELTRA_POOL_APP_ID || '1000'),
    assetXId: parseInt(process.env.NEXT_PUBLIC_ASSET_X_ID || '0'),
    assetYId: parseInt(process.env.NEXT_PUBLIC_ASSET_Y_ID || '1008')
  };
};

export const getSimulatorUrl = (): string => {
  return process.env.NEXT_PUBLIC_SIMULATOR_ADDRESS || 'http://localhost:8000';
};

// Color scheme constants
export const COLORS = {
  primary: {
    blue: '#0066FF',
    lightBlue: '#3385FF',
    darkBlue: '#0052CC',
  },
  secondary: {
    yellow: '#FFD700',
    lightYellow: '#FFED4A',
    darkYellow: '#F1C40F',
  },
  neutral: {
    white: '#FFFFFF',
    lightGray: '#F8F9FA',
    gray: '#6C757D',
    darkGray: '#343A40',
    black: '#000000',
  },
  status: {
    success: '#28A745',
    warning: '#FFC107',
    error: '#DC3545',
    info: '#17A2B8',
  }
};

// Fixed point scale for Algorand calculations
export const FIXED_POINT_SCALE = 1_000_000_000_000_000_000; // 1e18

// Asset decimals
export const ASSET_DECIMALS = {
  ALGO: 6,
  HACK: 6
};

// Format utilities
export const formatAlgoAmount = (amount: number): string => {
  return (amount / Math.pow(10, ASSET_DECIMALS.ALGO)).toFixed(6);
};

export const formatHackAmount = (amount: number): string => {
  return (amount / Math.pow(10, ASSET_DECIMALS.HACK)).toFixed(6);
};

export const formatPrice = (price: number): string => {
  return (price / FIXED_POINT_SCALE).toFixed(6);
};

export const parseAlgoAmount = (amount: string): number => {
  return Math.floor(parseFloat(amount) * Math.pow(10, ASSET_DECIMALS.ALGO));
};

export const parseHackAmount = (amount: string): number => {
  return Math.floor(parseFloat(amount) * Math.pow(10, ASSET_DECIMALS.HACK));
};
