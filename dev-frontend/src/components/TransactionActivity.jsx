import React from 'react'
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Avatar,
  LinearProgress
} from '@mui/material'
import {
  SwapHoriz,
  Add,
  Remove,
  Payment,
  AccessTime,
  AccountBalanceWallet
} from '@mui/icons-material'

const getTransactionIcon = (type) => {
  switch (type) {
    case 'swap':
      return <SwapHoriz />
    case 'add_liquidity':
      return <Add />
    case 'remove_liquidity':
      return <Remove />
    case 'payment':
      return <Payment />
    default:
      return <SwapHoriz />
  }
}

const getTransactionColor = (type) => {
  switch (type) {
    case 'swap':
      return 'primary'
    case 'add_liquidity':
      return 'success'
    case 'remove_liquidity':
      return 'warning'
    case 'payment':
      return 'info'
    default:
      return 'default'
  }
}

const formatTimeUntil = (seconds) => {
  if (seconds <= 0) return 'Executing...'
  if (seconds < 60) return `${Math.ceil(seconds)}s`
  if (seconds < 3600) return `${Math.ceil(seconds / 60)}m`
  return `${Math.ceil(seconds / 3600)}h`
}

const formatSize = (size) => {
  if (size >= 1000000) {
    return `${(size / 1000000).toFixed(1)}M`
  }
  if (size >= 1000) {
    return `${(size / 1000).toFixed(1)}K`
  }
  return size.toFixed(0)
}

const TransactionActivity = ({ transactions = [], pendingCount = 0 }) => {
  // Sort transactions by time until execution
  const sortedTransactions = [...transactions].sort((a, b) => 
    (a.time_until_execution || 0) - (b.time_until_execution || 0)
  )

  const recentTransactions = sortedTransactions.slice(0, 8) // Show latest 8

  return (
    <Card sx={{ height: 400 }}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <AccountBalanceWallet sx={{ color: 'primary.main' }} />
            <Typography variant="h6">Transaction Activity</Typography>
          </Box>
        }
        action={
          <Chip
            icon={<AccessTime />}
            label={`${pendingCount} Pending`}
            color={pendingCount > 10 ? 'warning' : 'default'}
            variant="outlined"
            size="small"
          />
        }
      />
      <CardContent sx={{ height: 320, pt: 0, overflow: 'hidden' }}>
        {recentTransactions.length > 0 ? (
          <List sx={{ height: '100%', overflowY: 'auto', pr: 1 }}>
            {recentTransactions.map((tx, index) => {
              const timeLeft = tx.time_until_execution || 0
              const isExecuting = timeLeft <= 0
              const progress = Math.max(0, Math.min(100, 100 - (timeLeft / 30) * 100))

              return (
                <ListItem
                  key={index}
                  sx={{
                    mb: 1,
                    backgroundColor: isExecuting 
                      ? 'rgba(76, 175, 80, 0.1)' 
                      : 'rgba(255, 255, 255, 0.03)',
                    borderRadius: 1,
                    border: isExecuting 
                      ? '1px solid rgba(76, 175, 80, 0.3)' 
                      : '1px solid rgba(255, 255, 255, 0.1)'
                  }}
                >
                  <ListItemIcon>
                    <Avatar
                      sx={{
                        width: 32,
                        height: 32,
                        backgroundColor: isExecuting ? 'success.main' : 'grey.700'
                      }}
                    >
                      {getTransactionIcon(tx.transaction_type)}
                    </Avatar>
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body2" fontWeight={600}>
                          {tx.transaction_type?.replace('_', ' ').toUpperCase() || 'SWAP'}
                        </Typography>
                        <Chip
                          label={formatSize(tx.size || 0)}
                          size="small"
                          color={getTransactionColor(tx.transaction_type)}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="caption" color="text.secondary" component="div">
                          {tx.wallet_address || 'Unknown wallet'}
                        </Typography>
                        <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                          <Typography variant="caption" color="text.secondary">
                            {formatTimeUntil(timeLeft)}
                          </Typography>
                          {!isExecuting && (
                            <LinearProgress
                              variant="determinate"
                              value={progress}
                              sx={{
                                flex: 1,
                                height: 3,
                                borderRadius: 2,
                                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: timeLeft < 5 ? '#ff9800' : '#2196f3'
                                }
                              }}
                            />
                          )}
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              )
            })}
          </List>
        ) : (
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            height="100%"
            color="text.secondary"
          >
            <AccountBalanceWallet sx={{ fontSize: 48, mb: 1, opacity: 0.5 }} />
            <Typography variant="body2">
              No pending transactions
            </Typography>
            <Typography variant="caption">
              Transactions will appear here when simulation is running
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default TransactionActivity
