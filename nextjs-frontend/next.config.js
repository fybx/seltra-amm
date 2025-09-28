/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_ALGOD_ADDRESS: process.env.NEXT_PUBLIC_ALGOD_ADDRESS || 'https://testnet-api.algonode.cloud',
    NEXT_PUBLIC_ALGOD_TOKEN: process.env.NEXT_PUBLIC_ALGOD_TOKEN || '',
    NEXT_PUBLIC_INDEXER_ADDRESS: process.env.NEXT_PUBLIC_INDEXER_ADDRESS || 'https://testnet-idx.algonode.cloud',
    NEXT_PUBLIC_SIMULATOR_ADDRESS: process.env.NEXT_PUBLIC_SIMULATOR_ADDRESS || 'http://localhost:8001',
    NEXT_PUBLIC_NETWORK: process.env.NEXT_PUBLIC_NETWORK || 'testnet',
    NEXT_PUBLIC_SELTRA_POOL_APP_ID: process.env.NEXT_PUBLIC_SELTRA_POOL_APP_ID || '1000',
    NEXT_PUBLIC_ASSET_X_ID: process.env.NEXT_PUBLIC_ASSET_X_ID || '0',
    NEXT_PUBLIC_ASSET_Y_ID: process.env.NEXT_PUBLIC_ASSET_Y_ID || '1008'
  }
}

module.exports = nextConfig
