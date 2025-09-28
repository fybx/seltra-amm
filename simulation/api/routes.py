"""
API routes for the Seltra Market Simulator.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple
import sys
import os

# Add the contracts directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../contracts/refactored'))

# Import will be resolved at runtime when the module is loaded
# This avoids circular imports since main.py imports this file

router = APIRouter()

# Initialize backend service for contract integration
try:
    from backend_service import SeltraBackendService
    backend_service = SeltraBackendService()
    CONTRACT_INTEGRATION_AVAILABLE = True
except Exception as e:
    print(f"Warning: Contract integration not available: {e}")
    CONTRACT_INTEGRATION_AVAILABLE = False


class ScenarioRequest(BaseModel):
    scenario: str


class VolatilityRequest(BaseModel):
    regime: str


class PriceShockRequest(BaseModel):
    magnitude: float
    duration: int = 60


class VolumeRequest(BaseModel):
    profile: str


class VolumeSpikeRequest(BaseModel):
    multiplier: float
    duration: int


class TradeRequest(BaseModel):
    size: float
    direction: str = "buy"


class TradingPatternRequest(BaseModel):
    pattern: str


class BlockchainConfigRequest(BaseModel):
    num_wallets: Optional[int] = None
    algod_address: Optional[str] = None


@router.get("/price")
async def get_current_price():
    """Get the current market price."""
    from simulation.main import get_simulator
    
    simulator = get_simulator()
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not available")
    
    return {
        "price": simulator.get_current_price(),
        "volatility": simulator.get_current_volatility(),
        "timestamp": int(__import__("time").time())
    }


@router.get("/history")
async def get_price_history(window: int = 100):
    """Get recent price history."""
    from simulation.main import get_simulator
    
    simulator = get_simulator()
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not available")
    
    history = simulator.get_price_history(window)
    return {
        "history": [
            {"price": price, "volume": volume, "timestamp": timestamp}
            for price, volume, timestamp in history
        ],
        "count": len(history)
    }


@router.get("/metrics")
async def get_simulation_metrics():
    """Get detailed simulation metrics."""
    from simulation.main import get_simulator
    
    simulator = get_simulator()
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not available")
    
    return simulator.get_metrics()


@router.post("/scenario")
async def set_scenario(request: ScenarioRequest):
    """Set the market scenario."""
    from simulation.main import get_simulator
    
    simulator = get_simulator()
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not available")
    
    valid_scenarios = [
        "normal", "volatile", "calm", "trending", 
        "mean_reverting", "flash_crash", "whale_activity"
    ]
    
    if request.scenario not in valid_scenarios:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid scenario. Valid options: {valid_scenarios}"
        )
    
    simulator.set_scenario(request.scenario)
    return {"message": f"Scenario set to {request.scenario}"}


@router.post("/volatility")
async def set_volatility_regime(request: VolatilityRequest):
    """Set the volatility regime."""
    from simulation.main import get_simulator
    
    simulator = get_simulator()
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not available")
    
    valid_regimes = ["low", "medium", "high"]
    
    if request.regime not in valid_regimes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid regime. Valid options: {valid_regimes}"
        )
    
    simulator.set_volatility_regime(request.regime)
    return {"message": f"Volatility regime set to {request.regime}"}


@router.post("/shock")
async def add_price_shock(request: PriceShockRequest):
    """Add a price shock to the simulation."""
    from simulation.main import get_simulator
    
    simulator = get_simulator()
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not available")
    
    if abs(request.magnitude) > 0.5:  # Limit to 50% shocks
        raise HTTPException(
            status_code=400,
            detail="Magnitude must be between -0.5 and 0.5"
        )
    
    simulator.add_price_shock(request.magnitude, request.duration)
    return {
        "message": f"Price shock added: {request.magnitude:.1%} for {request.duration}s"
    }


@router.post("/volume/profile")
async def set_volume_profile(request: VolumeRequest):
    """Set the volume profile."""
    from simulation.main import get_simulator
    
    simulator = get_simulator()
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not available")
    
    valid_profiles = ["light", "normal", "heavy", "whale_activity"]
    
    if request.profile not in valid_profiles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid profile. Valid options: {valid_profiles}"
        )
    
    simulator.set_volume_profile(request.profile)
    return {"message": f"Volume profile set to {request.profile}"}


@router.post("/volume/spike")
async def add_volume_spike(request: VolumeSpikeRequest):
    """Add a volume spike."""
    from simulation.main import get_simulator
    
    simulator = get_simulator()
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not available")
    
    if request.multiplier < 1.0 or request.multiplier > 20.0:
        raise HTTPException(
            status_code=400,
            detail="Multiplier must be between 1.0 and 20.0"
        )
    
    simulator.add_volume_spike(request.multiplier, request.duration)
    return {
        "message": f"Volume spike added: {request.multiplier}x for {request.duration}s"
    }


@router.post("/trade/simulate")
async def simulate_trade(request: TradeRequest):
    """Simulate a trade and get execution details."""
    from simulation.main import get_simulator
    
    simulator = get_simulator()
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not available")
    
    if request.direction not in ["buy", "sell"]:
        raise HTTPException(
            status_code=400,
            detail="Direction must be 'buy' or 'sell'"
        )
    
    if request.size <= 0:
        raise HTTPException(
            status_code=400,
            detail="Trade size must be positive"
        )
    
    execution_price, slippage = simulator.simulate_trade(
        request.size, request.direction
    )
    
    return {
        "execution_price": execution_price,
        "slippage": slippage,
        "slippage_bps": int(slippage * 10000),
        "current_price": simulator.get_current_price(),
        "trade_size": request.size,
        "direction": request.direction
    }


@router.post("/reset")
async def reset_simulation(initial_price: Optional[float] = None):
    """Reset the simulation to initial state."""
    from simulation.main import get_simulator
    
    simulator = get_simulator()
    if not simulator:
        raise HTTPException(status_code=503, detail="Simulator not available")
    
    simulator.reset_simulation(initial_price)
    return {
        "message": "Simulation reset",
        "initial_price": simulator.initial_price,
        "current_price": simulator.get_current_price()
    }


@router.get("/status")
async def get_status():
    """Get simulation status."""
    from simulation.main import get_simulator, get_blockchain_simulator
    
    simulator = get_simulator()
    blockchain_sim = get_blockchain_simulator()
    
    if not simulator:
        raise HTTPException(status_code=503, detail="Market simulator not available")
    
    market_metrics = simulator.get_metrics()
    blockchain_metrics = blockchain_sim.get_metrics() if blockchain_sim else {}
    
    return {
        "market_simulation": {
            "running": simulator.is_running,
            "current_price": simulator.get_current_price(),
            "current_volatility": simulator.get_current_volatility(),
            "scenario": market_metrics.get("scenario", "unknown"),
            "regime": market_metrics.get("regime", "unknown"),
            "uptime": market_metrics.get("uptime_seconds", 0),
            "total_trades": market_metrics.get("total_trades", 0)
        },
        "blockchain_simulation": {
            "running": blockchain_metrics.get("is_running", False),
            "total_transactions": blockchain_metrics.get("total_transactions", 0),
            "success_rate": blockchain_metrics.get("success_rate", 0),
            "transactions_per_minute": blockchain_metrics.get("transactions_per_minute", 0),
            "current_pattern": blockchain_metrics.get("current_pattern", "unknown"),
            "active_wallets": blockchain_metrics.get("active_wallets", 0),
            "pending_transactions": blockchain_metrics.get("pending_transactions", 0)
        }
    }


# Blockchain Simulation Endpoints

@router.get("/blockchain/wallets")
async def get_blockchain_wallets():
    """Get information about all simulated wallets."""
    from simulation.main import get_blockchain_simulator
    
    blockchain_sim = get_blockchain_simulator()
    if not blockchain_sim:
        raise HTTPException(status_code=503, detail="Blockchain simulator not available")
    
    wallets = blockchain_sim.get_wallet_info()
    return {
        "wallets": wallets,
        "total_count": len(wallets),
        "whale_count": len([w for w in wallets if w["pattern"] == "whale"]),
        "retail_count": len([w for w in wallets if w["pattern"] == "retail"])
    }


@router.get("/blockchain/metrics")
async def get_blockchain_metrics():
    """Get detailed blockchain simulation metrics."""
    from simulation.main import get_blockchain_simulator
    
    blockchain_sim = get_blockchain_simulator()
    if not blockchain_sim:
        raise HTTPException(status_code=503, detail="Blockchain simulator not available")
    
    return blockchain_sim.get_metrics()


@router.post("/blockchain/pattern")
async def set_trading_pattern(request: TradingPatternRequest):
    """Set the blockchain trading pattern (normal, volatile, etc.)."""
    from simulation.main import get_blockchain_simulator
    
    blockchain_sim = get_blockchain_simulator()
    if not blockchain_sim:
        raise HTTPException(status_code=503, detail="Blockchain simulator not available")
    
    valid_patterns = ["normal", "volatile"]
    
    if request.pattern not in valid_patterns:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid pattern. Valid options: {valid_patterns}"
        )
    
    blockchain_sim.set_trading_pattern(request.pattern)
    return {"message": f"Trading pattern set to {request.pattern}"}


@router.post("/blockchain/reset")
async def reset_blockchain_simulation():
    """Reset the blockchain simulation."""
    from simulation.main import get_blockchain_simulator
    
    blockchain_sim = get_blockchain_simulator()
    if not blockchain_sim:
        raise HTTPException(status_code=503, detail="Blockchain simulator not available")
    
    try:
        # Stop current simulation
        blockchain_sim.stop_simulation()
        
        # Reinitialize
        await blockchain_sim.initialize()
        
        # Start new simulation
        import asyncio
        asyncio.create_task(blockchain_sim.start_simulation())
        
        return {"message": "Blockchain simulation reset successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")


@router.get("/blockchain/transactions/pending")
async def get_pending_transactions():
    """Get currently pending transactions."""
    from simulation.main import get_blockchain_simulator
    
    blockchain_sim = get_blockchain_simulator()
    if not blockchain_sim:
        raise HTTPException(status_code=503, detail="Blockchain simulator not available")
    
    pending = []
    for plan in blockchain_sim.transaction_queue:
        pending.append({
            "wallet_address": plan.wallet.address[:12] + "...",
            "transaction_type": plan.tx_type.value,
            "size": plan.size,
            "target_time": plan.target_time,
            "time_until_execution": max(0, plan.target_time - __import__("time").time())
        })
    
    return {
        "pending_transactions": pending,
        "count": len(pending)
    }


@router.post("/demo/scenario")
async def trigger_demo_scenario(scenario_name: str):
    """Trigger a predefined demo scenario combining market and blockchain simulation."""
    from simulation.main import get_simulator, get_blockchain_simulator
    
    simulator = get_simulator()
    blockchain_sim = get_blockchain_simulator()
    
    if not simulator or not blockchain_sim:
        raise HTTPException(status_code=503, detail="Simulators not available")
    
    scenarios = {
        "calm_market": {
            "market_scenario": "calm",
            "volatility_regime": "low",
            "trading_pattern": "normal"
        },
        "volatile_spike": {
            "market_scenario": "volatile", 
            "volatility_regime": "high",
            "trading_pattern": "volatile"
        },
        "flash_crash": {
            "market_scenario": "flash_crash",
            "volatility_regime": "high", 
            "trading_pattern": "volatile"
        },
        "whale_activity": {
            "market_scenario": "normal",
            "volatility_regime": "medium",
            "trading_pattern": "normal"  # Whales are created in wallet generation
        }
    }
    
    if scenario_name not in scenarios:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario. Available: {list(scenarios.keys())}"
        )
    
    config = scenarios[scenario_name]
    
    # Set market conditions
    simulator.set_scenario(config["market_scenario"])
    simulator.set_volatility_regime(config["volatility_regime"])
    
    # Set blockchain trading pattern
    blockchain_sim.set_trading_pattern(config["trading_pattern"])
    
    return {
        "message": f"Demo scenario '{scenario_name}' activated",
        "configuration": config
    }


# Contract Integration Endpoints

class SwapRequest(BaseModel):
    userAddress: str
    assetIn: int
    assetOut: int
    amountIn: int
    minAmountOut: int = 0


@router.get("/contract-metrics")
async def get_contract_metrics():
    """Get comprehensive metrics from deployed contracts and backend service."""
    if not CONTRACT_INTEGRATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Contract integration not available")
    
    try:
        metrics = backend_service.get_contract_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contract metrics: {str(e)}")


@router.post("/execute-swap")
async def execute_swap(request: SwapRequest):
    """Execute a swap on the deployed contracts."""
    if not CONTRACT_INTEGRATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Contract integration not available")
    
    try:
        # For demo purposes, we'll simulate the swap
        # In a real implementation, this would call the contract client
        from simulation.main import get_simulator
        simulator = get_simulator()
        
        if not simulator:
            raise HTTPException(status_code=503, detail="Simulator not available")
        
        # Simulate swap execution
        current_price = simulator.get_current_price()
        if request.assetIn == 0:  # ALGO to HACK
            amount_out = int(request.amountIn * 1000000 / current_price)  # Convert to HACK
        else:  # HACK to ALGO
            amount_out = int(request.amountIn * current_price / 1000000)  # Convert to ALGO
        
        # Generate a mock transaction ID
        import time
        tx_id = f"SWAP_{int(time.time())}_{request.userAddress[:8]}"
        
        return {
            "transactionId": tx_id,
            "amountOut": amount_out,
            "priceImpact": 10,  # 0.1% in basis points
            "feePaid": int(request.amountIn * 30 / 10000),  # 0.3% fee
            "newPrice": current_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Swap execution failed: {str(e)}")


@router.post("/trigger-rebalance")
async def trigger_rebalance():
    """Trigger liquidity rebalancing on deployed contracts."""
    if not CONTRACT_INTEGRATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Contract integration not available")
    
    try:
        # Get current market conditions
        from simulation.main import get_simulator
        simulator = get_simulator()
        
        if not simulator:
            raise HTTPException(status_code=503, detail="Simulator not available")
        
        current_price = simulator.get_current_price()
        current_volatility = simulator.get_current_volatility()
        
        # Update oracle with current price
        volatility, regime = backend_service.update_oracle(current_price)
        
        # Check if rebalancing is needed
        should_rebalance, optimal_ranges, reason = backend_service.check_rebalancing(
            current_price=current_price,
            current_volatility=current_volatility,
            total_liquidity=1000000.0,  # Demo value
            current_efficiency=45.0,    # Demo value
            time_since_last=400,        # Demo value
            volatility_change=2.5       # Demo value
        )
        
        if should_rebalance:
            # Execute rebalance on chain
            tx_id = await backend_service.execute_rebalance_on_chain(optimal_ranges)
            
            return {
                "transactionId": tx_id,
                "reason": reason,
                "optimalRanges": [
                    {
                        "lower": r.lower,
                        "upper": r.upper,
                        "liquidity": r.liquidity
                    }
                    for r in optimal_ranges
                ],
                "volatilityRegime": regime
            }
        else:
            return {
                "message": "No rebalancing needed",
                "reason": reason,
                "volatilityRegime": regime
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebalance failed: {str(e)}")


@router.get("/contract-state")
async def get_contract_state():
    """Get current state from deployed contracts."""
    if not CONTRACT_INTEGRATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Contract integration not available")
    
    try:
        contract_state = backend_service.sync_with_contracts()
        return contract_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contract state: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for the simulation service."""
    from simulation.main import get_simulator, get_blockchain_simulator
    
    simulator = get_simulator()
    blockchain_sim = get_blockchain_simulator()
    
    return {
        "status": "healthy",
        "market_simulator": simulator is not None,
        "blockchain_simulator": blockchain_sim is not None,
        "contract_integration": CONTRACT_INTEGRATION_AVAILABLE,
        "timestamp": int(__import__("time").time())
    }
