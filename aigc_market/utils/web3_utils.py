import json
import requests
import os

from pinata import Pinata
from web3 import Web3
from web3.middleware import geth_poa_middleware
from aigc_market.constants import Web3Constants, InfuraNetwork
from aigc_market.utils.environment_utils import is_prod_environment
from django.conf import settings
from binascii import unhexlify


def get_network(force_prod: bool = False) -> InfuraNetwork:
    if is_prod_environment() or force_prod:
        return InfuraNetwork.ETH_MAIINNET
    else:
        return InfuraNetwork.ETH_GOERLI


def get_web3(network: InfuraNetwork) -> Web3:
    web3 = Web3(Web3.HTTPProvider(f'https://{network.value}.infura.io/v3/{Web3Constants.infura_key}'))
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return web3


def get_abi_json(contract_name: str) -> dict:
    with open(os.path.join(str(settings.BASE_DIR), f'aigc_market/hardhat/artifacts/contracts/{contract_name}'
                                              f'.sol/{contract_name}.json'), 'r') as f:
        return json.load(f)


def get_nft_contract(web3: Web3):
    abi = get_abi_json(Web3Constants.nft_contract_name)
    return web3.eth.contract(address=Web3Constants.nft_contract_address, abi=json.dumps(abi['abi']))


class PinataClient(Pinata):
    def pin_json(self, json_dict: dict):
        payload = {
            'pinataContent': json.dumps(json_dict)
        }
        response = requests.post(f'{self.base_url}pinning/pinJSONToIPFS', headers=self.headers, data=payload).json()
        if 'error' in response:
            return {'status': 'error', 'message': response['error']}
        return {'status': 'success', 'data': response}

    def pin_file(self, file: str):
        if not os.path.isfile(file):
            return {'status': 'error', 'message':'File does not exist'}
        files = {
            'file': open(file, 'rb')
        }
        response = requests.post(f'{self.base_url}pinning/pinFileToIPFS', headers=self.headers, files=files).json()
        if 'error' in response:
            return {'status': 'error', 'message': response['error']['details']}
        return {'status': 'success', 'data': response}

    @staticmethod
    def get_ipfs_content_uri(response: dict) -> str:
        ipfs_hash = response['data']['IpfsHash']
        base_url = "https://gateway.pinata.cloud/ipfs/"
        token_uri = base_url + ipfs_hash
        return token_uri

    def upload_nft_metadata_to_pinata(self, metadata: dict) -> str:
        response = self.pin_json(metadata)
        return PinataClient.get_ipfs_content_uri(response)

    def upload_media_to_pinata(self, f_bytes: bytes) -> str:
        path = os.path.join(str(settings.BASE_DIR), 'temp_file')
        with open(path, 'wb') as f:
            f.write(f_bytes)
        response = self.pin_file(path)
        os.remove(path)
        return PinataClient.get_ipfs_content_uri(response)


class DavinciMindMasterContract:
    def __init__(self, force_prod: bool = False):
        self.network = get_network(force_prod)
        self.web3 = get_web3(self.network)
        self.contract = get_nft_contract(self.web3)
        self.pinata_client = PinataClient(Web3Constants.pinata_key, Web3Constants.pinata_secret, Web3Constants.pinata_access_token)

    def mint_aigc_nft(self, user_wallet: str, doc_id: str, encryption_key: bytes, encrypted_doc: bytes,
                      encryptor: str, media_content: bytes) -> dict:
        metadata = {
            "name": f"DavinciMind doc {doc_id}",
            "description": f"NFT minted for AIGC doc_id = {doc_id}",
            "encrypted_doc": encrypted_doc.decode(),
            "attributes": [
                {
                    "trait_type": "MediaType",
                    "value": "Image"
                }
            ]
        }
        media_uri = self.pinata_client.upload_media_to_pinata(media_content)
        metadata['image'] = media_uri
        metadata_uri = self.pinata_client.upload_nft_metadata_to_pinata(metadata)
        # use ipfs suffix as our doc id in contract so the NFT metadata can be referenced
        ipfs_suffix = metadata_uri.split('/')[-1]

        transaction = self.contract.functions.mintAigcNft(
            ipfs_suffix,
            Web3.toChecksumAddress(user_wallet),
            encryption_key.decode(),
            encryptor
        ).buildTransaction({
            'from': Web3Constants.admin_wallet,
            'gas': 500000,
            'gasPrice': self.web3.toWei('2', 'gwei'),
            'nonce': self.web3.eth.getTransactionCount(Web3Constants.admin_wallet)
        })
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=unhexlify(Web3Constants.private_key))
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)

        return {
            'nft_metadata_uri': metadata_uri,
            'media_uri': media_uri,
            'tx_hash': self.web3.toHex(tx_hash),
            'tx_receipt': tx_receipt,
            'network': self.network.value
        }


if __name__ == "__main__":
    contract = get_nft_contract(get_web3(get_network()))
    print(contract.functions.totalSupply().call())
