import React, { useState, useEffect } from 'react';
import './App.css';

// Configuration from environment variables
const ALGOD_ADDRESS = process.env.REACT_APP_ALGOD_ADDRESS || 'http://localhost:4001';
const ALGOD_TOKEN = process.env.REACT_APP_ALGOD_TOKEN || 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
const INDEXER_ADDRESS = process.env.REACT_APP_INDEXER_ADDRESS || 'http://localhost:8980';
const SIMULATOR_ADDRESS = process.env.REACT_APP_SIMULATOR_ADDRESS || 'http://localhost:8001';

function App() {
  const [networkStatus, setNetworkStatus] = useState({
    algod: 'checking...',
    indexer: 'checking...',
    simulator: 'checking...'
  });

  const checkServices = async () => {
    // Check Algod
    try {
      const response = await fetch(`${ALGOD_ADDRESS}/health`);
      setNetworkStatus(prev => ({ 
        ...prev, 
        algod: response.ok ? 'connected' : 'error' 
      }));
    } catch (error) {
      setNetworkStatus(prev => ({ ...prev, algod: 'error' }));
    }

    // Check Indexer
    try {
      const response = await fetch(`${INDEXER_ADDRESS}/health`);
      setNetworkStatus(prev => ({ 
        ...prev, 
        indexer: response.ok ? 'connected' : 'error' 
      }));
    } catch (error) {
      setNetworkStatus(prev => ({ ...prev, indexer: 'error' }));
    }

    // Check Simulator
    try {
      const response = await fetch(`${SIMULATOR_ADDRESS}/health`);
      setNetworkStatus(prev => ({ 
        ...prev, 
        simulator: response.ok ? 'connected' : 'error' 
      }));
    } catch (error) {
      setNetworkStatus(prev => ({ ...prev, simulator: 'error' }));
    }
  };

  useEffect(() => {
    checkServices();
    const interval = setInterval(checkServices, 10000); // Check every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return '#4CAF50';
      case 'error': return '#F44336';
      default: return '#FF9800';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔄 Seltra AMM</h1>
        <p>Intelligent, self-adapting liquidity pools</p>
        
        <div className="network-status">
          <h3>Network Status</h3>
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Algod:</span>
              <span 
                className="status-indicator" 
                style={{ color: getStatusColor(networkStatus.algod) }}
              >
                ● {networkStatus.algod}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Indexer:</span>
              <span 
                className="status-indicator" 
                style={{ color: getStatusColor(networkStatus.indexer) }}
              >
                ● {networkStatus.indexer}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Simulator:</span>
              <span 
                className="status-indicator" 
                style={{ color: getStatusColor(networkStatus.simulator) }}
              >
                ● {networkStatus.simulator}
              </span>
            </div>
          </div>
        </div>

        <div className="features-preview">
          <h3>Coming Soon</h3>
          <ul>
            <li>🎯 Dynamic Liquidity Concentration</li>
            <li>🧠 Smart Rebalancing Engine</li>
            <li>📈 Adaptive Fee Structure</li>
            <li>⚡ Real-time Market Simulation</li>
            <li>💼 LP Dashboard & Analytics</li>
          </ul>
        </div>

        <button onClick={checkServices} className="refresh-button">
          Refresh Status
        </button>
      </header>
    </div>
  );
}

export default App;
