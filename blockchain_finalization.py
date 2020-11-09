import operator
import random

import config


class BlockchainFinalization:

    def __init__(self):
        self.type = config.block_finalization

    def apply_blockchain_finalization(self, blockchain):
        if self.type == 'ghost':
            return self.apply_ghost_to_find_best_chain(blockchain.ledger)

        elif self.type == 'longest_chain_rule':
            _, longest_chain = blockchain.get_the_canonical_blockchain()
            block_label = longest_chain[-1]
            block = blockchain.ledger.get_node(block_label)
            return block

    @staticmethod
    def apply_ghost_to_find_best_chain(tree):
        """GHOST is Ethereum's block finalization. The heaviest subtree is extended,
            i.e. the tree with most computational work: uncles are taken into consideration"""
        # Start with the genesis
        next_node_identifier = "Block 0 (Miner 0)"
        while True:
            sizes = BlockchainFinalization.get_n_nodes_in_subtrees(next_node_identifier, tree)
            # If node has no more children
            if not sizes:
                return tree.get_node(next_node_identifier)
            next_node_identifier = BlockchainFinalization.pick_heaviest_subtree(sizes)

    @staticmethod
    def pick_heaviest_subtree(sizes):
        """Sort the nodes by heaviest subtree and choose the heaviest one for that block height.
            Go to next lower height. """
        sizes.sort(key=operator.itemgetter(1), reverse=True)
        next_node_identifier = sizes[0][0]
        return next_node_identifier

    @staticmethod
    def get_n_nodes_in_subtrees(next_node_identifier, tree):
        """Calculate the number of nodes in subtree of node "next_node_identifier" """
        sizes = []
        for node in tree.children(next_node_identifier):
            node_size = node.identifier, tree.subtree(node.identifier).size()
            sizes.append(node_size)
        return sizes

