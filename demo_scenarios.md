# Seltra AMM - Demo Scenarios

## 🎯 **Demo Overview**

This document outlines compelling demo scenarios that showcase Seltra AMM's dynamic liquidity management capabilities. Each scenario demonstrates how the system adapts to different market conditions in real-time.

## 🎬 **Scenario 1: Calm Market - Tight Concentration**

### **Setup**

- **Initial State**: Stable market with low volatility
- **Price**: 1.0 ALGO/HACK
- **Volatility**: 1.5% (Low regime)
- **Liquidity**: Concentrated in tight ranges around current price

### **Demo Flow**

1. **Show Initial State**

   - Display tight liquidity concentration (3 ranges within ±5% of current price)
   - Highlight high capital efficiency
   - Show low slippage for small trades

2. **Execute Small Trades**

   - Perform 1-5 ALGO swaps
   - Show minimal slippage (<0.1%)
   - Demonstrate efficient price discovery

3. **Key Message**
   - "In calm markets, Seltra concentrates liquidity for maximum efficiency"

### **Expected Results**

- **Efficiency Score**: 85-95%
- **Slippage**: <0.1% for trades <1% of pool
- **Range Distribution**: 95% of liquidity within ±5% of current price

---

## 🌊 **Scenario 2: Volatility Spike - Dynamic Expansion**

### **Setup**

- **Trigger**: Market volatility increases to 8% (High regime)
- **Price Movement**: ±15% price swings
- **Liquidity**: Automatically expands to wider ranges

### **Demo Flow**

1. **Trigger Volatility Spike**

   - Add price shock: +10% then -8%
   - Watch volatility meter turn red
   - Show regime change from "LOW" to "HIGH"

2. **Automatic Rebalancing**

   - System detects volatility increase
   - Triggers automatic rebalancing
   - Expands liquidity ranges to ±20% of current price

3. **Show Adaptation**

   - Display new range distribution
   - Highlight improved protection against large price moves
   - Show maintained liquidity for normal trades

4. **Key Message**
   - "When volatility spikes, Seltra automatically expands ranges to protect against large moves"

### **Expected Results**

- **Efficiency Score**: 60-75% (lower but safer)
- **Range Distribution**: 80% of liquidity within ±20% of current price
- **Protection**: Reduced impermanent loss for LPs

---

## 🚀 **Scenario 3: Trending Market - Asymmetric Ranges**

### **Setup**

- **Market Condition**: Strong uptrend (+25% over 5 minutes)
- **Volatility**: Medium (4%)
- **Liquidity**: Asymmetric distribution favoring trend direction

### **Demo Flow**

1. **Start Trending Scenario**

   - Set market to "trending" mode
   - Watch price climb steadily
   - Show increasing volume

2. **Show Asymmetric Adaptation**

   - Display ranges shifted upward
   - More liquidity above current price
   - Reduced liquidity below (trend protection)

3. **Execute Trades in Trend**

   - Show better execution for trend-following trades
   - Demonstrate reduced slippage for buys
   - Highlight protection against counter-trend moves

4. **Key Message**
   - "In trending markets, Seltra adapts ranges to favor the trend direction"

### **Expected Results**

- **Asymmetric Distribution**: 60% liquidity above current price
- **Trend Efficiency**: 15% better execution for trend trades
- **Protection**: Reduced exposure to counter-trend moves

---

## 💥 **Scenario 4: Flash Crash - Emergency Response**

### **Setup**

- **Trigger**: Sudden -30% price drop
- **Duration**: 30 seconds
- **Recovery**: Gradual return to normal

### **Demo Flow**

1. **Trigger Flash Crash**

   - Add massive negative price shock
   - Watch all indicators turn red
   - Show panic selling simulation

2. **Emergency Response**

   - System detects extreme volatility
   - Triggers emergency rebalancing
   - Expands ranges to maximum width

3. **Recovery Phase**

   - Price gradually recovers
   - System slowly tightens ranges
   - Returns to normal operation

4. **Key Message**
   - "During extreme events, Seltra provides maximum protection and liquidity"

### **Expected Results**

- **Emergency Ranges**: ±50% of current price
- **Liquidity Protection**: Maintained throughout crash
- **Recovery Time**: 2-3 minutes to normal operation

---

## 🐋 **Scenario 5: Whale Activity - Large Trade Optimization**

### **Setup**

- **Large Trade**: 100 ALGO swap (10% of pool)
- **Market**: Normal volatility (3%)
- **Optimization**: Smart routing across ranges

### **Demo Flow**

1. **Prepare Large Trade**

   - Set up 100 ALGO swap
   - Show current range distribution
   - Calculate expected slippage

2. **Execute Smart Routing**

   - System routes trade across multiple ranges
   - Show optimal execution path
   - Display reduced slippage vs. single-range execution

3. **Compare with Static AMM**

   - Show what slippage would be in static AMM
   - Highlight 40-60% slippage reduction
   - Demonstrate capital efficiency

4. **Key Message**
   - "Seltra's dynamic ranges provide better execution for large trades"

### **Expected Results**

- **Slippage Reduction**: 40-60% vs. static AMM
- **Execution**: Optimal routing across 2-3 ranges
- **Efficiency**: Maintained despite large trade size

---

## 📊 **Scenario 6: Performance Comparison**

### **Setup**

- **Side-by-Side**: Seltra vs. Static AMM
- **Same Market Conditions**: Identical price movements
- **Metrics**: APY, slippage, impermanent loss

### **Demo Flow**

1. **Setup Comparison**

   - Show two identical pools
   - Same initial liquidity
   - Same market conditions

2. **Run Identical Scenarios**

   - Execute same trades on both pools
   - Show real-time performance metrics
   - Highlight differences

3. **Results Summary**

   - **APY**: Seltra 15-25% higher
   - **Slippage**: 30-50% lower
   - **Impermanent Loss**: 20-40% reduction

4. **Key Message**
   - "Seltra consistently outperforms static AMMs across all metrics"

---

## 🎮 **Interactive Demo Controls**

### **Real-Time Controls**

- **Volatility Slider**: Adjust market volatility (1-15%)
- **Price Shock Button**: Add ±5%, ±10%, ±20% price shocks
- **Regime Selector**: Switch between Low/Medium/High volatility
- **Trade Size**: Execute trades from 0.1 to 100 ALGO

### **Visualization Elements**

- **Liquidity Range Bars**: Show current range distribution
- **Price Chart**: Real-time price with range overlays
- **Efficiency Meter**: Live efficiency score (0-100%)
- **Volatility Indicator**: Color-coded regime display
- **Transaction Feed**: Live transaction history

### **Performance Metrics**

- **Live APY**: Real-time yield calculation
- **Slippage Tracker**: Average slippage by trade size
- **Range Utilization**: Percentage of liquidity in active ranges
- **Rebalancing Frequency**: How often ranges adjust

---

## 🎯 **Demo Script - 5 Minute Presentation**

### **Opening (30 seconds)**

"Welcome to Seltra AMM - the first AMM that adapts to market conditions in real-time. Unlike static AMMs, Seltra automatically adjusts liquidity concentration based on volatility."

### **Scenario 1 - Calm Market (60 seconds)**

"Let's start with a calm market. Notice how liquidity is tightly concentrated around the current price for maximum efficiency. Small trades execute with minimal slippage."

### **Scenario 2 - Volatility Spike (90 seconds)**

"Now watch what happens when volatility spikes. The system automatically detects the change and expands liquidity ranges to protect against large moves. This happens in real-time without any manual intervention."

### **Scenario 3 - Large Trade (60 seconds)**

"Here's a 100 ALGO trade. Seltra routes it optimally across multiple ranges, reducing slippage by 50% compared to a static AMM."

### **Scenario 4 - Performance Comparison (60 seconds)**

"Side-by-side comparison shows Seltra consistently outperforms static AMMs with 20% higher APY and 40% lower slippage."

### **Closing (30 seconds)**

"Seltra represents the future of AMMs - intelligent, adaptive, and efficient. Thank you for watching our demo."

---

## 🔧 **Technical Implementation Notes**

### **Demo Data Sources**

- **Real Contract State**: Live data from deployed contracts
- **Simulated Market**: Realistic price movements and volatility
- **Backend Calculations**: Actual EWMA and decision tree logic

### **Performance Targets**

- **Response Time**: <2 seconds for rebalancing
- **Accuracy**: 95%+ correlation with real market conditions
- **Reliability**: 99.9% uptime during demo

### **Fallback Plans**

- **Contract Issues**: Use simulated contract responses
- **Network Problems**: Pre-recorded demo scenarios
- **UI Issues**: Command-line demo interface

---

This comprehensive demo showcases Seltra AMM's core innovation: **dynamic liquidity management that adapts to market conditions in real-time**, providing better capital efficiency, lower slippage, and improved protection for liquidity providers.
