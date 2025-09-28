'use client';

import React, { ReactNode } from 'react';
import { useWallet } from '@/providers/WalletProvider';
import { useMarketData } from '@/providers/MarketDataProvider';
import { formatAlgoAmount, formatHackAmount } from '@/utils/config';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { wallet, connectWallet, disconnectWallet } = useWallet();
  const { simulatorStatus, isConnected } = useMarketData();

  return (
    <div className="min-h-screen bg-light">
      {/* Header */}
      <header style={{ 
        background: 'linear-gradient(135deg, #0066FF 0%, #0052CC 100%)',
        color: 'white',
        padding: '16px 0',
        boxShadow: '0 2px 8px rgba(0, 102, 255, 0.2)'
      }}>
        <div style={{ 
          maxWidth: '1200px', 
          margin: '0 auto', 
          padding: '0 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h1 style={{ 
              fontSize: '28px', 
              fontWeight: '700', 
              margin: '0',
              background: 'linear-gradient(135deg, #FFFFFF 0%, #FFD700 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Seltra AMM
            </h1>
            <p style={{ 
              fontSize: '14px', 
              margin: '4px 0 0 0',
              opacity: '0.9'
            }}>
              Intelligent Dynamic Liquidity Protocol
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {/* Network Status */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              padding: '8px 12px',
              background: 'rgba(255, 255, 255, 0.1)',
              borderRadius: '6px',
              fontSize: '14px'
            }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: isConnected ? '#28A745' : '#DC3545'
              }}></div>
              <span>Market: {isConnected ? 'Live' : 'Offline'}</span>
            </div>

            {/* Wallet Connection */}
            {wallet.isConnected ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ 
                  textAlign: 'right',
                  fontSize: '14px'
                }}>
                  <div style={{ fontWeight: '600' }}>
                    {wallet.address?.slice(0, 6)}...{wallet.address?.slice(-4)}
                  </div>
                  <div style={{ opacity: '0.8' }}>
                    {formatAlgoAmount(wallet.balance)} ALGO
                  </div>
                </div>
                <button 
                  onClick={disconnectWallet}
                  style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  Disconnect
                </button>
              </div>
            ) : (
              <button 
                onClick={connectWallet}
                className="btn-secondary"
                style={{ fontSize: '14px' }}
              >
                Connect Pera Wallet
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ 
        maxWidth: '1200px', 
        margin: '0 auto', 
        padding: '24px'
      }}>
        {children}
      </main>

      {/* Footer */}
      <footer style={{ 
        background: '#343A40',
        color: 'white',
        padding: '24px 0',
        marginTop: '48px'
      }}>
        <div style={{ 
          maxWidth: '1200px', 
          margin: '0 auto', 
          padding: '0 24px',
          textAlign: 'center'
        }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            gap: '24px',
            marginBottom: '16px'
          }}>
            <div style={{ fontSize: '14px' }}>
              <strong>Network:</strong> {process.env.NEXT_PUBLIC_NETWORK || 'testnet'}
            </div>
            <div style={{ fontSize: '14px' }}>
              <strong>Pool App ID:</strong> {process.env.NEXT_PUBLIC_SELTRA_POOL_APP_ID}
            </div>
            {simulatorStatus && (
              <div style={{ fontSize: '14px' }}>
                <strong>Scenario:</strong> {simulatorStatus.current_scenario}
              </div>
            )}
          </div>
          <div style={{ 
            fontSize: '12px', 
            opacity: '0.7'
          }}>
            Seltra AMM - Built on Algorand Blockchain
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
