import React, { useEffect, useRef } from 'react'
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box,
  Chip
} from '@mui/material'
import { TrendingUp, TrendingDown, Timeline } from '@mui/icons-material'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const PriceChart = ({ priceHistory = [] }) => {
  const chartRef = useRef(null)

  // Cleanup chart on unmount
  useEffect(() => {
    return () => {
      if (chartRef.current) {
        chartRef.current.destroy()
      }
    }
  }, [])

  // Process price history data with simpler labels - memoized to prevent unnecessary recalculations
  const processedData = React.useMemo(() => {
    if (!priceHistory || priceHistory.length === 0) return []
    
    return priceHistory.slice(-30).map((point, index) => ({
      x: new Date(point.timestamp * 1000).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }),
      y: point.price
    }))
  }, [priceHistory])

  const currentPrice = processedData.length > 0 ? processedData[processedData.length - 1].y : 0
  const previousPrice = processedData.length > 1 ? processedData[processedData.length - 2].y : currentPrice
  const priceChange = currentPrice - previousPrice
  const priceChangePercent = previousPrice > 0 ? (priceChange / previousPrice * 100) : 0

  const data = {
    labels: processedData.map(d => d.x),
    datasets: [
      {
        label: 'Price',
        data: processedData.map(d => d.y),
        borderColor: priceChange >= 0 ? '#4caf50' : '#f44336',
        backgroundColor: priceChange >= 0 ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.1,
        pointRadius: 0,
        pointHoverRadius: 5
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      intersect: false,
      mode: 'index'
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(26, 26, 26, 0.9)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: '#333',
        borderWidth: 1,
        callbacks: {
          title: (context) => {
            return context[0].label
          },
          label: (context) => {
            return `Price: $${context.parsed.y.toFixed(4)}`
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
          callback: (value) => `$${value.toFixed(2)}`
        }
      }
    },
    elements: {
      point: {
        backgroundColor: '#00d4ff'
      }
    },
    animation: {
      duration: 200,
      easing: 'easeInOutQuart'
    }
  }

  return (
    <Card sx={{ height: 400 }}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <Timeline sx={{ color: 'primary.main' }} />
            <Typography variant="h6">Real-Time Price</Typography>
          </Box>
        }
        action={
          <Box display="flex" gap={1} alignItems="center">
            <Typography variant="h5" fontWeight={600}>
              ${currentPrice.toFixed(4)}
            </Typography>
            <Chip
              icon={priceChange >= 0 ? <TrendingUp /> : <TrendingDown />}
              label={`${priceChange >= 0 ? '+' : ''}${priceChangePercent.toFixed(2)}%`}
              color={priceChange >= 0 ? 'success' : 'error'}
              size="small"
              sx={{ minWidth: 80 }}
            />
          </Box>
        }
      />
      <CardContent sx={{ height: 320, pt: 0 }}>
        {processedData.length > 0 ? (
          <Line 
            ref={chartRef} 
            data={data} 
            options={options}
            key={`price-chart-${processedData.length}`}
          />
        ) : (
          <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            height="100%"
            color="text.secondary"
          >
            <Typography>Waiting for price data...</Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}

export default PriceChart
