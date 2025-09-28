import axios from 'axios'

// Use environment variable or default to localhost
const API_BASE_URL = import.meta.env.VITE_SIMULATOR_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const simulationAPI = {
  // Health and status
  getHealth: async () => {
    const response = await api.get('/health')
    return response.data
  },

  getStatus: async () => {
    const response = await api.get('/api/v1/status')
    return response.data
  },

  // Market data
  getCurrentPrice: async () => {
    const response = await api.get('/api/v1/price')
    return response.data
  },

  getPriceHistory: async (window = 50) => {
    const response = await api.get(`/api/v1/history?window=${window}`)
    return response.data
  },

  getMetrics: async () => {
    const response = await api.get('/api/v1/metrics')
    return response.data
  },

  // Market control
  setScenario: async (scenario) => {
    const response = await api.post('/api/v1/scenario', { scenario })
    return response.data
  },

  setVolatilityRegime: async (regime) => {
    const response = await api.post('/api/v1/volatility', { regime })
    return response.data
  },

  addPriceShock: async (magnitude, duration = 60) => {
    const response = await api.post('/api/v1/shock', { magnitude, duration })
    return response.data
  },

  setVolumeProfile: async (profile) => {
    const response = await api.post('/api/v1/volume/profile', { profile })
    return response.data
  },

  addVolumeSpike: async (multiplier, duration) => {
    const response = await api.post('/api/v1/volume/spike', { multiplier, duration })
    return response.data
  },

  simulateTrade: async (size, direction = 'buy') => {
    const response = await api.post('/api/v1/trade/simulate', { size, direction })
    return response.data
  },

  resetSimulation: async (initialPrice = null) => {
    const params = initialPrice ? `?initial_price=${initialPrice}` : ''
    const response = await api.post(`/api/v1/reset${params}`)
    return response.data
  },

  // Blockchain simulation
  getWallets: async () => {
    const response = await api.get('/api/v1/blockchain/wallets')
    return response.data
  },

  getBlockchainMetrics: async () => {
    const response = await api.get('/api/v1/blockchain/metrics')
    return response.data
  },

  setTradingPattern: async (pattern) => {
    const response = await api.post('/api/v1/blockchain/pattern', { pattern })
    return response.data
  },

  resetBlockchainSimulation: async () => {
    const response = await api.post('/api/v1/blockchain/reset')
    return response.data
  },

  getPendingTransactions: async () => {
    const response = await api.get('/api/v1/blockchain/transactions/pending')
    return response.data
  },

  // Demo scenarios
  triggerDemoScenario: async (scenarioName) => {
    const response = await api.post(`/api/v1/demo/scenario?scenario_name=${scenarioName}`)
    return response.data
  }
}

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      throw new Error(`API Error: ${error.response.data.detail || error.response.statusText}`)
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('No response from simulation server. Is it running?')
    } else {
      // Something else happened
      throw new Error(`Request error: ${error.message}`)
    }
  }
)
