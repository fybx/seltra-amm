# Seltra AMM - Complete Understanding Guide

## Executive Summary

Seltra AMM is a "smart" Automated Market Maker that adapts to market conditions in real-time. Unlike traditional AMMs (like Uniswap V2) that use static liquidity distribution, Seltra implements concentrated liquidity that dynamically adjusts based on volatility, creating better capital efficiency and trading experiences.

---

## Core Concept: From Traditional to Concentrated Liquidity

### Traditional AMM (The "Seesaw" Model)
```
ETH/USDC Pool: 100 ETH ↔ 200,000 USDC
Price: $2,000 per ETH
```

**How it works:**
- Single liquidity pool with fixed ratio
- Liquidity spread from $0 to infinity
- Simple but capital inefficient
- Most liquidity sits unused at extreme prices

### Concentrated Liquidity (Seltra's Innovation)
Instead of one big seesaw, imagine **multiple smaller seesaws at different price ranges**:

```
Range 1: $1,800-$2,200 → 30 ETH ↔ 60,000 USDC
Range 2: $1,900-$2,100 → 50 ETH ↔ 100,000 USDC  
Range 3: $1,950-$2,050 → 20 ETH ↔ 40,000 USDC
```

**Key insight:** Focus liquidity where trading actually happens!

---

## Understanding "Dynamic Liquidity Concentration"

### What "Moving Liquidity" Actually Means

**Scenario**: ETH price moves from $2,000 to $2,100

**Before (static):**
- Range 3 ($1,950-$2,050) becomes mostly USDC (people bought ETH)
- Other ranges have unbalanced liquidity

**After rebalancing:**
- System creates new range: $2,050-$2,150 with fresh liquidity
- Removes liquidity from unused ranges
- **Result**: More liquidity available where current trading happens

### How Multiple Ranges Work in Practice

**Critical Understanding:** Trading happens at a **single price point**, but multiple ranges can be "active" at that same price.

```python
class LiquidityPosition:
    price_lower: float      # $1,950
    price_upper: float      # $2,050  
    liquidity_amount: float # Trading capacity (NOT just token amounts)
    x_tokens: float         # Current X tokens (changes as price moves)
    y_tokens: float         # Current Y tokens (changes as price moves)

# When someone trades at $2,000:
# 1. Find all positions active at $2,000
# 2. Aggregate their liquidity capacity
# 3. Execute trade against combined liquidity
# 4. Update each position proportionally
```

### The Liquidity Amount Mystery - SOLVED

**Question:** What is `liquidity_amount` mathematically?

**Answer:** It's **trading capacity** - how much volume this position can handle before price moves significantly. NOT just the sum of tokens.

**Key Relationships:**
- `x_tokens/y_tokens` = current price (NOT range center)
- `liquidity_amount` = constant until LP adds/removes liquidity  
- As price moves, token balances change but liquidity_amount stays fixed

**Example:**
```python
# At price $2000
position = LiquidityPosition(1900, 2100, liquidity=100, x=25, y=50000)
# x/y ratio: 50000/25 = 2000 = CURRENT PRICE

# Price moves to $2100 (top of range)
# Same position becomes:
position = LiquidityPosition(1900, 2100, liquidity=100, x=0, y=55000)
# All X tokens sold, more Y collected, but liquidity capacity unchanged
```

---

## Dynamic Concentration Algorithm

### Core Algorithm Implementation

```python
class DynamicLiquidityEngine:
    def __init__(self):
        self.volatility_window = 10  # Last 10 trades
        self.base_concentration = 0.05  # ±5% default range
        self.volatility_threshold_low = 0.02  # 2% = calm market
        self.volatility_threshold_high = 0.08  # 8% = crazy market
        
    def calculate_optimal_ranges(self, current_price: float) -> List[Tuple]:
        """Core algorithm: determine where liquidity should be positioned"""
        
        # Step 1: Calculate recent volatility
        recent_volatility = self.get_recent_volatility()
        
        # Step 2: Determine concentration level
        if recent_volatility < self.volatility_threshold_low:
            # Calm market - concentrate tightly
            concentration_factor = 0.5  # Tighter ranges
            num_ranges = 3
        elif recent_volatility > self.volatility_threshold_high:
            # Volatile market - spread wide
            concentration_factor = 2.0  # Wider ranges
            num_ranges = 5
        else:
            # Normal market
            concentration_factor = 1.0
            num_ranges = 4
            
        # Step 3: Generate optimal ranges around current price
        base_range = self.base_concentration * concentration_factor
        
        ranges = []
        for i in range(num_ranges):
            # Create overlapping ranges centered around current price
            offset = (i - num_ranges//2) * base_range * 0.5
            lower = current_price * (1 + offset - base_range/2)
            upper = current_price * (1 + offset + base_range/2)
            ranges.append((lower, upper))
            
        return ranges
    
    def should_rebalance(self) -> bool:
        """Decide if we need to rebalance based on conditions"""
        return (
            self.volatility_changed_significantly() or
            self.price_moved_outside_active_ranges() or
            self.time_since_last_rebalance() > MAX_REBALANCE_INTERVAL
        )
```

### Volatility Oracle Function

**What it does:** Measures market conditions to inform concentration decisions

```python
def calculate_recent_volatility(self) -> float:
    """Simple volatility calculation for hackathon"""
    recent_prices = self.get_last_n_prices(self.volatility_window)
    if len(recent_prices) < 2:
        return 0.0
    
    # Calculate standard deviation of price changes
    price_changes = []
    for i in range(1, len(recent_prices)):
        change = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
        price_changes.append(change)
    
    return statistics.stdev(price_changes) if price_changes else 0.0
```

---

## Smart Contract Architecture for Algorand

### Contract Interaction Flow

```
┌─────────┐    ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  User   │    │  Frontend   │    │ SeltraPool   │    │ Rebalancer  │
└─────────┘    └─────────────┘    └──────────────┘    └─────────────┘
     │               │                    │                   │
     │ 1. Swap 10 ETH │                   │                   │
     ├──────────────→│                    │                   │
     │               │ 2. Check current   │                   │
     │               │    liquidity       │                   │
     │               ├───────────────────→│                   │
     │               │ 3. Execute swap    │                   │
     │               ├───────────────────→│                   │
     │               │                    │ 4. Update price   │
     │               │                    ├──────────────────→│
     │               │                    │ 5. Check volatility│
     │               │                    │ & trigger rebalance│
     │               │                    │←──────────────────┤
     │               │                    │ 6. Atomic rebalance│
     │               │                    │   transaction      │
     │               │                    │←──────────────────┤
     │ 7. Transaction │                   │                   │
     │    confirmed   │←───────────────────┤                   │
     │←──────────────┤                    │                   │
```

### Core Contract Implementation

```python
# Main Pool Contract
class SeltraPoolContract:
    @external
    def swap(self, asset_in: Asset, amount_in: int) -> int:
        # 1. Calculate output using active liquidity
        active_liquidity = self.get_active_liquidity_at_current_price()
        amount_out = self.calculate_swap_output(amount_in, active_liquidity)
        
        # 2. Execute swap across active positions
        self.execute_swap_across_positions(amount_in, amount_out)
        
        # 3. Update price and trigger rebalance check
        self.update_current_price()
        self.maybe_trigger_rebalance()  # Async call to rebalancer
        
        return amount_out
    
    @external  
    def rebalance(self, new_ranges: List[Tuple]) -> None:
        """Called by rebalancer contract"""
        # Use atomic transaction group for safety
        with atomic_transaction_group():
            self.collect_all_liquidity()
            self.redistribute_to_new_ranges(new_ranges)
            self.update_position_tracking()

# Rebalancer Contract (separate for modularity)
class RebalancerContract:
    @external
    def check_and_rebalance(self, pool_address: str) -> None:
        volatility = self.calculate_volatility(pool_address)
        
        if self.should_rebalance(volatility):
            new_ranges = self.calculate_optimal_ranges(volatility)
            # Call pool's rebalance function
            self.call_pool_rebalance(pool_address, new_ranges)
```

---

## Hackathon Implementation Strategy

### 1-Day Implementation Plan

**Morning (4 hours): Core Contracts**
1. **Basic pool with 3 static ranges** (2 hours)
2. **Simple volatility calculation** (1 hour)  
3. **Rebalancing trigger logic** (1 hour)

**Afternoon (4 hours): Demo Polish**
1. **Minimal frontend showing ranges** (2 hours)
2. **Volatility simulator for testing** (1 hour)
3. **Demo scenario preparation** (1 hour)

### Simplified Implementation for Demo

```python
class SimpleSeltraPool:
    def __init__(self):
        self.current_price = 2000.0
        self.positions = [
            # Start with 3 simple ranges
            {"range": (1900, 2100), "x": 50, "y": 100000},  # Wide
            {"range": (1950, 2050), "x": 25, "y": 50000},   # Medium  
            {"range": (1980, 2020), "x": 10, "y": 20000},   # Tight
        ]
    
    def get_active_liquidity(self):
        active_positions = [
            pos for pos in self.positions
            if pos["range"][0] <= self.current_price <= pos["range"][1]
        ]
        return sum(pos["x"] for pos in active_positions)
    
    def rebalance_on_volatility_change(self, new_volatility):
        # This is where the magic happens - adjust ranges based on volatility
        if new_volatility > 0.05:  # High volatility
            self.widen_ranges()
        else:  # Low volatility  
            self.narrow_ranges()
```

### Key Demo Moments

```python
# Demo Script
def demo_scenario():
    # 1. Show normal trading with tight ranges
    pool.simulate_calm_market()
    show_liquidity_visualization()  # Tight concentration
    
    # 2. Trigger volatility event
    pool.simulate_volatile_trades()
    show_rebalancing_in_real_time()  # Watch ranges widen
    
    # 3. Show improved execution vs static pool
    compare_slippage_side_by_side()
```

---

## Key Formulas for Implementation

### Volatility Adjustment
```
concentration = base_concentration * (1 + ln(current_vol/baseline_vol) * sensitivity)
```

### Dynamic Fee Structure  
```
fee = base_fee * (1 + volatility_multiplier)
```

### Optimal Range Calculation
```
range = current_price ± (volatility * time_factor)
```

### Simplified Liquidity Amount (for hackathon)
```python
def simplified_liquidity_amount(x, y, range_width):
    return sqrt(x * y) / range_width  # Tighter range = higher effective liquidity
```

---

## Critical Questions Answered

### Q: How do multiple seesaws work if trading price is single point?
**A:** Multiple ranges can be "active" at the same price. They aggregate their liquidity capacity, creating deeper liquidity at that price point.

### Q: What is liquidity_amount mathematically?
**A:** It's trading capacity, not token amounts. Represents how much volume this position can handle before significant price impact.

### Q: How does "moving liquidity" actually work?
**A:** System redistributes capital across different price ranges based on where trading activity occurs and volatility conditions.

### Q: How to implement for hackathon with time constraints?
**A:** Start with 3 static ranges, add simple volatility detection, and focus on visual demonstration of rebalancing.

---

## Success Metrics for Hackathon Demo

**Technical Achievement:**
- [ ] Basic concentrated liquidity working (3 ranges)
- [ ] Volatility calculation and range adjustment
- [ ] Visual demonstration of liquidity rebalancing

**Demo Impact:**
- [ ] Show liquidity concentration during calm markets
- [ ] Demonstrate range widening during volatility
- [ ] Compare execution vs traditional AMM
- [ ] Real-time visualization of liquidity movement

**Judge Appeal:**
- [ ] Clear explanation of innovation
- [ ] Working prototype demonstrating core concept
- [ ] Visual proof of superior capital efficiency
- [ ] Technical depth without overwhelming complexity

---

*This guide represents the complete understanding developed through our discussion, ready for hackathon implementation.*
