import React, { useState } from 'react'
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box,
  Grid,
  Avatar,
  Chip,
  Tooltip,
  ButtonGroup,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material'
import {
  AccountBalanceWallet,
  TrendingUp,
  Person,
  Speed,
  FilterList
} from '@mui/icons-material'

const getWalletIcon = (pattern) => {
  switch (pattern) {
    case 'whale':
      return <TrendingUp />
    case 'retail':
      return <Person />
    case 'arbitrage_bot':
      return <Speed />
    default:
      return <AccountBalanceWallet />
  }
}

const getWalletColor = (pattern) => {
  switch (pattern) {
    case 'whale':
      return '#ff9800' // Orange for whales
    case 'retail':
      return '#4caf50' // Green for retail
    case 'arbitrage_bot':
      return '#2196f3' // Blue for bots
    default:
      return '#757575' // Grey for unknown
  }
}

const formatAddress = (address) => {
  if (!address) return 'Unknown'
  return `${address.slice(0, 6)}...${address.slice(-4)}`
}

const formatBalance = (balance) => {
  if (balance >= 1000000) {
    return `${(balance / 1000000).toFixed(1)}M`
  }
  if (balance >= 1000) {
    return `${(balance / 1000).toFixed(1)}K`
  }
  return balance.toFixed(0)
}

const WalletStatus = ({ wallets = [] }) => {
  const [filter, setFilter] = useState('all')

  // Filter wallets based on selected filter
  const filteredWallets = wallets.filter(wallet => {
    if (filter === 'all') return true
    return wallet.pattern === filter
  })

  // Calculate statistics
  const whaleCount = wallets.filter(w => w.pattern === 'whale').length
  const retailCount = wallets.filter(w => w.pattern === 'retail').length
  const botCount = wallets.filter(w => w.pattern === 'arbitrage_bot').length
  
  const totalBalance = wallets.reduce((sum, wallet) => sum + (wallet.balance_algo || 0), 0)
  const avgBalance = wallets.length > 0 ? totalBalance / wallets.length : 0

  const filters = [
    { value: 'all', label: 'All', count: wallets.length },
    { value: 'whale', label: 'Whales', count: whaleCount },
    { value: 'retail', label: 'Retail', count: retailCount },
    { value: 'arbitrage_bot', label: 'Bots', count: botCount }
  ]

  return (
    <Card>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <AccountBalanceWallet sx={{ color: 'primary.main' }} />
            <Typography variant="h6">Wallet Status</Typography>
          </Box>
        }
        action={
          <Box display="flex" gap={1} alignItems="center">
            <Typography variant="body2" color="text.secondary">
              Total Balance: {formatBalance(totalBalance)} ALGO
            </Typography>
            <Chip
              label={`${wallets.length} Active`}
              color="primary"
              variant="outlined"
              size="small"
            />
          </Box>
        }
      />
      <CardContent>
        {/* Filter Buttons */}
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <FilterList sx={{ color: 'text.secondary' }} />
          <ButtonGroup size="small" variant="outlined">
            {filters.map((filterOption) => (
              <Button
                key={filterOption.value}
                onClick={() => setFilter(filterOption.value)}
                variant={filter === filterOption.value ? 'contained' : 'outlined'}
                sx={{ textTransform: 'none' }}
              >
                {filterOption.label} ({filterOption.count})
              </Button>
            ))}
          </ButtonGroup>
        </Box>

        {/* Summary Stats */}
        <Grid container spacing={2} mb={3}>
          <Grid item xs={3}>
            <Box textAlign="center" p={2} sx={{ backgroundColor: 'rgba(255, 152, 0, 0.1)', borderRadius: 1 }}>
              <Typography variant="h4" fontWeight={600} sx={{ color: '#ff9800' }}>
                {whaleCount}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Whales
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box textAlign="center" p={2} sx={{ backgroundColor: 'rgba(76, 175, 80, 0.1)', borderRadius: 1 }}>
              <Typography variant="h4" fontWeight={600} sx={{ color: '#4caf50' }}>
                {retailCount}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Retail
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box textAlign="center" p={2} sx={{ backgroundColor: 'rgba(33, 150, 243, 0.1)', borderRadius: 1 }}>
              <Typography variant="h4" fontWeight={600} sx={{ color: '#2196f3' }}>
                {botCount}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Bots
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={3}>
            <Box textAlign="center" p={2} sx={{ backgroundColor: 'rgba(156, 39, 176, 0.1)', borderRadius: 1 }}>
              <Typography variant="h4" fontWeight={600} sx={{ color: '#9c27b0' }}>
                {formatBalance(avgBalance)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Avg Balance
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Wallets Table */}
        {filteredWallets.length > 0 ? (
          <TableContainer component={Paper} sx={{ maxHeight: 400, backgroundColor: 'transparent' }}>
            <Table size="small" stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Wallet</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Balance</TableCell>
                  <TableCell align="right">Trade Freq</TableCell>
                  <TableCell align="right">Avg Size</TableCell>
                  <TableCell align="right">Vol Sensitivity</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredWallets.slice(0, 20).map((wallet, index) => ( // Show max 20 wallets
                  <TableRow key={wallet.address || index} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Avatar
                          sx={{
                            width: 24,
                            height: 24,
                            backgroundColor: getWalletColor(wallet.pattern)
                          }}
                        >
                          {getWalletIcon(wallet.pattern)}
                        </Avatar>
                        <Tooltip title={wallet.address || 'Unknown address'}>
                          <Typography variant="body2" fontFamily="monospace">
                            {formatAddress(wallet.address)}
                          </Typography>
                        </Tooltip>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={wallet.pattern || 'unknown'}
                        size="small"
                        sx={{
                          backgroundColor: getWalletColor(wallet.pattern),
                          color: 'white',
                          textTransform: 'capitalize'
                        }}
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight={600}>
                        {formatBalance(wallet.balance_algo || 0)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {(wallet.trade_frequency || 0).toFixed(1)}/min
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {formatBalance(wallet.avg_trade_size || 0)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2">
                        {(wallet.volatility_sensitivity || 0).toFixed(2)}x
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            py={4}
            color="text.secondary"
          >
            <AccountBalanceWallet sx={{ fontSize: 48, mb: 1, opacity: 0.5 }} />
            <Typography variant="body2">
              No wallets available
            </Typography>
            <Typography variant="caption">
              Wallets will appear when blockchain simulation is running
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default WalletStatus
