import os
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv
import time

import deploy

# Load environment variables
load_dotenv()

# Set up web3 connection
provider_url = os.getenv("CELO_PROVIDER_URL")
w3 = Web3(HTTPProvider(provider_url))
assert w3.is_connected(), "Not connected to a Celo node"

# Add PoA middleware to web3.py instance
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Get contract ABI and address
abi = deploy.abi
contract_address = deploy.contract_address
contract = w3.eth.contract(address=contract_address, abi=abi)

# Initialize account
account_address = os.getenv("CELO_DEPLOYER_ADDRESS")
private_key = os.getenv("CELO_DEPLOYER_PRIVATE_KEY")



# Function to create a proposal
def create_proposal(description, recipient, amount, private_key):
    
     # Ensure chainId matches the network you are using (e.g., 44787 for Alfajores Testnet)
    chain_id = 44787
    
    # Fetch the current gas price from the network
    current_gas_price = w3.eth.gas_price

    # Ensure that the nonce is correctly set
    nonce = w3.eth.get_transaction_count(account_address, 'pending')

    # Build the transaction
    txn = contract.functions.createProposal(description, recipient, amount).build_transaction({
        'chainId': chain_id,
        'gas': 2000000,
        'gasPrice': current_gas_price,
        'nonce': nonce
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    print(f"Proposal Created: {txn_hash.hex()}")


# Function to vote for a proposal
def vote(proposal_id, private_key):
     # Fetch the current gas price from the network and increase it to ensure quick mining
    current_gas_price = w3.eth.gas_price
    increased_gas_price = int(current_gas_price * 1.2)
    
    # Ensure that the nonce is correctly set
    nonce = w3.eth.get_transaction_count(account_address, 'pending')

    txn = contract.functions.vote(proposal_id).build_transaction({
        'chainId': 44787,
        'gas': 200000,
        'gasPrice': increased_gas_price,
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    print(f"Voted: {txn_hash.hex()}")

# Function to execute a proposal
def execute_proposal(proposal_id, private_key):
     # Fetch the current gas price from the network and increase it to ensure quick mining
    current_gas_price = w3.eth.gas_price
    increased_gas_price = int(current_gas_price * 1.5)
    
    # Ensure that the nonce is correctly set
    nonce = w3.eth.get_transaction_count(account_address, 'pending')

    txn = contract.functions.executeProposal(proposal_id).build_transaction({
        'chainId': 44787,
        'gas': 200000,
        'gasPrice': increased_gas_price,
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

    print(f"Proposal Executed: {txn_hash.hex()}")

# Example Usage
description = "Send funds to charity"
recipient =  "0xcdd1151b2bC256103FA2565475e686346CeFd813" # "RECIPIENT_ADDRESS"
amount = int(w3.to_wei(0.00001, 'ether'))  # 1 Ether

# Create a new proposal
create_proposal(description, recipient, amount, private_key)

# Vote for the proposal with id 0
vote(0, private_key)

# Execute the proposal with id 0
execute_proposal(0, private_key)