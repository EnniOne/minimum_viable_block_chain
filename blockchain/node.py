from blockchain import Blockchain, Transaction
from nacl.signing import SigningKey
from hashlib import sha256
from time import sleep
from threading import Thread
import random


class Node:
    """Represent a Node."""

    def __init__(self, neighbours, unverified_transactions_pool):
        """
        Initialize the Node.

        :param neighbours: Other nodes that take part in the network.
        :param unverified_transactions_pool: Pool of unverified transactions
        """
        self.private_key = SigningKey.generate()
        self.public_key = self.private_key.verify_key
        self.id = sha256(self.public_key.encode()).hexdigest()
        self.name = self.id
        self.blockchain = Blockchain()
        self.neighbours = neighbours
        self.unverified_transactions_pool = unverified_transactions_pool

    def log(self, message):
        """Log a message to stdout, adding this node's identifier"""

        print("[{id}]: {msg}".format(id=self.name, msg=message))

    def mine(self):
        """Mine a new block"""

        try:
            transaction = self.unverified_transactions_pool.pop()
        except IndexError:
            self.log("No transaction new transaction found")
            return False

        self.consensus()  # ensure consensus
        if not transaction.is_valid(self.blockchain.ledger):
            self.log("Transaction invalid")
            return False

        # Get proof of last block
        last_block = self.blockchain.last_block
        last_proof = last_block.dict["proof"]

        proof = self.blockchain.proof_of_work(last_proof)  # compute new proof

        block = self.blockchain.new_block(proof, transaction)  # Add new block to ledger
        self.log("New block forged: {}".format(block.hash))
        return True

    def consensus(self):
        """Replace the blockchain with the longest valid in the network."""

        for node in self.neighbours:
            min_length = len(self.blockchain.ledger)
            current_neighbour_chain = node.blockchain

            # Only replace ledger if the neighbours chain is longer and valid
            if len(current_neighbour_chain.ledger) > min_length and current_neighbour_chain.is_valid():
                self.blockchain.ledger = current_neighbour_chain.ledger


class MiningNode(Node, Thread):
    """Represent a Thread that mines new blocks"""
    def __init__(self, neighbours, unverified_transactions_pool):
        Thread.__init__(self)
        super().__init__(neighbours, unverified_transactions_pool)
        self.daemon = True

    def run(self):
        """Mine and never stop (unless there is an evil alien that demands you to stop. Then stop.)"""
        while True:
            if not self.mine():
                sleep(5)


class WalletNode(Node, Thread):
    """Represent a Person using a simple wallet."""

    def __init__(self, neighbours, unverified_transactions_pool, name):
        Thread.__init__(self)
        super().__init__(neighbours, unverified_transactions_pool)
        self.daemon = True
        self.name = name
        self.friends = []

    def add_friends(self, *friend_nodes):
        for node in friend_nodes:
            self.friends.append(node)

    def new_transaction(self, recipient, amount):
        """Send an amount of coins to a recipient"""
        self.consensus()
        if recipient not in [x.name for x in self.friends]:
            self.log("I don't know {}".format(recipient))
            return False

        if amount > self.balance:
            self.log("I don't have enough money to send {} {} Coins.".format(recipient, amount))
            return False

        self.log("I'm sending {} {} Coins.".format(recipient, amount))

        outputs = []
        spent_outputs = []
        for block in self.blockchain.ledger:
            for output in block.transaction.outputs:  # Sum all earnings
                if output["public_key"] == self.public_key:
                    outputs.append((block.transaction.hash, block.transaction.outputs.index(output)))

            for input in block.transaction.inputs:  # Detect outgoings
                if input["public_key"] == self.public_key:
                    spent_outputs.append((input["hash"], input["output_index"]))

        outputs_for_t_input = []
        for output in outputs:
            if output not in spent_outputs:
                outputs_for_t_input.append(output)
        outputs = outputs_for_t_input

        output_amount = 0
        for b in self.blockchain.ledger:
            for output in outputs:
                if b.transaction.hash == output[0]:
                    output_amount += b.transaction.outputs[output[1]]["amount"]

        for friend in self.friends:
            if friend.name == recipient:
                recipient = friend.public_key

        inputs = []
        for output in outputs:  # Generate inputs
            sig = self.private_key.sign(output[0].encode())
            inputs.append({"hash": output[0], "output_index": output[1],
                           "signature": sig, "public_key": self.public_key})

        outputs = [{"public_key": recipient, "amount": amount}]
        if amount < output_amount:
            outputs.append({"public_key": self.public_key, "amount": output_amount - amount})

        transaction = Transaction(inputs=inputs.copy(), outputs=outputs.copy())
        self.unverified_transactions_pool.append(transaction)

    def go_to_work(self):
        """Add a new generating transaction for 50 coins"""
        self.consensus()
        transaction = Transaction([], [{"public_key": self.public_key, "amount": 50}])
        self.unverified_transactions_pool.append(transaction)

    @property
    def balance(self):
        """Return the Node's balance"""
        self.consensus()  # update
        balance = 0

        outgoings = []

        for block in self.blockchain.ledger:
            for output in block.transaction.outputs:  # Sum all earnings
                if output["public_key"] == self.public_key:
                    balance += output["amount"]

            for input in block.transaction.inputs:  # Detect outgoings
                if input["public_key"] == self.public_key:
                    outgoings.append((input["hash"], input["output_index"]))

        # Sub outgoings
        for block in self.blockchain.ledger:
            for outgoing in outgoings:
                if block.transaction.hash == outgoing[0]:
                    balance -= block.transaction.outputs[outgoing[1]]["amount"]

        return balance

    def run(self):
        while True:
            self.go_to_work()
            self.log("Balance {}".format(self.balance))
            sleep(5)
            recipient = random.choice(self.friends).name
            amount = random.randint(1, 100)
            self.new_transaction(recipient, amount)
