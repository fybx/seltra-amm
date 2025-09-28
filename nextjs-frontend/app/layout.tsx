import type { Metadata } from 'next';
import { WalletProvider } from '@/providers/WalletProvider';
import { ContractProvider } from '@/providers/ContractProvider';
import { MarketDataProvider } from '@/providers/MarketDataProvider';
import Layout from '@/components/Layout';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'Seltra AMM - Intelligent Dynamic Liquidity',
  description: 'Next-generation AMM with dynamic liquidity concentration based on market volatility',
  keywords: 'AMM, DeFi, Algorand, Liquidity, Trading',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <WalletProvider>
          <ContractProvider>
            <MarketDataProvider>
              <Layout>
                {children}
              </Layout>
            </MarketDataProvider>
          </ContractProvider>
        </WalletProvider>
      </body>
    </html>
  );
}
