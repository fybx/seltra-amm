'use client';

import React, { useState } from 'react';
import { useMarketData } from '@/providers/MarketDataProvider';
import { useContract } from '@/providers/ContractProvider';

const MarketDashboard: React.FC = () => {
  const { marketData, simulatorStatus, isConnected, setScenario, setVolatilityRegime, addPriceShock } = useMarketData();
  const { poolState } = useContract();
  const [shockMagnitude, setShockMagnitude] = useState('10');
  const [shockDuration, setShockDuration] = useState('60');

  const scenarios = [
    { id: 'normal', name: 'Normal Market', description: 'Standard trading conditions' },
    { id: 'volatile', name: 'Volatile Market', description: 'High volatility periods' },
    { id: 'calm', name: 'Calm Market', description: 'Low volatility, stable prices' },
    { id: 'trending', name: 'Trending Market', description: 'Strong directional movement' },
    { id: 'flash_crash', name: 'Flash Crash', description: 'Sudden large price drops' }
  ];

  const regimes = [
    { id: 'low', name: 'Low Volatility', color: '#28A745' },
    { id: 'medium', name: 'Medium Volatility', color: '#FFC107' },
    { id: 'high', name: 'High Volatility', color: '#DC3545' }
  ];

  const handleScenarioChange = async (scenario: string) => {
    await setScenario(scenario);
  };

  const handleRegimeChange = async (regime: string) => {
    await setVolatilityRegime(regime);
  };

  const handlePriceShock = async () => {
    await addPriceShock(parseFloat(shockMagnitude), parseInt(shockDuration));
  };

  const formatPrice = (price: number): string => {
    return price.toFixed(6);
  };

  const formatVolatility = (volatility: number): string => {
    return (volatility * 100).toFixed(2) + '%';
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
      {/* Market Metrics */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Market Metrics</h3>
          <p className="card-subtitle">Real-time market data from simulation</p>
        </div>

        {isConnected && marketData ? (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{ 
              padding: '16px', 
              background: '#F0F7FF', 
              borderRadius: '8px',
              border: '1px solid #0066FF'
            }}>
              <div style={{ fontSize: '12px', color: '#6C757D', marginBottom: '4px' }}>
                Current Price
              </div>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#0066FF' }}>
                ${formatPrice(marketData.price)}
              </div>
            </div>

            <div style={{ 
              padding: '16px', 
              background: '#FFFBF0', 
              borderRadius: '8px',
              border: '1px solid #FFD700'
            }}>
              <div style={{ fontSize: '12px', color: '#6C757D', marginBottom: '4px' }}>
                24h Volume
              </div>
              <div style={{ fontSize: '24px', fontWeight: '700', color: '#F1C40F' }}>
                ${marketData.volume.toLocaleString()}
              </div>
            </div>

            <div style={{ 
              padding: '16px', 
              background: regimes.find(r => r.id === marketData.regime)?.id === 'low' ? '#D4EDDA' : 
                         regimes.find(r => r.id === marketData.regime)?.id === 'medium' ? '#FFF3CD' : '#F8D7DA',
              borderRadius: '8px',
              border: `1px solid ${regimes.find(r => r.id === marketData.regime)?.color || '#6C757D'}`
            }}>
              <div style={{ fontSize: '12px', color: '#6C757D', marginBottom: '4px' }}>
                Volatility
              </div>
              <div style={{ 
                fontSize: '20px', 
                fontWeight: '700', 
                color: regimes.find(r => r.id === marketData.regime)?.color || '#6C757D'
              }}>
                {formatVolatility(marketData.volatility)}
              </div>
              <div style={{ fontSize: '12px', marginTop: '4px' }}>
                {regimes.find(r => r.id === marketData.regime)?.name || 'Unknown'}
              </div>
            </div>

            <div style={{ 
              padding: '16px', 
              background: '#F8F9FA', 
              borderRadius: '8px',
              border: '1px solid #E9ECEF'
            }}>
              <div style={{ fontSize: '12px', color: '#6C757D', marginBottom: '4px' }}>
                Scenario
              </div>
              <div style={{ fontSize: '16px', fontWeight: '600', color: '#343A40' }}>
                {scenarios.find(s => s.id === marketData.scenario)?.name || marketData.scenario}
              </div>
            </div>
          </div>
        ) : (
          <div style={{ 
            padding: '32px', 
            textAlign: 'center', 
            color: '#6C757D' 
          }}>
            {isConnected ? 'Loading market data...' : 'Market simulator offline'}
          </div>
        )}
      </div>

      {/* Pool Analytics */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Pool Analytics</h3>
          <p className="card-subtitle">Liquidity distribution and pool metrics</p>
        </div>

        {poolState ? (
          <div>
            <div style={{ marginBottom: '20px' }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                marginBottom: '8px' 
              }}>
                <span style={{ fontSize: '14px', color: '#6C757D' }}>Pool Price:</span>
                <span style={{ fontWeight: '600' }}>
                  {formatPrice(poolState.currentPrice / 1e18)} ALGO/HACK
                </span>
              </div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                marginBottom: '8px' 
              }}>
                <span style={{ fontSize: '14px', color: '#6C757D' }}>Total Liquidity:</span>
                <span style={{ fontWeight: '600' }}>
                  {(poolState.totalLiquidity / 1e6).toFixed(2)} ALGO
                </span>
              </div>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                marginBottom: '8px' 
              }}>
                <span style={{ fontSize: '14px', color: '#6C757D' }}>Fee Rate:</span>
                <span style={{ fontWeight: '600' }}>
                  {(poolState.feeRate / 100).toFixed(2)}%
                </span>
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
                Liquidity Ranges
              </h4>
              {poolState.ranges.map((range) => (
                <div 
                  key={range.id}
                  style={{ 
                    padding: '12px',
                    marginBottom: '8px',
                    background: range.isActive ? '#F0F7FF' : '#F8F9FA',
                    borderRadius: '6px',
                    border: range.isActive ? '1px solid #0066FF' : '1px solid #E9ECEF'
                  }}
                >
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    marginBottom: '4px'
                  }}>
                    <span style={{ fontWeight: '600', fontSize: '14px' }}>
                      Range {range.id}
                    </span>
                    <span style={{
                      padding: '2px 6px',
                      borderRadius: '3px',
                      fontSize: '10px',
                      fontWeight: '600',
                      background: range.isActive ? '#28A745' : '#6C757D',
                      color: 'white'
                    }}>
                      {range.isActive ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: '#6C757D' }}>
                    {formatPrice(range.lower / 1e18)} - {formatPrice(range.upper / 1e18)} ALGO
                  </div>
                  <div style={{ fontSize: '12px', color: '#6C757D' }}>
                    Liquidity: {(range.liquidity / 1e6).toFixed(2)} ALGO
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ 
            padding: '32px', 
            textAlign: 'center', 
            color: '#6C757D' 
          }}>
            Loading pool data...
          </div>
        )}
      </div>

      {/* Market Controls */}
      <div className="card" style={{ gridColumn: 'span 2' }}>
        <div className="card-header">
          <h3 className="card-title">Market Controls</h3>
          <p className="card-subtitle">Control simulation scenarios and market conditions</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '24px' }}>
          {/* Scenario Control */}
          <div>
            <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
              Market Scenario
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {scenarios.map((scenario) => (
                <button
                  key={scenario.id}
                  onClick={() => handleScenarioChange(scenario.id)}
                  style={{
                    padding: '12px',
                    border: marketData?.scenario === scenario.id ? '2px solid #0066FF' : '2px solid #E9ECEF',
                    borderRadius: '6px',
                    background: marketData?.scenario === scenario.id ? '#F0F7FF' : 'white',
                    color: marketData?.scenario === scenario.id ? '#0066FF' : '#6C757D',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '14px'
                  }}
                >
                  <div style={{ fontWeight: '600' }}>{scenario.name}</div>
                  <div style={{ fontSize: '12px', opacity: '0.8' }}>{scenario.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Volatility Control */}
          <div>
            <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
              Volatility Regime
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {regimes.map((regime) => (
                <button
                  key={regime.id}
                  onClick={() => handleRegimeChange(regime.id)}
                  style={{
                    padding: '12px',
                    border: marketData?.regime === regime.id ? `2px solid ${regime.color}` : '2px solid #E9ECEF',
                    borderRadius: '6px',
                    background: marketData?.regime === regime.id ? `${regime.color}20` : 'white',
                    color: marketData?.regime === regime.id ? regime.color : '#6C757D',
                    cursor: 'pointer',
                    textAlign: 'center',
                    fontSize: '14px',
                    fontWeight: '600'
                  }}
                >
                  {regime.name}
                </button>
              ))}
            </div>
          </div>

          {/* Price Shock Control */}
          <div>
            <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
              Price Shock
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '12px', color: '#6C757D', display: 'block', marginBottom: '4px' }}>
                  Magnitude (%)
                </label>
                <input
                  type="number"
                  value={shockMagnitude}
                  onChange={(e) => setShockMagnitude(e.target.value)}
                  className="input"
                  style={{ fontSize: '14px', padding: '8px' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', color: '#6C757D', display: 'block', marginBottom: '4px' }}>
                  Duration (seconds)
                </label>
                <input
                  type="number"
                  value={shockDuration}
                  onChange={(e) => setShockDuration(e.target.value)}
                  className="input"
                  style={{ fontSize: '14px', padding: '8px' }}
                />
              </div>
              <button
                onClick={handlePriceShock}
                className="btn-secondary"
                style={{ fontSize: '14px', padding: '10px' }}
              >
                Apply Shock
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketDashboard;
