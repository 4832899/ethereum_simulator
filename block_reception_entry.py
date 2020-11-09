

class BlockReceptionEntry:

    def __init__(self, block, received_from, received_at):
        self.block = block
        self.received_from = received_from
        self.received_at = received_at

    def __str__(self):
        event = str(self.block) + \
                ", mined at " + str(self.block.timestamp) +\
                " received from peer " + \
                str(self.received_from) + " at " + str(self.received_at)
        return event