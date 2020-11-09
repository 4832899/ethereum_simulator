from datetime import datetime
from block import Block
from treelib import Tree
from collections import OrderedDict

class Blockchain:

    def __init__(self):
        """Initialize a new blockchain by appending the genesis block to it"""
        genesis_block = Block(id=0,
                              beneficiary_miner_id=0,
                              timestamp=datetime.now())
        self.ledger = Tree()
        self.ledger.create_node("Block 0 (Miner 0)", "Block 0 (Miner 0)", data=genesis_block)


    def append(self, block: Block) -> None:
        """Append an incoming block to the blockchain"""

        #if block is the first to be appended after the genesis
        if self.ledger.depth == 0:
            self.ledger.create_node(tag=str(block),
                                    identifier=str(block),
                                    parent="Block 0 (Miner 0)",
                                    data=block)
        else:
            self.ledger.create_node(tag=str(block),
                                    identifier=str(block),
                                    parent=str(block.previous_block),
                                    data=block)

    def get_tip_blockchain(self):
        """Locate the last block in the canonical blockchain"""
        try:
            _, canonical_blockchain = self.get_the_canonical_blockchain()
            block_label = canonical_blockchain[-1]
            return self.ledger.get_node(block_label).data
        except:
            print("Tip of the blockchain could not be found.")

    def get_the_canonical_blockchain(self):
        blockchain_fork_lengths = self.order_blockchain_forks_per_length()
        ordered_lengths = OrderedDict(sorted(blockchain_fork_lengths.items()))
        fork_length, canonical_blockchain = ordered_lengths.popitem()
        return fork_length, canonical_blockchain

    def order_blockchain_forks_per_length(self):
        blockchain_path_lengths = {}
        for path in self.ledger.paths_to_leaves():
            blockchain_path_lengths[len(path)] = path
        return blockchain_path_lengths

    def get_number_of_uncles_in_blockchain(self):
        number_blocks_in_canonical_blockchain, _ = self.get_the_canonical_blockchain()
        total_blocks_in_whole_blockchain = self.ledger.size()
        return total_blocks_in_whole_blockchain - number_blocks_in_canonical_blockchain

    def get_percentage_of_uncles_in_blockchain(self):
        number_of_uncles = self.get_number_of_uncles_in_blockchain()
        total_blocks_in_whole_blockchain = self.ledger.size()
        return round(number_of_uncles/total_blocks_in_whole_blockchain, 2)

    def __str__(self):
        """Draw the blockchain"""
        return self.ledger.to_json()
