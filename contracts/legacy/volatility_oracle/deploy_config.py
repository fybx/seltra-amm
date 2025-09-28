import logging

import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

from smart_contracts.volatility_oracle.contract import VolatilityOracleContract

logger = logging.getLogger(__name__)


# define deployment behaviour based on supplied app spec
def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:
    from algokit_utils.config import config

    config.configure(
        debug=True,
        # trace_all=True,  # uncomment for detailed logging
    )

    app_client = algokit_utils.ApplicationClient(
        algod_client,
        app_spec,
        creator=deployer,
        indexer_client=indexer_client,
    )

    app_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )
    
    logger.info(f"Volatility Oracle deployed with app ID: {app_client.app_id}")
    
    return app_client
