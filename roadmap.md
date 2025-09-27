# Seltra AMM - Hackathon Roadmap

**Total Time: 12 hours | Team: 2 developers | Approach: LLM-assisted development**

## Project Overview

Build a working demo of Seltra AMM with:

- Single pool AMM with dynamic liquidity concentration
- Market simulation environment
- Real-time visualization of liquidity rebalancing
- Deployed to Algorand testnet

---

## MILESTONE 1: Environment Setup & Basic Infrastructure (2 hours)

**Target: Foundation for development**

### 1.1 Development Environment (30 min)

**LLM Prompt Template:**

```
"Set up Algorand development environment for Python smart contracts. Include:
- Algorand Python SDK installation
- Local node setup or testnet connection
- Basic project structure with contracts/ and simulation/ directories
- Requirements.txt with all dependencies"
```

**Deliverables:**

- [ ] Algorand Python SDK installed
- [ ] Testnet connection established
- [ ] Project structure created
- [ ] Basic wallet setup for testing

### 1.2 Market Simulation Framework (90 min)

**LLM Prompt Template:**

```
"Create a market simulation framework that:
- Simulates realistic price movements using random walks
- Supports different volatility regimes (calm, normal, volatile)
- Provides historical price data for volatility calculations
- Includes volume simulation for realistic trading patterns
- Has configurable market scenarios (bull market, bear market, sideways)"
```

**Technical Requirements:**

```python
class MarketSimulator:
    def __init__(self, initial_price: float, volatility: float)
    def get_current_price(self) -> float
    def get_price_history(self, window: int) -> List[float]
    def simulate_trade(self, size: float) -> TradeResult
    def set_volatility_regime(self, regime: str)  # "calm", "normal", "volatile"
```

**Deliverables:**

- [ ] MarketSimulator class with basic price generation
- [ ] Volatility regime switching functionality
- [ ] Historical data storage and retrieval
- [ ] Trade simulation with realistic slippage

---

## MILESTONE 2: Core AMM Contract (3 hours)

**Target: Basic concentrated liquidity AMM**

### 2.1 Basic Pool Contract (90 min)

**LLM Prompt Template:**

```
"Create an Algorand smart contract for a concentrated liquidity AMM that:
- Supports multiple liquidity ranges at different price points
- Implements add_liquidity, remove_liquidity, and swap functions
- Uses Algorand Python syntax with proper decorators
- Handles ASA (Algorand Standard Asset) transactions
- Includes basic slippage protection"
```

**Technical Requirements:**

```python
class SeltraPoolContract:
    @external
    def add_liquidity(self, asset_x: Asset, asset_y: Asset, amount_x: int, amount_y: int, price_lower: int, price_upper: int) -> int

    @external
    def remove_liquidity(self, lp_token_id: int) -> Tuple[int, int]

    @external
    def swap(self, asset_in: Asset, amount_in: int, min_amount_out: int) -> int
```

**Deliverables:**

- [ ] Basic pool contract with 3 static liquidity ranges
- [ ] Liquidity position tracking
- [ ] Swap execution logic
- [ ] LP token minting/burning

### 2.2 Volatility Calculation Engine (60 min)

**LLM Prompt Template:**

```
"Implement a simple volatility calculation system that:
- Uses Exponentially Weighted Moving Average (EWMA) for recent price changes
- Calculates standard deviation of price returns over a rolling window
- Provides volatility classification (low/medium/high)
- Updates in real-time as new trades occur
- Uses simple decision tree logic for regime detection"
```

**Technical Requirements:**

```python
class VolatilityOracle:
    def __init__(self, window_size: int = 10, alpha: float = 0.3)
    def update_price(self, new_price: float) -> None
    def get_volatility(self) -> float
    def get_volatility_regime(self) -> str  # "low", "medium", "high"
    def should_rebalance(self) -> bool
```

**Deliverables:**

- [ ] VolatilityOracle class with EWMA calculation
- [ ] Regime detection logic
- [ ] Rebalancing trigger conditions

### 2.3 Dynamic Range Adjustment (90 min)

**LLM Prompt Template:**

```
"Create a rebalancing system that:
- Adjusts liquidity ranges based on volatility regime
- Uses simple decision tree logic for range concentration
- Implements atomic rebalancing transactions
- Preserves total liquidity while redistributing across ranges
- Includes safety checks to prevent liquidity loss"
```

**Technical Requirements:**

```python
class RebalancingEngine:
    def calculate_optimal_ranges(self, current_price: float, volatility: float) -> List[Tuple[float, float]]
    def should_rebalance(self) -> bool
    def execute_rebalance(self, new_ranges: List[Tuple[float, float]]) -> None
```

**Decision Tree Logic:**

```
IF volatility < 0.02:
    concentration_factor = 0.5  # Tight ranges
    num_ranges = 3
ELIF volatility > 0.08:
    concentration_factor = 2.0  # Wide ranges
    num_ranges = 5
ELSE:
    concentration_factor = 1.0  # Normal ranges
    num_ranges = 4
```

**Deliverables:**

- [ ] RebalancingEngine with decision tree logic
- [ ] Range calculation algorithms
- [ ] Atomic rebalancing execution
- [ ] Safety validation functions

---

## MILESTONE 3: Integration & Testing (2 hours)

**Target: Working system with simulation**

### 3.1 Contract Integration (60 min)

**LLM Prompt Template:**

```
"Integrate all contract components:
- Connect VolatilityOracle to SeltraPoolContract
- Implement automatic rebalancing triggers
- Add event logging for demo visualization
- Create comprehensive error handling
- Include gas optimization for Algorand"
```

**Deliverables:**

- [ ] Integrated contract system
- [ ] Automatic rebalancing on volatility changes
- [ ] Event logging for frontend
- [ ] Error handling and validation

### 3.2 Simulation Environment (60 min)

**LLM Prompt Template:**

```
"Create a comprehensive simulation environment that:
- Connects market simulator to AMM contract
- Simulates realistic trading scenarios
- Generates demo data for different market conditions
- Includes performance metrics calculation
- Provides data export for frontend visualization"
```

**Technical Requirements:**

```python
class SeltraSimulation:
    def __init__(self, initial_price: float)
    def run_scenario(self, scenario_name: str, duration: int) -> SimulationResult
    def get_metrics(self) -> Dict[str, float]  # APY, slippage, efficiency
    def export_data(self) -> Dict  # For frontend visualization
```

**Deliverables:**

- [ ] Integrated simulation environment
- [ ] Pre-defined market scenarios
- [ ] Performance metrics calculation
- [ ] Data export functionality

---

## MILESTONE 4: Frontend & Visualization (2 hours)

**Target: Demo-ready interface**

### 4.1 Basic Frontend (60 min)

**LLM Prompt Template:**

```
"Create a simple web interface using HTML/CSS/JavaScript that:
- Shows current liquidity ranges as visual bars
- Displays real-time price and volatility
- Includes basic trading interface (swap simulation)
- Shows rebalancing events in real-time
- Uses responsive design for demo presentation"
```

**Technical Requirements:**

- HTML page with canvas for liquidity visualization
- Real-time data updates via WebSocket or polling
- Simple trading form with slippage display
- Volatility indicator with color coding

**Deliverables:**

- [ ] Basic HTML/CSS/JS frontend
- [ ] Liquidity range visualization
- [ ] Real-time price display
- [ ] Trading simulation interface

### 4.2 Demo Scenarios (60 min)

**LLM Prompt Template:**

```
"Create compelling demo scenarios that showcase:
- Calm market with tight liquidity concentration
- Volatile market with wide range distribution
- Real-time rebalancing during regime changes
- Comparison with static AMM performance
- Performance metrics side-by-side display"
```

**Demo Script:**

1. **Scenario 1**: Calm market - show tight concentration
2. **Scenario 2**: Volatility spike - watch ranges widen
3. **Scenario 3**: Recovery - ranges tighten again
4. **Comparison**: Static vs Dynamic AMM performance

**Deliverables:**

- [ ] Pre-recorded demo scenarios
- [ ] Live demo script with talking points
- [ ] Performance comparison charts
- [ ] "Wow factor" moments identified

---

## MILESTONE 5: Deployment & Polish (3 hours)

**Target: Production-ready demo**

### 5.1 Algorand Deployment (90 min)

**LLM Prompt Template:**

```
"Deploy Seltra AMM contracts to Algorand testnet:
- Create deployment scripts for testnet
- Set up proper contract initialization
- Configure ASA assets for testing
- Include deployment verification
- Create simple interaction scripts for demo"
```

**Deliverables:**

- [ ] Contracts deployed to testnet
- [ ] Deployment scripts and documentation
- [ ] Test ASA assets created
- [ ] Basic interaction examples

### 5.2 Demo Preparation (90 min)

**LLM Prompt Template:**

```
"Prepare final demo presentation:
- Create compelling demo scenarios
- Prepare backup screenshots/videos
- Write clear explanation of innovation
- Prepare technical architecture diagram
- Create simple comparison with existing AMMs"
```

**Demo Checklist:**

- [ ] Live demo working smoothly
- [ ] Backup video recordings
- [ ] Technical architecture diagram
- [ ] Performance comparison data
- [ ] Clear innovation explanation

---

## MILESTONE 6: Final Integration & Testing (0.5 hours)

**Target: Demo-ready system**

### 6.1 End-to-End Testing (30 min)

**LLM Prompt Template:**

```
"Perform final end-to-end testing:
- Test all demo scenarios multiple times
- Verify contract deployment and interaction
- Check frontend responsiveness
- Validate performance metrics
- Prepare troubleshooting guide"
```

**Deliverables:**

- [ ] All scenarios tested and working
- [ ] Troubleshooting documentation
- [ ] Performance benchmarks
- [ ] Demo script finalized

---

## Resource Allocation

### Developer A (Backend Focus):

- Milestone 1: Market Simulation Framework
- Milestone 2: Core AMM Contract + Volatility Engine
- Milestone 3: Contract Integration
- Milestone 5: Algorand Deployment

### Developer F (Frontend Focus):

- Milestone 1: Development Environment Setup
- Milestone 2: Dynamic Range Adjustment
- Milestone 4: Frontend & Visualization
- Milestone 6: Final Testing

### Parallel Work Opportunities:

- Milestone 1: Environment setup + Market simulation (parallel)
- Milestone 2: Contract development + Volatility engine (parallel)
- Milestone 4: Frontend development + Demo scenarios (parallel)

---

## Success Criteria

### Technical Achievement:

- [ ] Contracts deployed and functional on Algorand testnet
- [ ] Dynamic liquidity concentration working
- [ ] Volatility-based rebalancing demonstrated
- [ ] Real-time visualization operational

### Demo Impact:

- [ ] Clear demonstration of core innovation
- [ ] Compelling comparison with static AMMs
- [ ] Smooth live demo without technical issues
- [ ] Professional presentation quality

### Judge Appeal:

- [ ] Clear problem-solution fit
- [ ] Working prototype with real blockchain deployment
- [ ] Technical depth appropriate for hackathon scope
- [ ] Innovation clearly differentiated from existing solutions

---

## Risk Mitigation

### Technical Risks:

- **Contract bugs**: Extensive testing in simulation before deployment
- **Deployment issues**: Have backup deployment scripts ready
- **Frontend issues**: Keep visualization simple, focus on core functionality

### Time Risks:

- **Scope creep**: Stick to core features, avoid over-engineering
- **Integration delays**: Plan buffer time for integration milestones
- **Demo preparation**: Start demo scenarios early, not at the end

### Backup Plans:

- **If contracts fail**: Focus on simulation demo with clear explanation
- **If frontend fails**: Use simple charts and live coding demonstration
- **If deployment fails**: Show local testnet deployment with explanation

---

## LLM Prompt Engineering Tips

### Effective Prompts Include:

1. **Clear technical requirements** with specific function signatures
2. **Context about Algorand** and blockchain constraints
3. **Expected deliverables** with checkboxes
4. **Code examples** for desired patterns
5. **Constraints and limitations** (time, complexity, etc.)

### Prompt Templates for Each Component:

- **Contract Development**: Include Algorand Python syntax, ASA handling, gas optimization
- **Algorithm Implementation**: Include mathematical formulas, decision trees, validation logic
- **Integration**: Include error handling, event logging, testing requirements
- **Frontend**: Include responsive design, real-time updates, demo scenarios

---

_This roadmap is optimized for LLM-assisted development with clear milestones, specific technical requirements, and well-defined deliverables for each phase._
