import { useState, useEffect, useCallback } from 'react'
import { simulationAPI } from '../services/api'

export const useSimulationData = () => {
  const [connectionStatus, setConnectionStatus] = useState({
    market_active: false,
    blockchain_active: false,
    current_price: null,
    total_wallets: 0
  })

  const [marketData, setMarketData] = useState({
    current_price: 0,
    current_volatility: 0,
    price_history: [],
    scenario: 'normal',
    regime: 'medium'
  })

  const [blockchainData, setBlockchainData] = useState({
    wallets: [],
    recent_transactions: [],
    pending_transactions: 0,
    total_transactions: 0,
    success_rate: 0,
    transactions_per_minute: 0,
    current_pattern: 'normal'
  })

  const [error, setError] = useState(null)

  // Fetch current status
  const fetchStatus = useCallback(async () => {
    try {
      const healthData = await simulationAPI.getHealth()
      setConnectionStatus({
        market_active: healthData.market_simulator_active,
        blockchain_active: healthData.blockchain_simulator_active,
        current_price: healthData.current_price,
        total_wallets: healthData.total_wallets
      })

      if (healthData.market_simulator_active) {
        const statusData = await simulationAPI.getStatus()
        setMarketData(prev => ({
          ...prev,
          current_price: statusData.market_simulation.current_price,
          current_volatility: statusData.market_simulation.current_volatility,
          scenario: statusData.market_simulation.scenario,
          regime: statusData.market_simulation.regime,
          uptime_seconds: statusData.market_simulation.uptime
        }))

        setBlockchainData(prev => ({
          ...prev,
          total_transactions: statusData.blockchain_simulation.total_transactions,
          success_rate: statusData.blockchain_simulation.success_rate,
          transactions_per_minute: statusData.blockchain_simulation.transactions_per_minute,
          current_pattern: statusData.blockchain_simulation.current_pattern,
          pending_transactions: statusData.blockchain_simulation.pending_transactions
        }))
      }

      setError(null)
    } catch (err) {
      setError(`Connection failed: ${err.message}`)
    }
  }, [])

  // Fetch price history
  const fetchPriceHistory = useCallback(async () => {
    try {
      const historyData = await simulationAPI.getPriceHistory(50)
      setMarketData(prev => ({
        ...prev,
        price_history: historyData.history
      }))
    } catch (err) {
      console.error('Failed to fetch price history:', err)
    }
  }, [])

  // Fetch wallet information
  const fetchWallets = useCallback(async () => {
    try {
      const walletsData = await simulationAPI.getWallets()
      setBlockchainData(prev => ({
        ...prev,
        wallets: walletsData.wallets
      }))
    } catch (err) {
      console.error('Failed to fetch wallets:', err)
    }
  }, [])

  // Fetch pending transactions
  const fetchPendingTransactions = useCallback(async () => {
    try {
      const pendingData = await simulationAPI.getPendingTransactions()
      setBlockchainData(prev => ({
        ...prev,
        recent_transactions: pendingData.pending_transactions
      }))
    } catch (err) {
      console.error('Failed to fetch pending transactions:', err)
    }
  }, [])

  // Control methods
  const triggerScenario = useCallback(async (scenarioName) => {
    try {
      await simulationAPI.triggerDemoScenario(scenarioName)
      setError(null)
    } catch (err) {
      setError(`Failed to trigger scenario: ${err.message}`)
    }
  }, [])

  const setVolatilityRegime = useCallback(async (regime) => {
    try {
      await simulationAPI.setVolatilityRegime(regime)
      setError(null)
    } catch (err) {
      setError(`Failed to set volatility regime: ${err.message}`)
    }
  }, [])

  const setTradingPattern = useCallback(async (pattern) => {
    try {
      await simulationAPI.setTradingPattern(pattern)
      setError(null)
    } catch (err) {
      setError(`Failed to set trading pattern: ${err.message}`)
    }
  }, [])

  const addPriceShock = useCallback(async (magnitude, duration = 60) => {
    try {
      await simulationAPI.addPriceShock(magnitude, duration)
      setError(null)
    } catch (err) {
      setError(`Failed to add price shock: ${err.message}`)
    }
  }, [])

  // Set up polling intervals
  useEffect(() => {
    // Initial fetch
    fetchStatus()
    fetchPriceHistory()
    fetchWallets()
    fetchPendingTransactions()

    // Set up intervals - optimized for performance
    const statusInterval = setInterval(fetchStatus, 3000) // Every 3 seconds
    const historyInterval = setInterval(fetchPriceHistory, 2000) // Every 2 seconds for charts
    const walletInterval = setInterval(fetchWallets, 15000) // Every 15 seconds
    const txInterval = setInterval(fetchPendingTransactions, 4000) // Every 4 seconds

    return () => {
      clearInterval(statusInterval)
      clearInterval(historyInterval)
      clearInterval(walletInterval)
      clearInterval(txInterval)
    }
  }, [fetchStatus, fetchPriceHistory, fetchWallets, fetchPendingTransactions])

  return {
    connectionStatus,
    marketData,
    blockchainData,
    error,
    triggerScenario,
    setVolatilityRegime,
    setTradingPattern,
    addPriceShock
  }
}
