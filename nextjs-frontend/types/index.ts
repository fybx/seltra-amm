// Seltra AMM Types

export interface WalletState {
  isConnected: boolean;
  address: string | null;
  balance: number;
  assetBalances: Record<string, number>;
}

export interface PoolState {
  appId: number;
  assetX: number;
  assetY: number;
  currentPrice: number;
  totalLiquidity: number;
  feeRate: number;
  ranges: LiquidityRange[];
}

export interface LiquidityRange {
  id: number;
  lower: number;
  upper: number;
  liquidity: number;
  isActive: boolean;
}

export interface MarketData {
  price: number;
  volume: number;
  volatility: number;
  regime: 'low' | 'medium' | 'high';
  scenario: string;
  timestamp: number;
  price_history: PricePoint[];
}

export interface PricePoint {
  price: number;
  volume: number;
  timestamp: number;
}

export interface SwapParams {
  assetIn: number;
  assetOut: number;
  amountIn: number;
  minAmountOut: number;
  deadline: number;
}

export interface LiquidityParams {
  assetX: number;
  assetY: number;
  amountXDesired: number;
  amountYDesired: number;
  amountXMin: number;
  amountYMin: number;
  rangeId: number;
  deadline: number;
}

export interface TransactionResult {
  success: boolean;
  txId?: string;
  error?: string;
}

export interface NetworkConfig {
  algodAddress: string;
  algodToken: string;
  indexerAddress: string;
  network: 'localnet' | 'testnet' | 'mainnet';
}

export interface ContractConfig {
  poolAppId: number;
  assetXId: number;
  assetYId: number;
}

export interface SimulatorStatus {
  market_active: boolean;
  blockchain_active: boolean;
  current_scenario: string;
  current_regime: string;
  uptime: number;
}
