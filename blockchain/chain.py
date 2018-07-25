from .block import Block
from .transaction import Transaction
from hashlib import sha256


class Blockchain:
    """Represent a blockchain"""

    def __init__(self):
        """Initialize the block chain."""
        self.ledger = []  # The actual consistent chain
        self.first_block()

    def __str__(self):
        string = ""
        for x in self.ledger:
            string += x.hash + "\n"
        return str(string)

    def first_block(self):
        """Create the first block of the ledger"""
        self.ledger.append(Block(identifier=1, previous_hash=1, proof=100,
                                 transaction=Transaction([], [])))

    def new_block(self, proof, transaction):
        """
        Create a new block and add it to the ledger

        :param proof: Proof of work
        :param transaction: Transaction included in the block
        :return: The new block
        """

        # Build a block
        block = Block(identifier=len(self.ledger) + 1, previous_hash=self.last_block.hash, proof=proof,
                      transaction=transaction)

        # Add to ledger and return the new block
        self.ledger.append(block)
        return block

    def is_valid(self):
        """Determine if the ledger is valid"""

        prev_block = self.ledger[0]
        for i in range(len(self.ledger) - 1):
            i += 1  # Index should start at 1
            current_block = self.ledger[i]

            # Check if the hash pointer of the current block to the previous block
            # matches the hash hof the previous block
            if current_block.dict["previous"] != prev_block.hash:
                return False

            # Check if the proof of work was done
            if not sha256((str(prev_block.dict["proof"]) +
                           str(current_block.dict["proof"])).encode()).hexdigest()[:4] == "0000":
                return False

            # Check if the transaction in the block is valid
            if not current_block.transaction.is_valid(self.ledger[:i]):
                return False

            prev_block = current_block  # assign new previous block

        return True

    @staticmethod
    def proof_of_work(prev_proof):
        """A simple proof of work algorithm"""
        proof = 0
        while not sha256((str(prev_proof) + str(proof)).encode()).hexdigest()[:4] == "0000":
            proof += 1  # increment proof until the first 4 digits are 0000

        return proof

    @property
    def last_block(self):
        """Return the last block of the ledger"""
        return self.ledger[-1]
