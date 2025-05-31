import argparse
import asyncio
from typing import List
import os
# from config.config import (
#     RPC_URLS,
#     ETHERSCAN_API_KEY,
# )

from config.config import *

class DefiAuditor:
    
    def __init__(self, chain: str = "ethereum"):
        self.chain = chain
    

    def _get_contract_files(self, path: str) -> List[str]:
        contract_files = []
        
        if os.path.isfile(path):
            if path.endswith(('.sol', '.vy')):
                contract_files.append(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(('.sol', '.vy')):
                        contract_files.append(os.path.join(root, file))

        return contract_files
    
    async def test_file_fetch(
        self,
        paths: str,
    ) -> List[str]:
        
        try:
            all_contract_files = []
            for path in paths:
                all_contract_files.extend(self._get_contract_files(path))

            print(f"Found {len(all_contract_files)} contract files to analyze")
            return all_contract_files
        except:
            print(f"Error here")


async def main():
    # we'll first need to fetch and get all the data for the audit to be done
    """1. Smart Contract(s) itself
            - either by fetching it through etherscan (for staring) via address (if its verified) (will add it later)
            - either by getting it from user itself ##### would be better is unverifeid/ undeloyed as well (firstly)
       2. ABI code ??
       3. ByteCode if required ??
    """

    # - - - - -> -> -> we'll use class structure (suggested by GPT)

    #lets just first take input files from user.

    parser = argparse.ArgumentParser(
        description="DeFi Smart Contract Auditor"
    )

    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Paths to smart contract files or directories to audit"
    )

    parser.add_argument(
        "--chain",
        default="ethereum",
        choices=["ethereum", "bsc", "avalanche"],
        help="chain"
    )

    args = parser.parse_args()

    auditor = DefiAuditor(args.chain)
    contract_files = await auditor.test_file_fetch(args.files)
    for i in contract_files:
        print("we have",i)


    # Simulate async audit logic
    await asyncio.sleep(0.1)  


if __name__ == "__main__":
    asyncio.run(main())


    


