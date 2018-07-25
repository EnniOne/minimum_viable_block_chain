from hashlib import sha256
from nacl.exceptions import BadSignatureError
from time import time


class Transaction:
    """Represent a transaction"""

    def __init__(self, inputs, outputs):
        """
        Initialize a new transaction.

        :param input: input(s) for the transaction. Can be a list or a single input.
        A single input should look like this:
        {"hash": hash_of_referenced_transaction, "output_index": output_index_in_referenced_transaction,
        "signature": sender's signature on 'hash', "public_key": sender's public_key}
        :param output: output(s) for the transaction. Can be a list or a single output. A single output
        should look like this: {"public_key": pub_key of recipient, "amount": amount of transaction}
        """
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = time()

    @property
    def dict(self):
        """Return a dictionary representing this transaction"""
        return {"input": self.inputs, "output": self.outputs}

    @property
    def hash(self):
        """Hash this block using sha256"""
        return sha256((str(self.dict) + str(self.timestamp)).encode()).hexdigest()

    def is_valid(self, ledger):
        """Checks if the transaction is valid"""
        # See transaction as valid if no input is given
        if not self.inputs:
            return True

        # Get amount of outputs
        output_amount = 0
        for output in self.outputs:
            output_amount += output["amount"]

        # Ensure that coins are not spend
        for input in self.inputs:
            for block in ledger:
                if input in block.transaction.inputs:
                    print("Coins were already spent")
                    return False

        # Search for input transaction and verify
        input_amount = 0  # for checking balance
        for input in self.inputs:  # iterate through inputs
            input_found = False
            for block in ledger:  # iterate through blocks
                if input["hash"] == block.transaction.hash:
                    input_found = True
                    try:
                        current_output = block.transaction.outputs[input["output_index"]]
                    except IndexError:
                        print("Output not found")
                        return False  # Fail if output is not found

                    if current_output["public_key"] == input["public_key"]:  # check if input belongs to sender
                        # Verify signature
                        try:
                            current_output["public_key"].verify(input["signature"])
                            input_amount += current_output["amount"]
                            break
                        except BadSignatureError:
                            print("Signature does not match")
                            return False  # Fail if signature doesn't fit
                    else:
                        print("PubKey does not match")
                        return False  # Fail if pubKeys do't match

            if not input_found:
                print("Input not found")
                return False  # Fail if one input is not found

        # Check balance
        if output_amount != input_amount:
            print("Amount does not fit: {0} {1}".format(output_amount, input_amount))
            return False  # Fail if input and output amounts are different

        return True
