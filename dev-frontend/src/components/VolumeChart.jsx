import React from 'react'
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box
} from '@mui/material'
import { BarChart } from '@mui/icons-material'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const VolumeChart = ({ priceHistory = [] }) => {
  // Process volume data from price history - memoized for performance
  const volumeData = React.useMemo(() => {
    if (!priceHistory || priceHistory.length === 0) return []
    
    return priceHistory.slice(-15).map((point, index) => ({
      x: new Date(point.timestamp * 1000).toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }),
      y: point.volume,
      price: point.price
    }))
  }, [priceHistory])

  // Calculate volume statistics
  const volumes = volumeData.map(d => d.y)
  const totalVolume = volumes.reduce((sum, vol) => sum + vol, 0)
  const avgVolume = volumes.length > 0 ? totalVolume / volumes.length : 0
  const maxVolume = Math.max(...volumes, 0)

  const data = {
    labels: volumeData.map(d => d.x),
    datasets: [
      {
        label: 'Trading Volume',
        data: volumeData.map(d => d.y),
        backgroundColor: volumeData.map(d => {
          const intensity = d.y / maxVolume
          if (intensity > 0.8) return 'rgba(244, 67, 54, 0.8)' // High volume - red
          if (intensity > 0.6) return 'rgba(255, 152, 0, 0.8)' // Medium-high - orange  
          if (intensity > 0.4) return 'rgba(255, 193, 7, 0.8)' // Medium - yellow
          return 'rgba(76, 175, 80, 0.8)' // Low volume - green
        }),
        borderColor: volumeData.map(d => {
          const intensity = d.y / maxVolume
          if (intensity > 0.8) return '#f44336'
          if (intensity > 0.6) return '#ff9800'
          if (intensity > 0.4) return '#ffc107'
          return '#4caf50'
        }),
        borderWidth: 1,
        borderRadius: 2,
        borderSkipped: false
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(26, 26, 26, 0.9)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#333',
        borderWidth: 1,
        callbacks: {
          title: (context) => {
            return `Time: ${context[0].label}`
          },
          label: (context) => {
            const volume = context.parsed.y
            return `Volume: ${volume.toLocaleString()}`
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: '#333',
          drawBorder: false
        },
        ticks: {
          color: '#999',
          maxTicksLimit: 6,
          maxRotation: 45
        }
      },
      y: {
        display: true,
        grid: {
          color: '#333',
          drawBorder: false
        },
        ticks: {
          color: '#999',
          callback: (value) => {
            if (value >= 1000000) {
              return (value / 1000000).toFixed(1) + 'M'
            }
            if (value >= 1000) {
              return (value / 1000).toFixed(1) + 'K'
            }
            return value.toLocaleString()
          }
        }
      }
    },
    animation: {
      duration: 300,
      easing: 'easeInOutQuart'
    }
  }

  const formatVolume = (volume) => {
    if (volume >= 1000000) {
      return (volume / 1000000).toFixed(2) + 'M'
    }
    if (volume >= 1000) {
      return (volume / 1000).toFixed(1) + 'K'
    }
    return volume.toLocaleString()
  }

  return (
    <Card sx={{ height: 400 }}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <BarChart sx={{ color: 'primary.main' }} />
            <Typography variant="h6">Trading Volume</Typography>
          </Box>
        }
        action={
          <Box textAlign="right">
            <Typography variant="body2" color="text.secondary">
              Avg: {formatVolume(avgVolume)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total: {formatVolume(totalVolume)}
            </Typography>
          </Box>
        }
      />
      <CardContent sx={{ height: 320, pt: 0 }}>
        {volumeData.length > 0 ? (
          <Bar data={data} options={options} />
        ) : (
          <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            height="100%"
            color="text.secondary"
          >
            <Typography>Waiting for volume data...</Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default VolumeChart
