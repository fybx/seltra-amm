import logging

import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

# from smart_contracts.seltra_pool.contract import SeltraPoolContract  # Not needed for deployment

logger = logging.getLogger(__name__)


# define deployment behaviour based on supplied app spec
def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.Arc56Contract,
    deployer: algokit_utils.Account,
) -> algokit_utils.AppClient:
    from algokit_utils.config import config

    config.configure(
        debug=True,
        # trace_all=True,  # uncomment for detailed logging
    )

    # Create AppClient with correct parameters for current AlgoKit Utils version
    app_client = algokit_utils.AppClient(
        app_spec,
        algod_client,
        creator=deployer,
        indexer_client=indexer_client,
    )

    app_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )
    
    logger.info(f"Seltra Pool deployed with app ID: {app_client.app_id}")
    
    return app_client
