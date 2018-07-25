from blockchain import Node, MiningNode, WalletNode, Transaction
from time import sleep

# Globals
unverified_transactions_pool = []
all_nodes = []


def blockchain_demo():
    # Create nodes and append them
    first_node = Node(all_nodes, unverified_transactions_pool)
    second_node = Node(all_nodes, unverified_transactions_pool)
    all_nodes.append(first_node)
    all_nodes.append(second_node)

    # Create new creating transaction and mine
    t1 = Transaction(inputs=[], outputs=[{"public_key": first_node.public_key, "amount": 100}])
    unverified_transactions_pool.append(t1)
    second_node.mine()

    # Add new valid transaction and mine
    sig = first_node.private_key.sign(t1.hash.encode())
    t2 = Transaction(inputs=[{"hash": t1.hash, "output_index": 0, "signature": sig, "public_key": first_node.public_key}],
                     outputs=[{"public_key": second_node.public_key, "amount": 100}])
    unverified_transactions_pool.append(t2)
    second_node.mine()

    first_node.consensus()
    print("\n")
    print(first_node.blockchain)
    print(first_node.blockchain.ledger == second_node.blockchain.ledger)


def wallet_demo():
    # Alice and bob both have a wallet
    alice = WalletNode(all_nodes, unverified_transactions_pool, "Alice")
    bob = WalletNode(all_nodes, unverified_transactions_pool, "Bob")
    all_nodes.append(alice)
    all_nodes.append(bob)
    alice.add_friends(bob)
    bob.add_friends(alice)

    # Add transactions
    t1 = Transaction(inputs=[], outputs=[{"public_key": alice.public_key, "amount": 100}])
    t2 = Transaction(inputs=[], outputs=[{"public_key": alice.public_key, "amount": 100}])
    unverified_transactions_pool.append(t1)
    unverified_transactions_pool.append(t2)

    # Let the mining begin
    bob.mine()
    alice.mine()
    sig_t1 = alice.private_key.sign(t1.hash.encode())
    sig_t2 = alice.private_key.sign(t2.hash.encode())
    t3 = Transaction(inputs=[{"hash": t1.hash, "output_index": 0, "signature": sig_t1, "public_key": alice.public_key},
                             {"hash": t1.hash, "output_index": 0, "signature": sig_t2, "public_key": alice.public_key}],
                     outputs=[{"public_key": bob.public_key, "amount": 150},
                              {"public_key": alice.public_key, "amount": 50}])
    unverified_transactions_pool.append(t3)
    bob.mine()
    bob.new_transaction("Alice", 20)
    alice.mine()
    alice.new_transaction("Bob", 35)
    bob.mine()
    assert alice.blockchain.ledger == bob.blockchain.ledger
    print(alice.balance)  # alice should have 35 Coins now
    print(bob.balance)  # bob should have 165


def thread_demo():
    # 3 Friends
    alice = WalletNode(all_nodes, unverified_transactions_pool, "Alice")
    bob = WalletNode(all_nodes, unverified_transactions_pool, "Bob")
    charlie = WalletNode(all_nodes, unverified_transactions_pool, "Charlie")
    alice.add_friends(bob, charlie)
    bob.add_friends(alice, charlie)
    charlie.add_friends(alice, bob)
    all_nodes.append(alice)
    all_nodes.append(bob)
    all_nodes.append(charlie)

    # Generate 5 mining nodes
    for i in range(3):
        n = MiningNode(all_nodes, unverified_transactions_pool)
        all_nodes.append(n)

    # Start everything
    for n in all_nodes:
        n.start()
