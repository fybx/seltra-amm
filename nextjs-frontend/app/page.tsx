'use client';

import React, { useState } from 'react';
import SwapInterface from '@/components/SwapInterface';
import LiquidityInterface from '@/components/LiquidityInterface';
import MarketDashboard from '@/components/MarketDashboard';
import TransactionMonitor from '@/components/TransactionMonitor';
import BalanceTracker from '@/components/BalanceTracker';
import { useWallet } from '@/providers/WalletProvider';
import { useMarketData } from '@/providers/MarketDataProvider';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<'swap' | 'liquidity' | 'analytics'>('swap');
  const { wallet } = useWallet();
  const { marketData, isConnected } = useMarketData();

  const tabs = [
    { id: 'swap', name: 'Swap', description: 'Exchange tokens with dynamic pricing' },
    { id: 'liquidity', name: 'Liquidity', description: 'Manage concentrated liquidity positions' },
    { id: 'analytics', name: 'Analytics', description: 'Market data and pool metrics' }
  ];

  return (
    <div>
      {/* Hero Section */}
      <div style={{
        background: 'linear-gradient(135deg, #0066FF 0%, #FFD700 100%)',
        borderRadius: '16px',
        padding: '48px 32px',
        marginBottom: '32px',
        color: 'white',
        textAlign: 'center'
      }}>
        <h1 style={{
          fontSize: '48px',
          fontWeight: '700',
          margin: '0 0 16px 0',
          background: 'linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          Seltra AMM
        </h1>
        <p style={{
          fontSize: '20px',
          margin: '0 0 24px 0',
          opacity: '0.9'
        }}>
          Intelligent Dynamic Liquidity Protocol on Algorand
        </p>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '32px',
          flexWrap: 'wrap'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: '700' }}>
              {marketData ? `$${marketData.price.toFixed(4)}` : '--'}
            </div>
            <div style={{ fontSize: '14px', opacity: '0.8' }}>Current Price</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: '700' }}>
              {marketData ? `${(marketData.volatility * 100).toFixed(2)}%` : '--'}
            </div>
            <div style={{ fontSize: '14px', opacity: '0.8' }}>Volatility</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: '700' }}>
              {isConnected ? 'Live' : 'Offline'}
            </div>
            <div style={{ fontSize: '14px', opacity: '0.8' }}>Market Status</div>
          </div>
        </div>
      </div>

      {/* Connection Status */}
      {!wallet.isConnected && (
        <div style={{
          background: '#FFF3CD',
          border: '1px solid #FFEAA7',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '16px', fontWeight: '600', color: '#856404', marginBottom: '8px' }}>
            Connect Your Wallet
          </div>
          <div style={{ fontSize: '14px', color: '#856404' }}>
            Connect your Pera Wallet to start trading and providing liquidity
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div style={{
        display: 'flex',
        marginBottom: '32px',
        background: 'white',
        borderRadius: '12px',
        padding: '8px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        border: '1px solid #E9ECEF'
      }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            style={{
              flex: 1,
              padding: '16px 24px',
              border: 'none',
              borderRadius: '8px',
              background: activeTab === tab.id ? 
                'linear-gradient(135deg, #0066FF 0%, #0052CC 100%)' : 
                'transparent',
              color: activeTab === tab.id ? 'white' : '#6C757D',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              textAlign: 'center'
            }}
          >
            <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '4px' }}>
              {tab.name}
            </div>
            <div style={{ 
              fontSize: '12px', 
              opacity: activeTab === tab.id ? '0.9' : '0.7'
            }}>
              {tab.description}
            </div>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'swap' && <SwapInterface />}
        {activeTab === 'liquidity' && <LiquidityInterface />}
        {activeTab === 'analytics' && <MarketDashboard />}
      </div>

      {/* Grafik Arayüz Bileşenleri */}
      <div style={{ display: 'flex', gap: '24px', marginTop: '32px' }}>
        <div style={{ flex: 1 }}>
          <BalanceTracker />
        </div>
      </div>

      {/* Transaction Monitor - Floating */}
      <TransactionMonitor />

      {/* Features Section */}
      <div style={{ marginTop: '64px' }}>
        <h2 style={{
          fontSize: '32px',
          fontWeight: '700',
          textAlign: 'center',
          marginBottom: '48px',
          color: '#343A40'
        }}>
          Why Choose Seltra AMM?
        </h2>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '24px'
        }}>
          <div className="card">
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #0066FF 0%, #0052CC 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '16px',
              fontSize: '24px',
              color: 'white'
            }}>
              ⚡
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '12px' }}>
              Dynamic Liquidity
            </h3>
            <p style={{ color: '#6C757D', lineHeight: '1.6' }}>
              Automatically adjusts liquidity concentration based on market volatility for optimal capital efficiency.
            </p>
          </div>

          <div className="card">
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #FFD700 0%, #F1C40F 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '16px',
              fontSize: '24px',
              color: '#343A40'
            }}>
              🎯
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '12px' }}>
              Smart Rebalancing
            </h3>
            <p style={{ color: '#6C757D', lineHeight: '1.6' }}>
              Intelligent rebalancing engine responds to market conditions in real-time for better returns.
            </p>
          </div>

          <div className="card">
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #28A745 0%, #20C997 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '16px',
              fontSize: '24px',
              color: 'white'
            }}>
              🔒
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '12px' }}>
              Algorand Security
            </h3>
            <p style={{ color: '#6C757D', lineHeight: '1.6' }}>
              Built on Algorand blockchain with 4.5-second finality and enterprise-grade security.
            </p>
          </div>
        </div>
      </div>

      {/* Transaction Monitor */}
      <TransactionMonitor />
    </div>
  );
}
