"""
Seltra Market Simulator Service

Provides realistic market simulation for testing and demonstrating
the Seltra AMM dynamic liquidity management capabilities.
"""

import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .market_simulator import MarketSimulator
from .blockchain_simulator import AlgorandTransactionSimulator
from .api.routes import router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global simulator instances
simulator: MarketSimulator = None
blockchain_simulator: AlgorandTransactionSimulator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    global simulator, blockchain_simulator
    
    # Startup
    logger.info("Starting Seltra Simulation Services...")
    
    # Initialize market simulator
    simulator = MarketSimulator(
        initial_price=100.0,
        initial_volatility=0.02,
        tick_interval=1.0
    )
    
    # Initialize blockchain simulator with market simulator reference
    # Load configuration from environment variables
    import os

    pool_app_id = os.getenv('SELTRA_POOL_APP_ID')
    if pool_app_id and pool_app_id.strip():
        pool_app_id = int(pool_app_id)
    else:
        pool_app_id = None
    
    asset_x_id_str = os.getenv('ASSET_X_ID', '0')
    asset_x_id = int(asset_x_id_str) if asset_x_id_str and asset_x_id_str.strip() else 0
    
    asset_y_id = os.getenv('ASSET_Y_ID')  # HACK token ID
    if asset_y_id and asset_y_id.strip():
        asset_y_id = int(asset_y_id)
    else:
        asset_y_id = None
        
    faucet_private_key = os.getenv('FAUCET_PRIVATE_KEY')

    # Convert string IDs to integers
    try:
        pool_app_id = int(pool_app_id) if pool_app_id else None
        asset_x_id = int(asset_x_id)
        asset_y_id = int(asset_y_id) if asset_y_id else None
    except (ValueError, TypeError):
        logger.warning("Invalid contract IDs in environment variables, using None")
        pool_app_id = None
        asset_x_id = 0  # ALGO
        asset_y_id = None

    logger.info(f"📋 Loaded configuration:")
    logger.info(f"   Pool App ID: {pool_app_id}")
    logger.info(f"   Asset X ID (ALGO): {asset_x_id}")
    logger.info(f"   Asset Y ID (HACK): {asset_y_id}")

    blockchain_simulator = AlgorandTransactionSimulator(
        algod_address="http://algod:8080",  # Use docker service name
        num_wallets=20,
        market_simulator=simulator,  # Pass market simulator for volatility sync
        pool_app_id=pool_app_id,
        asset_x_id=asset_x_id,
        asset_y_id=asset_y_id,
        faucet_private_key=faucet_private_key
    )
    
    try:
        # Initialize blockchain simulator
        await blockchain_simulator.initialize()
    except Exception as e:
        logger.warning(f"Blockchain simulator initialization failed: {e}")
        logger.info("Continuing with market simulation only...")
    
    # Start simulations in background tasks
    market_task = asyncio.create_task(simulator.run_simulation())
    blockchain_task = None
    
    if blockchain_simulator:
        blockchain_task = asyncio.create_task(blockchain_simulator.start_simulation())
    
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down Simulation Services...")
        
        if simulator:
            simulator.stop_simulation()
        if blockchain_simulator:
            blockchain_simulator.stop_simulation()
            await blockchain_simulator.cleanup()
        
        # Cancel background tasks
        market_task.cancel()
        if blockchain_task:
            blockchain_task.cancel()
        
        try:
            await market_task
            if blockchain_task:
                await blockchain_task
        except asyncio.CancelledError:
            pass


# Create FastAPI app with lifespan events
app = FastAPI(
    title="Seltra Market Simulator",
    description="Real-time market simulation for Seltra AMM development and testing",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global simulator, blockchain_simulator
    return {
        "status": "healthy",
        "market_simulator_active": simulator.is_running if simulator else False,
        "blockchain_simulator_active": blockchain_simulator.is_running if blockchain_simulator else False,
        "current_price": simulator.get_current_price() if simulator else None,
        "total_wallets": len(blockchain_simulator.wallet_manager.wallets) if blockchain_simulator and blockchain_simulator.wallet_manager else 0
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Seltra Market Simulator API",
        "version": "0.1.0",
        "docs": "/docs"
    }


def get_simulator() -> MarketSimulator:
    """Get the global market simulator instance."""
    return simulator


def get_blockchain_simulator() -> AlgorandTransactionSimulator:
    """Get the global blockchain simulator instance."""
    return blockchain_simulator


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "simulation.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
