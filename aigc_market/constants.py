import os
from enum import Enum
from dotenv import load_dotenv
import pathlib

load_dotenv(os.path.join(pathlib.Path(__file__).parent.resolve(), 'hardhat/.env'))


class Web3Constants:
    admin_wallet = os.environ['ACCOUNT_ADDRESS']
    private_key = os.environ['ACCOUNT_PRIVATE_KEY']
    nft_contract_address = os.environ['NFT_CONTRACT_ADDRESS']
    nft_contract_name = os.environ['NFT_CONTRACT_NAME']
    infura_key = os.environ['INFURA_KEY']
    pinata_key = os.environ['PINATA_KEY']
    pinata_secret = os.environ['PINATA_SECRET']
    pinata_access_token = os.environ['PINATA_ACCESS_TOKEN']


class InfuraNetwork(Enum):
    ETH_MAIINNET = 'mainnet'
    ETH_GOERLI = 'goerli'
