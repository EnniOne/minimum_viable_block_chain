from hashlib import sha256
from time import time


class Block:
    """Inner class to represent a block."""

    def __init__(self, identifier, transaction, proof, previous_hash):
        """
        Initialize a new block that only contains one transaction.

        :param identifier: Identifier of the block
        :param transaction: transaction in this block
        :param proof: proof of work
        :param previous_hash: hash of previous block
        """
        self.id = identifier
        self.transaction = transaction
        self.proof = proof
        self.previous = previous_hash
        self.timestamp = time()

    @property
    def dict(self):
        """Return a sorted dict representing this block"""
        return {"ID": self.id, "transaction": self.transaction.dict, "timestamp": self.timestamp,
                "proof": self.proof, "previous": self.previous}

    @property
    def hash(self):
        """
        Hash this block using sha256
        """
        return sha256(str(self.dict).encode()).hexdigest()
