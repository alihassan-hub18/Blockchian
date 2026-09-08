import hashlib
import time
import json
from ecdsa import SigningKey, SECP256k1, VerifyingKey

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()
        self.signature = None

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "timestamp": self.timestamp
        }

    def sign_transaction(self, private_key):
        private_key_obj = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        transaction_data = json.dumps(self.to_dict(), sort_keys=True).encode()
        self.signature = private_key_obj.sign(transaction_data).hex()

    def verify_signature(self):
        if not self.signature:
            return False
        if self.sender == "SYSTEM":
            return True
        try:
            public_key_obj = VerifyingKey.from_string(bytes.fromhex(self.sender), curve=SECP256k1)
            transaction_data = json.dumps(self.to_dict(), sort_keys=True).encode()
            return public_key_obj.verify(bytes.fromhex(self.signature), transaction_data)
        except Exception:
            return False

class Block:
    def __init__(self, index, transactions, previous_hash, difficulty=2):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.difficulty = difficulty
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self):
        target = "0" * self.difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()
        print(f"[Block Mined]: {self.hash} (Nonce: {self.nonce})")

class AdvancedBlockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = 2
        self.mining_reward = 50
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_tx = Transaction("SYSTEM", "GenesisAddress", 0)
        genesis_block = Block(0, [genesis_tx], "0", self.difficulty)
        genesis_block.mine_block()
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        if not transaction.verify_signature():
            raise Exception("Invalid Transaction Signature! Rejected.")
        self.pending_transactions.append(transaction)
        return True

    def mine_pending_transactions(self, miner_address):
        reward_tx = Transaction("SYSTEM", miner_address, self.mining_reward)
        self.pending_transactions.append(reward_tx)

        block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=self.get_latest_block().hash,
            difficulty=self.difficulty
        )
        block.mine_block()
        self.chain.append(block)
        self.pending_transactions = []

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.compute_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
            for tx in current_block.transactions:
                if not tx.verify_signature():
                    return False
        return True

if __name__ == "__main__":
    # Generate cryptographic wallet keys using ECDSA SigningKey
    alice_sk = SigningKey.generate(curve=SECP256k1)
    alice_vk = alice_sk.get_verifying_key()
    alice_private = alice_sk.to_string().hex()
    alice_public = alice_vk.to_string().hex()

    # Fixed: VerifyingKey is derived from SigningKey
    bob_sk = SigningKey.generate(curve=SECP256k1)
    bob_vk = bob_sk.get_verifying_key().to_string().hex()

    # Initialize Blockchain
    print("Initializing Advanced Blockchain System...")
    my_blockchain = AdvancedBlockchain()

    # Create and sign a transaction securely
    print("\nCreating and signing transaction from Alice to Bob...")
    tx1 = Transaction(alice_public, bob_vk, 25)
    tx1.sign_transaction(alice_private)
    my_blockchain.add_transaction(tx1)

    # Mine block to record transaction
    print("\nMining block for pending transactions...")
    my_blockchain.mine_pending_transactions("MinerAddressXYZ")

    print(f"\nBlockchain validity status: {my_blockchain.is_chain_valid()}")
    print(f"Total blocks in chain: {len(my_blockchain.chain)}")