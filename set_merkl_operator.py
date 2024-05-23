from web3 import Web3
import json
import os
import dotenv

dotenv.load_dotenv(dotenv_path='.env')
RPC_URL = os.getenv('RPC_URL')
MERKL_TRUSTED_ADDRESS = os.getenv('MERKL_TRUSTED_ADDRESS')
MERKL_TRUSTED_ADDRESS_KEY = os.getenv('MERKL_TRUSTED_ADDRESS_KEY')

w3 = Web3(Web3.HTTPProvider(RPC_URL))

with open('distributor_abi.json') as f:
    distributor_abi = json.load(f)

with open('arcadia_factory_abi.json') as f:
    arcadia_factory_abi = json.load(f)

distributor = w3.eth.contract(address='0x3Ef3D8bA38EBe18DB133cEc108f4D14CE00Dd9Ae', abi=distributor_abi)
arcadia_factory = w3.eth.contract(address='0xDa14Fdd72345c4d2511357214c5B89A919768e59', abi=arcadia_factory_abi)
ARCADIA_CLAIMER = "0x3146e7bCeE81aE5a9BDcC8452ba7bBf9f8524205"

def main():
    amount_of_accounts = arcadia_factory.functions.allAccountsLength().call()
    for i in range(0, amount_of_accounts):
        account_address = arcadia_factory.functions.allAccounts(i).call()
        is_operator = distributor.functions.operators(account_address, ARCADIA_CLAIMER).call()
        if is_operator == 0:
            gas_price = w3.eth.gas_price
            tx = distributor.functions.toggleOperator(account_address, ARCADIA_CLAIMER).build_transaction({
                'from': MERKL_TRUSTED_ADDRESS,
                'maxFeePerGas': gas_price,
                'nonce': w3.eth.get_transaction_count(MERKL_TRUSTED_ADDRESS),
                'chainId': 8453
            })
            gas_usage = w3.eth.estimate_gas(tx)
            tx.update({'gas': int(gas_usage * 1.2)})
            tx_signed = w3.eth.account.sign_transaction(tx, MERKL_TRUSTED_ADDRESS_KEY)
            tx_hash = w3.eth.send_raw_transaction(tx_signed.rawTransaction)
            w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f'Set for account ID {i}: {tx_hash.hex()}')

if __name__ == '__main__':
    main()