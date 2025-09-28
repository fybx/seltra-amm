import React, { useState, useEffect } from 'react'
import { 
  Container, 
  Grid, 
  Typography, 
  AppBar, 
  Toolbar, 
  Box,
  Alert,
  Chip
} from '@mui/material'
import { Timeline, ShowChart, Assessment, AccountBalance } from '@mui/icons-material'

import SimulationControls from './components/SimulationControls'
import PriceChart from './components/PriceChart'
import VolatilityChart from './components/VolatilityChart'
import VolumeChart from './components/VolumeChart'
import TransactionActivity from './components/TransactionActivity'
import WalletStatus from './components/WalletStatus'
import LiveMetrics from './components/LiveMetrics'
import { useSimulationData } from './hooks/useSimulationData'

function App() {
  const {
    connectionStatus,
    marketData,
    blockchainData,
    error,
    triggerScenario,
    setVolatilityRegime,
    setTradingPattern,
    addPriceShock
  } = useSimulationData()

  return (
    <>
      {/* Header */}
      <AppBar position="static" sx={{ background: 'linear-gradient(90deg, #000 0%, #1a1a1a 100%)' }}>
        <Toolbar>
          <ShowChart sx={{ mr: 2, color: '#00d4ff' }} />
          <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            Seltra Dev Console
          </Typography>
          <Box display="flex" gap={1} alignItems="center">
            <Chip 
              icon={<Timeline />}
              label={`Market: ${connectionStatus.market_active ? 'LIVE' : 'OFFLINE'}`}
              color={connectionStatus.market_active ? 'success' : 'error'}
              variant="outlined"
              size="small"
            />
            <Chip 
              icon={<AccountBalance />}
              label={`Blockchain: ${connectionStatus.blockchain_active ? 'LIVE' : 'OFFLINE'}`}
              color={connectionStatus.blockchain_active ? 'success' : 'error'}
              variant="outlined"
              size="small"
            />
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth={false} sx={{ mt: 2, mb: 2 }}>
        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Top Row - Controls and Live Metrics */}
          <Grid item xs={12} md={8}>
            <SimulationControls
              onTriggerScenario={triggerScenario}
              onSetVolatilityRegime={setVolatilityRegime}
              onSetTradingPattern={setTradingPattern}
              onAddPriceShock={addPriceShock}
              currentScenario={marketData?.scenario}
              currentRegime={marketData?.regime}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <LiveMetrics 
              marketData={marketData}
              blockchainData={blockchainData}
            />
          </Grid>

          {/* Charts Row */}
          <Grid item xs={12} lg={8}>
            <PriceChart priceHistory={marketData?.price_history || []} />
          </Grid>
          <Grid item xs={12} lg={4}>
            <VolatilityChart 
              currentVolatility={marketData?.current_volatility}
              regime={marketData?.regime}
            />
          </Grid>

          {/* Second Charts Row */}
          <Grid item xs={12} lg={8}>
            <VolumeChart priceHistory={marketData?.price_history || []} />
          </Grid>
          <Grid item xs={12} lg={4}>
            <TransactionActivity 
              transactions={blockchainData?.recent_transactions || []}
              pendingCount={blockchainData?.pending_transactions || 0}
            />
          </Grid>

          {/* Bottom Row - Wallet Status */}
          <Grid item xs={12}>
            <WalletStatus wallets={blockchainData?.wallets || []} />
          </Grid>
        </Grid>
      </Container>
    </>
  )
}

export default App
