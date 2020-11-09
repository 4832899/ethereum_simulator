from datetime import datetime
import random

class Block:

    def __init__(self,
                 id,
                 timestamp: datetime,
                 previous_block=None,
                 beneficiary_miner_id: int = None,
                 depth: int = 0):

        self.id = id
        self.timestamp = timestamp
        self.previous_block = previous_block
        self.beneficiary_miner_id = beneficiary_miner_id
        self.depth = depth

    def __lt__(self, other_block):
        """This function implements the 'less equal' comparison between two blocks.
           It returns true, if self's creation time is more recent than the creation time of other_block"""
        return self.timestamp < other_block.timestamp

    def __str__(self):
        """The string representation of a block.
            It returns the block ID and the miner ID who created the block."""
        return "Block " + str(self.id) + \
               " (Miner " + str(self.beneficiary_miner_id) + ')'
