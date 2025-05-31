import os


RPC_URLS = {
    "ethereum": os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/your-project-id"),
    "bsc": os.getenv("BSC_RPC_URL", "https://bsc-dataseed.binance.org/"),
    "avalanche": os.getenv("AVALANCHE_RPC_URL", "https://api.avax.network/ext/bc/C/rpc")
}

ETHERSCAN_API_KEY = "abc"