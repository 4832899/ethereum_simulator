import collections
from collections import deque
from datetime import timedelta

from block_reception_entry import BlockReceptionEntry
from blockchain import Blockchain
from msg_exchange import Msg


class Peer:

    """This class models the peer/client """

    def __init__(self, id, client):
        self.id = id                    # the integer identifying the peer.
        self.hash_power = 0             # hash power is assigned according to data from [ethstats.org]
        self.client = client
        self.messages_delay = Msg()
        self.blockchain = Blockchain()  # local copy of the blockchain
        self.blocks_reception_history = collections.OrderedDict()
        self.blocks_received_counter = 0

    def __str__(self):
        return "Node " + str(self.id) + " contains " + str(self.blockchain)

    def block_is_not_requested(self, block):
        """Check if the block being advertised should be requested.
        In the text, it s referred as Verification of Block Advertisements"""

        # do not request if the block being advertised was mined by the peer himself
        if block.beneficiary_miner_id == self.id:
            return True

        # do not request if block is already part of the blockchain
        blockchain_contains_the_block = self.blockchain.ledger.get_node(block)
        if blockchain_contains_the_block:
            return False

        # do not request, if block's depth is more than 7 generations older than last block
        # it cannot be included as uncle in new block, therefore do not request it
        # (when uncles are requested, they are not included in the chain, just recorded)
        else:
            last_block = self.get_tip_blockchain()
            if block.depth < last_block.depth - 7:
                return True
            else:
                return False

    def get_tip_blockchain(self):
        """Locate the last block in the blockchain.
            This method is used to check if a block being advertised should be requested or not."""
        try:
            # obtain the canonical blockchain (the one fork considered "the blockchain" among
            # the peers in the P2P network)"
            _, canonical_blockchain = self.blockchain.get_the_canonical_blockchain()

            # retrieve the last block of the canonical blockchain
            block_label = canonical_blockchain[-1]
            block = self.blockchain.ledger.get_node(block_label).data
            return block
        except:
            print("Tip of the blockchain could not be accessed.")

    def advertise_and_transfer_block(self, network, block, neighbors, peer_received_the_block,
                                     queue_of_peers_waiting_to_transmit_block, reception_timestamp):
        # if peer is geth, it propagates the block to all of its neighbors
        for neighbor_id in neighbors:

            # if the neighbor still did not receive
            if not peer_received_the_block[neighbor_id - 1]:

                # mark peer as having received the block
                peer_received_the_block[neighbor_id - 1] = True

                # locating neighbor in the network
                neighbor = network.nodes[neighbor_id]['data']

                # simulating the response of the neighbor to the block advertisment
                # check if neighbor requests the block or not
                if neighbor.block_is_not_requested(block):
                    continue

                # block is requested
                else:
                    # block is transferred to the neighbor. He returns the transmission timestamp, which
                    # is the time he receives the block added to all delays (block transfer delay, network delay,
                    # sync messages delay). This transmission timestamp is effectively the time when the peer
                    # transmits the block to his own neighbors
                    transmission_timestamp = self.transfer_block(receiver_id=neighbor_id,
                                                                   block=block,
                                                                   transmission_time=reception_timestamp,
                                                                   network=network)

                    # adding the peer that just received the block to the queue of peers waiting to transmit
                    # the block
                    queue_of_peers_waiting_to_transmit_block.append((neighbor_id, transmission_timestamp))


    def transfer_block(self, receiver_id, block, transmission_time, network):
        """Transfer the received block to the neighbors"""

        receiver = self.record_block_reception_in_history(block, network, receiver_id, transmission_time)

        # uncomment the following line to see the which block is being transferred to which peer
        # during the course of the simulation
        print("Node", str(receiver_id), "received block", str(block.id))

        # add the block to the blockchain
        self.synchronize_the_blockchain(block, receiver)

        # Comment/Uncomment this line to hide/see the evolution of each peer's blockchains during the simulation
        #print("Peer", str(receiver.id))
        #receiver.blockchain.ledger.show()

        forward_time = self.calculate_delay_to_relay_the_block(transmission_time)
        return forward_time

    def synchronize_the_blockchain(self, block, receiver):
        """Appending the received block to the peer's blockchain.
           If a peer receives a block whose depth is higher than the peer's last block,
           transfer all missing  blocks to the peer"""

        # check which previous blocks (blocks before the received block) are missing
        parent = block.previous_block

        if not receiver.blockchain.ledger.contains(str(parent)):

            # build a queue with missing blocks
            blocks_missing = deque()

            #add the block itself to queue
            blocks_missing.append(block)

            # add the previous blocks to the queue
            while not receiver.blockchain.ledger.contains(str(parent)):
                blocks_missing.append(parent)
                parent = parent.previous_block

            # transfer the missing blocks to the receiving peer's blockchain
            while blocks_missing:
                try:
                    previous_block = blocks_missing.pop()
                    receiver.blockchain.append(previous_block)
                except:
                    print("error in syncing")
                    pass

        # no previous blocks are missing, simply transfer the block
        elif receiver.blockchain.ledger.contains(str(parent)) and not receiver.blockchain.ledger.contains(str(block)):
            receiver.blockchain.append(block)

    def calculate_delay_to_relay_the_block(self, transmission_time):
        """Calculate the time when the block should be forwarded to next peer.
           The time delay caused by network and blockchain synchronization message exchanges is taken into account"""
        forward_time = transmission_time + timedelta(seconds=self.messages_delay.calculate_blockchain_sync_delay()) + \
                       timedelta(seconds=self.messages_delay.calculate_network_delay_for_block_transfer())
        return forward_time

    def record_block_reception_in_history(self, block, network, receiver_id, transmission_time):
        # create the entry
        block_reception_entry = BlockReceptionEntry(block=block,
                                                    received_from=self.id,
                                                    received_at=transmission_time)
        #locate the peer in the network
        receiver = network.nodes[receiver_id]['data']

        #save the entry
        receiver.blocks_received_counter += 1
        receiver.blocks_reception_history[self.blocks_received_counter] = block_reception_entry
        return receiver
