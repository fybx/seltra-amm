import React from 'react'
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip
} from '@mui/material'
import { Speed, TrendingUp, Warning } from '@mui/icons-material'

const VOLATILITY_THRESHOLDS = {
  low: { min: 0, max: 0.01, color: '#4caf50', label: 'Low' },
  medium: { min: 0.01, max: 0.05, color: '#ff9800', label: 'Medium' },
  high: { min: 0.05, max: 0.20, color: '#f44336', label: 'High' },
  extreme: { min: 0.20, max: 1.0, color: '#9c27b0', label: 'Extreme' }
}

const getVolatilityLevel = (volatility) => {
  for (const [key, threshold] of Object.entries(VOLATILITY_THRESHOLDS)) {
    if (volatility >= threshold.min && volatility < threshold.max) {
      return { level: key, ...threshold }
    }
  }
  return { level: 'extreme', ...VOLATILITY_THRESHOLDS.extreme }
}

const VolatilityChart = ({ currentVolatility = 0, regime = 'medium' }) => {
  const volatilityPercent = currentVolatility * 100
  const volLevel = getVolatilityLevel(currentVolatility)
  
  // Calculate progress bar value (0-100)
  const maxDisplayVol = 0.15 // 15% max for display
  const progressValue = Math.min((currentVolatility / maxDisplayVol) * 100, 100)

  const getIcon = () => {
    switch (volLevel.level) {
      case 'low':
        return <Speed sx={{ color: volLevel.color }} />
      case 'medium':
        return <TrendingUp sx={{ color: volLevel.color }} />
      case 'high':
      case 'extreme':
        return <Warning sx={{ color: volLevel.color }} />
      default:
        return <Speed />
    }
  }

  return (
    <Card sx={{ height: 400 }}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            {getIcon()}
            <Typography variant="h6">Volatility Monitor</Typography>
          </Box>
        }
        action={
          <Chip
            label={`${volLevel.label} Regime`}
            sx={{ 
              backgroundColor: volLevel.color,
              color: 'white',
              fontWeight: 600
            }}
          />
        }
      />
      <CardContent>
        <Box mb={3}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Current Volatility
            </Typography>
            <Typography variant="h4" fontWeight={600} sx={{ color: volLevel.color }}>
              {volatilityPercent.toFixed(2)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={progressValue}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: volLevel.color,
                borderRadius: 4
              }
            }}
          />
        </Box>

        {/* Volatility Levels */}
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Volatility Levels
          </Typography>
          {Object.entries(VOLATILITY_THRESHOLDS).map(([key, threshold]) => {
            const isActive = key === volLevel.level
            return (
              <Box
                key={key}
                display="flex"
                alignItems="center"
                justifyContent="space-between"
                py={1}
                px={2}
                mb={1}
                sx={{
                  backgroundColor: isActive ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  borderRadius: 1,
                  border: isActive ? `1px solid ${threshold.color}` : '1px solid transparent'
                }}
              >
                <Box display="flex" alignItems="center" gap={1}>
                  <Box
                    width={12}
                    height={12}
                    borderRadius="50%"
                    sx={{ backgroundColor: threshold.color }}
                  />
                  <Typography variant="body2" fontWeight={isActive ? 600 : 400}>
                    {threshold.label}
                  </Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {(threshold.min * 100).toFixed(1)}% - {threshold.max === 1.0 ? '∞' : (threshold.max * 100).toFixed(1)}%
                </Typography>
              </Box>
            )
          })}
        </Box>

        {/* Market Impact Indicator */}
        <Box mt={3} p={2} sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Market Impact
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {volLevel.level === 'low' && 'Tight liquidity ranges, minimal slippage expected'}
            {volLevel.level === 'medium' && 'Moderate liquidity distribution, normal trading conditions'}
            {volLevel.level === 'high' && 'Wide liquidity ranges deployed, increased fees active'}
            {volLevel.level === 'extreme' && 'Maximum protection mode, emergency ranges activated'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  )
}

export default VolatilityChart
