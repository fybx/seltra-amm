'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { MarketData, SimulatorStatus } from '@/types';
import { getSimulatorUrl } from '@/utils/config';

interface MarketDataContextType {
  marketData: MarketData | null;
  simulatorStatus: SimulatorStatus | null;
  isConnected: boolean;
  setScenario: (scenario: string) => Promise<void>;
  setVolatilityRegime: (regime: string) => Promise<void>;
  addPriceShock: (magnitude: number, duration: number) => Promise<void>;
}

const MarketDataContext = createContext<MarketDataContextType | undefined>(undefined);

export const useMarketData = () => {
  const context = useContext(MarketDataContext);
  if (!context) {
    throw new Error('useMarketData must be used within a MarketDataProvider');
  }
  return context;
};

interface MarketDataProviderProps {
  children: ReactNode;
}

export const MarketDataProvider: React.FC<MarketDataProviderProps> = ({ children }) => {
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [simulatorStatus, setSimulatorStatus] = useState<SimulatorStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const simulatorUrl = getSimulatorUrl();

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const fetchData = async () => {
      try {
        // Fetch current market status
        const statusResponse = await axios.get(`${simulatorUrl}/api/v1/status`);
        setSimulatorStatus(statusResponse.data);
        setIsConnected(true);

        // Fetch market metrics
        const metricsResponse = await axios.get(`${simulatorUrl}/api/v1/metrics`);
        const metrics = metricsResponse.data;

        // Fetch price history
        const historyResponse = await axios.get(`${simulatorUrl}/api/v1/history?window=50`);
        const history = historyResponse.data.history;

        const currentData: MarketData = {
          price: metrics.current_price || 100,
          volume: metrics.current_volume || 0,
          volatility: metrics.current_volatility || 0.02,
          regime: metrics.regime || 'medium',
          scenario: metrics.scenario || 'normal',
          timestamp: Date.now(),
          price_history: history.map((point: any) => ({
            price: point.price,
            volume: point.volume,
            timestamp: point.timestamp
          }))
        };

        setMarketData(currentData);
      } catch (error) {
        console.error('Error fetching market data:', error);
        setIsConnected(false);
      }
    };

    // Initial fetch
    fetchData();

    // Set up polling interval
    intervalId = setInterval(fetchData, 2000); // Update every 2 seconds

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [simulatorUrl]);

  const setScenario = async (scenario: string) => {
    try {
      await axios.post(`${simulatorUrl}/api/v1/scenario`, { scenario });
    } catch (error) {
      console.error('Error setting scenario:', error);
    }
  };

  const setVolatilityRegime = async (regime: string) => {
    try {
      await axios.post(`${simulatorUrl}/api/v1/volatility`, { regime });
    } catch (error) {
      console.error('Error setting volatility regime:', error);
    }
  };

  const addPriceShock = async (magnitude: number, duration: number) => {
    try {
      await axios.post(`${simulatorUrl}/api/v1/shock`, { 
        magnitude, 
        duration 
      });
    } catch (error) {
      console.error('Error adding price shock:', error);
    }
  };

  return (
    <MarketDataContext.Provider value={{
      marketData,
      simulatorStatus,
      isConnected,
      setScenario,
      setVolatilityRegime,
      addPriceShock
    }}>
      {children}
    </MarketDataContext.Provider>
  );
};
