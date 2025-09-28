import logging

import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from smart_contracts.rebalancing_engine.contract import RebalancingEngineContract

logger = logging.getLogger(__name__)


def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.AppSpec,
    deployer: algokit_utils.Account,
    template_values: dict[str, str] | None = None,
) -> algokit_utils.DeployResponse:
    """Deploy the RebalancingEngine contract."""
    logger.info("Deploying RebalancingEngine contract...")
    
    # Default template values for RebalancingEngine
    default_template_values = {
        "authorized_pool_id": "0",  # Will be set during initialization
        "max_slippage": "100",      # 1% maximum slippage
        "cooldown_seconds": "300",  # 5 minutes cooldown
        "min_range_size": "50",     # 0.5% minimum range size
    }
    
    if template_values:
        default_template_values.update(template_values)
    
    return algokit_utils.deploy(
        algod_client=algod_client,
        indexer_client=indexer_client,
        app_spec=app_spec,
        deployer=deployer,
        template_values=default_template_values,
    )
