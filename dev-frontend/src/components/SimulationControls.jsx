import React, { useState } from 'react'
import {
  Card,
  CardHeader,
  CardContent,
  Grid,
  Button,
  ButtonGroup,
  TextField,
  Typography,
  Box,
  Chip,
  Divider,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material'
import {
  PlayArrow,
  TrendingUp,
  TrendingDown,
  Speed,
  Warning,
  FlashOn,
  Timeline
} from '@mui/icons-material'

const SCENARIOS = [
  { id: 'calm_market', name: 'Calm Trading', icon: <Timeline />, color: 'success', description: 'Low volatility, tight ranges' },
  { id: 'volatile_spike', name: 'Volatility Spike', icon: <TrendingUp />, color: 'warning', description: 'High volatility, range expansion' },
  { id: 'flash_crash', name: 'Flash Crash', icon: <TrendingDown />, color: 'error', description: 'Extreme market stress test' },
  { id: 'whale_activity', name: 'Whale Activity', icon: <Speed />, color: 'info', description: 'Large transaction handling' }
]

const VOLATILITY_REGIMES = [
  { value: 'low', label: 'Low (<1%)', color: 'success' },
  { value: 'medium', label: 'Medium (~2%)', color: 'warning' },
  { value: 'high', label: 'High (>5%)', color: 'error' }
]

const TRADING_PATTERNS = [
  { value: 'normal', label: 'Normal', description: '0.5 tx/min/wallet, 5% whales' },
  { value: 'volatile', label: 'Volatile', description: '2.0 tx/min/wallet, 15% whales' }
]

const SimulationControls = ({
  onTriggerScenario,
  onSetVolatilityRegime,
  onSetTradingPattern,
  onAddPriceShock,
  currentScenario = 'normal',
  currentRegime = 'medium'
}) => {
  const [shockMagnitude, setShockMagnitude] = useState(0)
  const [shockDuration, setShockDuration] = useState(60)
  const [tradingPattern, setTradingPattern] = useState('normal')

  const handleScenarioTrigger = (scenarioId) => {
    onTriggerScenario(scenarioId)
  }

  const handleVolatilityChange = (regime) => {
    onSetVolatilityRegime(regime)
  }

  const handleTradingPatternChange = (event) => {
    const pattern = event.target.value
    setTradingPattern(pattern)
    onSetTradingPattern(pattern)
  }

  const handlePriceShock = () => {
    onAddPriceShock(shockMagnitude / 100, shockDuration) // Convert to decimal
  }

  return (
    <Card>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <PlayArrow sx={{ color: 'primary.main' }} />
            <Typography variant="h6">Simulation Controls</Typography>
          </Box>
        }
        subheader="Control market scenarios and blockchain patterns"
      />
      <CardContent>
        <Grid container spacing={3}>
          {/* Demo Scenarios */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FlashOn />
              Demo Scenarios
            </Typography>
            <Grid container spacing={2}>
              {SCENARIOS.map((scenario) => (
                <Grid item xs={6} sm={3} key={scenario.id}>
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={scenario.icon}
                    onClick={() => handleScenarioTrigger(scenario.id)}
                    color={scenario.color}
                    sx={{
                      height: 80,
                      flexDirection: 'column',
                      gap: 0.5,
                      textTransform: 'none'
                    }}
                  >
                    <Typography variant="caption" fontWeight={600}>
                      {scenario.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" fontSize="0.7rem">
                      {scenario.description}
                    </Typography>
                  </Button>
                </Grid>
              ))}
            </Grid>
          </Grid>

          <Divider sx={{ width: '100%', my: 1 }} />

          {/* Current Status */}
          <Grid item xs={12}>
            <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
              <Typography variant="subtitle2">Current:</Typography>
              <Chip
                label={`Scenario: ${currentScenario}`}
                color="primary"
                variant="outlined"
                size="small"
              />
              <Chip
                label={`Regime: ${currentRegime}`}
                color={
                  currentRegime === 'low' ? 'success' :
                  currentRegime === 'medium' ? 'warning' : 'error'
                }
                variant="outlined"
                size="small"
              />
            </Box>
          </Grid>

          <Divider sx={{ width: '100%', my: 1 }} />

          {/* Manual Controls */}
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" gutterBottom>
              Volatility Regime
            </Typography>
            <ButtonGroup variant="outlined" fullWidth size="small">
              {VOLATILITY_REGIMES.map((regime) => (
                <Button
                  key={regime.value}
                  color={regime.color}
                  onClick={() => handleVolatilityChange(regime.value)}
                  variant={currentRegime === regime.value ? 'contained' : 'outlined'}
                >
                  {regime.label}
                </Button>
              ))}
            </ButtonGroup>
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Trading Pattern</InputLabel>
              <Select
                value={tradingPattern}
                onChange={handleTradingPatternChange}
                label="Trading Pattern"
              >
                {TRADING_PATTERNS.map((pattern) => (
                  <MenuItem key={pattern.value} value={pattern.value}>
                    <Box>
                      <Typography variant="body2">{pattern.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {pattern.description}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" gutterBottom>
              Price Shock
            </Typography>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Magnitude: {shockMagnitude}%
              </Typography>
              <Slider
                size="small"
                value={shockMagnitude}
                onChange={(_, value) => setShockMagnitude(value)}
                min={-20}
                max={20}
                step={1}
                marks={[
                  { value: -20, label: '-20%' },
                  { value: 0, label: '0%' },
                  { value: 20, label: '+20%' }
                ]}
              />
              <Box display="flex" gap={1} alignItems="center" mt={1}>
                <TextField
                  size="small"
                  label="Duration (s)"
                  type="number"
                  value={shockDuration}
                  onChange={(e) => setShockDuration(Number(e.target.value))}
                  inputProps={{ min: 10, max: 300 }}
                  sx={{ width: 100 }}
                />
                <Button
                  variant="contained"
                  color="warning"
                  onClick={handlePriceShock}
                  disabled={shockMagnitude === 0}
                  startIcon={<Warning />}
                >
                  Trigger
                </Button>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  )
}

export default SimulationControls
