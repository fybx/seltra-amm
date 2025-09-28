import React, { useState, useEffect } from "react";
import "./ContractDashboard.css";

const ContractDashboard = () => {
  const [contractState, setContractState] = useState({
    poolState: null,
    liquidityRanges: [],
    volatility: null,
    efficiency: null,
    loading: true,
    error: null,
  });

  const [walletConnected, setWalletConnected] = useState(false);
  const [userAddress, setUserAddress] = useState("");
  const [swapAmount, setSwapAmount] = useState("");
  const [swapDirection, setSwapDirection] = useState("ALGO_TO_HACK");

  // Contract addresses from deployment
  const CONTRACT_ADDRESSES = {
    seltraPool: 1001,
    hackToken: 1002,
    oracle: 1003,
    explorerBase: "https://lora.algokit.io/localnet",
  };

  useEffect(() => {
    fetchContractState();
    const interval = setInterval(fetchContractState, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchContractState = async () => {
    try {
      const response = await fetch(
        "http://localhost:8001/api/contract-metrics"
      );
      if (response.ok) {
        const data = await response.json();
        setContractState({
          poolState: data.pool_state,
          liquidityRanges: data.liquidity_ranges || [],
          volatility: data.volatility,
          efficiency: data.efficiency,
          loading: false,
          error: null,
        });
      } else {
        throw new Error("Failed to fetch contract state");
      }
    } catch (error) {
      console.error("Error fetching contract state:", error);
      setContractState((prev) => ({
        ...prev,
        loading: false,
        error: error.message,
      }));
    }
  };

  const connectWallet = async () => {
    // Simulate wallet connection for demo
    setWalletConnected(true);
    setUserAddress(
      "D3T5QSYOWI2NFLKI4GGMNJDMCH7WRK7LEEZTUVSNWBKYHHYLSOKGYU5K6M"
    );
  };

  const executeSwap = async () => {
    if (!walletConnected || !swapAmount) return;

    try {
      const response = await fetch("http://localhost:8001/api/execute-swap", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userAddress,
          assetIn:
            swapDirection === "ALGO_TO_HACK" ? 0 : CONTRACT_ADDRESSES.hackToken,
          assetOut:
            swapDirection === "ALGO_TO_HACK" ? CONTRACT_ADDRESSES.hackToken : 0,
          amountIn: parseInt(swapAmount) * 1000000, // Convert to microAlgos
          minAmountOut: 0,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Swap executed! Transaction ID: ${result.transactionId}`);
        fetchContractState(); // Refresh state
      } else {
        throw new Error("Swap failed");
      }
    } catch (error) {
      console.error("Swap error:", error);
      alert(`Swap failed: ${error.message}`);
    }
  };

  const triggerRebalance = async () => {
    try {
      const response = await fetch(
        "http://localhost:8001/api/trigger-rebalance",
        {
          method: "POST",
        }
      );

      if (response.ok) {
        const result = await response.json();
        alert(`Rebalance triggered! Transaction ID: ${result.transactionId}`);
        fetchContractState(); // Refresh state
      } else {
        throw new Error("Rebalance failed");
      }
    } catch (error) {
      console.error("Rebalance error:", error);
      alert(`Rebalance failed: ${error.message}`);
    }
  };

  const formatPrice = (price) => {
    return (price / 1e18).toFixed(6);
  };

  const formatLiquidity = (liquidity) => {
    return (liquidity / 1e6).toFixed(2);
  };

  const getVolatilityColor = (regime) => {
    switch (regime) {
      case "low":
        return "#4CAF50";
      case "medium":
        return "#FF9800";
      case "high":
        return "#F44336";
      default:
        return "#9E9E9E";
    }
  };

  if (contractState.loading) {
    return (
      <div className="contract-dashboard">
        <div className="loading">Loading contract state...</div>
      </div>
    );
  }

  if (contractState.error) {
    return (
      <div className="contract-dashboard">
        <div className="error">Error: {contractState.error}</div>
      </div>
    );
  }

  return (
    <div className="contract-dashboard">
      <header className="dashboard-header">
        <h1>🔄 Seltra AMM - Live Contract Dashboard</h1>
        <div className="wallet-section">
          {!walletConnected ? (
            <button onClick={connectWallet} className="connect-wallet-btn">
              Connect Wallet
            </button>
          ) : (
            <div className="wallet-info">
              <span className="wallet-address">
                {userAddress.slice(0, 8)}...{userAddress.slice(-8)}
              </span>
              <button
                onClick={() => setWalletConnected(false)}
                className="disconnect-btn"
              >
                Disconnect
              </button>
            </div>
          )}
        </div>
      </header>

      <div className="dashboard-grid">
        {/* Pool State */}
        <div className="card pool-state">
          <h3>Pool State</h3>
          {contractState.poolState && (
            <div className="pool-info">
              <div className="info-row">
                <span>Current Price:</span>
                <span className="price">
                  {formatPrice(contractState.poolState.current_price)} ALGO/HACK
                </span>
              </div>
              <div className="info-row">
                <span>Total Liquidity:</span>
                <span>
                  {formatLiquidity(contractState.poolState.total_liquidity)}{" "}
                  ALGO
                </span>
              </div>
              <div className="info-row">
                <span>Fee Rate:</span>
                <span>{contractState.poolState.fee_rate / 100}%</span>
              </div>
              <div className="info-row">
                <span>Asset X (ALGO):</span>
                <span>{contractState.poolState.asset_x_id}</span>
              </div>
              <div className="info-row">
                <span>Asset Y (HACK):</span>
                <span>{contractState.poolState.asset_y_id}</span>
              </div>
            </div>
          )}
        </div>

        {/* Volatility & Efficiency */}
        <div className="card volatility-card">
          <h3>Market Conditions</h3>
          {contractState.volatility && (
            <div className="volatility-info">
              <div className="volatility-meter">
                <div
                  className="volatility-indicator"
                  style={{
                    backgroundColor: getVolatilityColor(
                      contractState.volatility.regime
                    ),
                  }}
                >
                  {contractState.volatility.regime.toUpperCase()}
                </div>
                <span className="volatility-value">
                  {contractState.volatility.current.toFixed(2)}%
                </span>
              </div>
              <div className="efficiency-score">
                <span>Efficiency Score:</span>
                <span className="efficiency-value">
                  {contractState.efficiency
                    ? contractState.efficiency.toFixed(1)
                    : "N/A"}
                  %
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Liquidity Ranges */}
        <div className="card liquidity-ranges">
          <h3>Liquidity Ranges</h3>
          <div className="ranges-container">
            {contractState.liquidityRanges.map((range, index) => (
              <div key={range.range_id} className="range-item">
                <div className="range-header">
                  <span>Range {range.range_id}</span>
                  <span
                    className={`status ${
                      range.is_active ? "active" : "inactive"
                    }`}
                  >
                    {range.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                <div className="range-details">
                  <div>
                    Price: {formatPrice(range.price_lower)} -{" "}
                    {formatPrice(range.price_upper)}
                  </div>
                  <div>Liquidity: {formatLiquidity(range.liquidity)} ALGO</div>
                </div>
                <div className="range-visualization">
                  <div
                    className="range-bar"
                    style={{
                      width: "100%",
                      height: "20px",
                      backgroundColor: range.is_active ? "#4CAF50" : "#E0E0E0",
                      borderRadius: "10px",
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Trading Interface */}
        <div className="card trading-interface">
          <h3>Trading Interface</h3>
          <div className="swap-form">
            <div className="swap-direction">
              <label>
                <input
                  type="radio"
                  value="ALGO_TO_HACK"
                  checked={swapDirection === "ALGO_TO_HACK"}
                  onChange={(e) => setSwapDirection(e.target.value)}
                />
                ALGO → HACK
              </label>
              <label>
                <input
                  type="radio"
                  value="HACK_TO_ALGO"
                  checked={swapDirection === "HACK_TO_ALGO"}
                  onChange={(e) => setSwapDirection(e.target.value)}
                />
                HACK → ALGO
              </label>
            </div>
            <div className="amount-input">
              <input
                type="number"
                placeholder="Amount"
                value={swapAmount}
                onChange={(e) => setSwapAmount(e.target.value)}
                disabled={!walletConnected}
              />
              <span className="asset-label">
                {swapDirection === "ALGO_TO_HACK" ? "ALGO" : "HACK"}
              </span>
            </div>
            <button
              onClick={executeSwap}
              disabled={!walletConnected || !swapAmount}
              className="swap-btn"
            >
              Execute Swap
            </button>
          </div>
        </div>

        {/* Contract Links */}
        <div className="card contract-links">
          <h3>Contract Explorer</h3>
          <div className="links">
            <a
              href={`${CONTRACT_ADDRESSES.explorerBase}/application/${CONTRACT_ADDRESSES.seltraPool}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              SeltraPool Contract
            </a>
            <a
              href={`${CONTRACT_ADDRESSES.explorerBase}/asset/${CONTRACT_ADDRESSES.hackToken}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              HACK Token
            </a>
            <a
              href={`${CONTRACT_ADDRESSES.explorerBase}/application/${CONTRACT_ADDRESSES.oracle}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              Volatility Oracle
            </a>
          </div>
        </div>

        {/* Rebalancing Controls */}
        <div className="card rebalancing-controls">
          <h3>Rebalancing Controls</h3>
          <div className="rebalance-info">
            <p>Trigger manual rebalancing based on current market conditions</p>
            <button onClick={triggerRebalance} className="rebalance-btn">
              Trigger Rebalance
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContractDashboard;
