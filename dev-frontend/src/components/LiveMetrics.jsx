import React from 'react'
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  LinearProgress,
  Divider
} from '@mui/material'
import {
  Assessment,
  TrendingUp,
  Speed,
  Timer,
  CheckCircle,
  Error,
  AccountBalance,
  ShowChart
} from '@mui/icons-material'

const MetricCard = ({ icon, label, value, subtitle, color = 'primary', progress }) => (
  <Box
    p={2}
    sx={{
      backgroundColor: 'rgba(255, 255, 255, 0.03)',
      borderRadius: 1,
      border: '1px solid rgba(255, 255, 255, 0.1)',
      height: '100%'
    }}
  >
    <Box display="flex" alignItems="center" gap={1} mb={1}>
      <Box sx={{ color: `${color}.main` }}>
        {icon}
      </Box>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
    </Box>
    <Typography variant="h5" fontWeight={600} sx={{ color: `${color}.main` }}>
      {value}
    </Typography>
    {subtitle && (
      <Typography variant="caption" color="text.secondary">
        {subtitle}
      </Typography>
    )}
    {progress !== undefined && (
      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{
          mt: 1,
          height: 4,
          borderRadius: 2,
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          '& .MuiLinearProgress-bar': {
            backgroundColor: `${color}.main`
          }
        }}
      />
    )}
  </Box>
)

const formatDuration = (seconds) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  if (minutes > 0) {
    return `${minutes}m ${secs}s`
  }
  return `${secs}s`
}

const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num?.toFixed?.(0) || '0'
}

const LiveMetrics = ({ marketData = {}, blockchainData = {} }) => {
  const {
    current_price = 0,
    current_volatility = 0,
    scenario = 'normal',
    regime = 'medium'
  } = marketData

  const {
    total_transactions = 0,
    success_rate = 0,
    transactions_per_minute = 0,
    current_pattern = 'normal',
    pending_transactions = 0,
    wallets = []
  } = blockchainData

  const uptime = marketData?.uptime_seconds || 0
  const activeWallets = wallets?.length || 0

  return (
    <Card sx={{ height: 500 }}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <Assessment sx={{ color: 'primary.main' }} />
            <Typography variant="h6">Live Metrics</Typography>
          </Box>
        }
        action={
          <Chip
            label={`Uptime: ${formatDuration(uptime)}`}
            color="success"
            variant="outlined"
            size="small"
          />
        }
        sx={{ pb: 1 }}
      />
      <CardContent sx={{ height: 420, pt: 0, overflowY: 'auto' }}>
        <Grid container spacing={1.5} sx={{ minHeight: '100%' }}>
          {/* Market Metrics */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ShowChart />
              Market Status
            </Typography>
          </Grid>
          
          <Grid item xs={6}>
            <MetricCard
              icon={<TrendingUp />}
              label="Current Price"
              value={`$${current_price.toFixed(4)}`}
              subtitle={`Scenario: ${scenario}`}
              color="success"
            />
          </Grid>

          <Grid item xs={6}>
            <MetricCard
              icon={<Speed />}
              label="Volatility"
              value={`${(current_volatility * 100).toFixed(2)}%`}
              subtitle={`${regime.charAt(0).toUpperCase() + regime.slice(1)} regime`}
              color={regime === 'low' ? 'success' : regime === 'medium' ? 'warning' : 'error'}
              progress={Math.min((current_volatility / 0.15) * 100, 100)}
            />
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 1 }} />
            <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <AccountBalance />
              Blockchain Status
            </Typography>
          </Grid>

          <Grid item xs={6}>
            <MetricCard
              icon={<Timer />}
              label="Transactions"
              value={formatNumber(total_transactions)}
              subtitle={`${transactions_per_minute.toFixed(1)}/min`}
              color="info"
            />
          </Grid>

          <Grid item xs={6}>
            <MetricCard
              icon={success_rate >= 95 ? <CheckCircle /> : <Error />}
              label="Success Rate"
              value={`${success_rate.toFixed(1)}%`}
              subtitle={`${pending_transactions} pending`}
              color={success_rate >= 95 ? 'success' : success_rate >= 85 ? 'warning' : 'error'}
              progress={success_rate}
            />
          </Grid>

          <Grid item xs={6}>
            <MetricCard
              icon={<AccountBalance />}
              label="Active Wallets"
              value={activeWallets.toString()}
              subtitle={`Pattern: ${current_pattern}`}
              color="primary"
            />
          </Grid>

          <Grid item xs={6}>
            <MetricCard
              icon={<Speed />}
              label="Network Load"
              value={pending_transactions > 20 ? 'High' : pending_transactions > 10 ? 'Medium' : 'Low'}
              subtitle={`${pending_transactions} queued`}
              color={pending_transactions > 20 ? 'error' : pending_transactions > 10 ? 'warning' : 'success'}
              progress={Math.min((pending_transactions / 30) * 100, 100)}
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}

export default LiveMetrics
