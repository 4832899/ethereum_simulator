import logging
import math
import random

import matplotlib

import config
from block import Block
from block_discoveries_scheduler import BlockDiscoveriesScheduler
from block_reception_entry import BlockReceptionEntry
from blockchain_finalization import BlockchainFinalization
from miner_election import MinerElection
from network import Network
from utils import log

matplotlib.use('TkAgg')

class Simulator:

    def __init__(self):
        self.miner = MinerElection()
        self.network = None
        self.block_discoveries_queue = None
        self.next_cycle = None
        self.next_block_discovery_time = None
        self.cycles_to_be_executed = []
        self.uncles_counter = 0
        self.build_network()
        self.build_queue_of_events()
        self.n_confirmation_to_reach_consensus = config.n_confirmations_to_reach_consensus

    def build_network(self):
        """Initialize the network"""
        g = Network()
        g.create_peers()
        g.connect_peers()
        #g.draw_network()
        if config.perc_failing_nodes:
            g.fail_nodes()
        logging.info("Active peers in the network: " + str(g.graph.number_of_nodes()))
        self.network = g.graph

    def build_queue_of_events(self):
        scheduler = BlockDiscoveriesScheduler()
        self.block_discoveries_queue, self.cycles_to_be_executed = scheduler.initialize_block_discovery_queue()

    def run(self):
        # log the number of block discoveries
        block_discoveries = len(self.block_discoveries_queue)
        logging.info("Block discoveries " + str(block_discoveries))

        # while there are blocks to be mined in the queue
        while self.block_discoveries_queue:

            # if running the simulation until a certain n of confirmations is reached
            if self.n_confirmation_to_reach_consensus:
                # take the most powerful miner in the network as reference
                peer_1 = self.network.nodes[1]['data']

                #run the simulator until a certain number of confirmations for a block is reached
                _, canonical = peer_1.blockchain.get_the_canonical_blockchain()
                n_blocks_in_canonical_chain = len(canonical)
                n_confirmations_so_far = n_blocks_in_canonical_chain - self.uncles_counter
                if n_confirmations_so_far > self.n_confirmation_to_reach_consensus + 1:
                    logging.info(str(self.n_confirmation_to_reach_consensus) + " confirmations reached...")
                    logging.info(str(self.uncles_counter) + " uncles")
                    return self.uncles_counter, self.network

            # pop the cycle number and the exact time when the block is to be discovered
            cycle, block_discovery_time = self.block_discoveries_queue.popleft()
            last_cycle = self.cycles_to_be_executed[-1]

            #if block discoveries queue is not empty yet or it s the last cycle
            if self.block_discoveries_queue or cycle == last_cycle:

                # if it's the last cycle, just trigger the block discovery of the last block and finish the simulation
                if cycle == last_cycle:
                    self.trigger_block_discovery(block_discovery_time)

                # if it's not the last cycle yet, keep track of the next cycle and corresponding block discovery time
                else:
                    self.next_cycle, self.next_block_discovery_time = self.block_discoveries_queue[0]
                    self.cycles_to_be_executed.remove(cycle)
                    self.trigger_block_discovery(block_discovery_time)

        return self.uncles_counter, self.network

    def trigger_block_discovery(self, block_discovery_time):

        # Peer is elected to mine the block in this round
        block_miner_id = self.miner.election(self.network)
        block_miner = self.network.nodes[block_miner_id]['data']

        # appending mined block to miner's own ledger
        # 1. compute the last block of the longest chain or best chain according to ghost algorithm,
        # i.e., the block that will be referenced as the previous block in the newly mined block
        blockchain = block_miner.blockchain
        blockchain_finalization = BlockchainFinalization()
        block_to_extend = blockchain_finalization.apply_blockchain_finalization(blockchain)
        last_block = block_to_extend.data

        # 2. construct the mined block
        # determine block depth
        new_block_depth = last_block.depth + 1
        # determine block ID
        new_block_number = last_block.id + 1
        # create the block object
        block = Block(id=new_block_number,
                      timestamp=block_discovery_time,
                      previous_block=last_block,
                      beneficiary_miner_id=block_miner_id,
                      depth=new_block_depth)

        # 3. append it to the miner's blockchain
        block_miner.blockchain.append(block)

        # 4. register the mined block into miner's block reception history
        block_reception_entry = BlockReceptionEntry(block=block,
                                                    received_from='self-mined',
                                                    received_at=block_discovery_time)
        block_miner.blocks_received_counter += 1
        label = str(block_miner.blocks_received_counter) + ' self-mined'
        block_miner.blocks_reception_history[label] = block_reception_entry

        # Finally, propagate the block to the network
        self.propagate_block(sender_id=block_miner.id,
                             block=block,
                             transmission_timestamp=block_discovery_time)

    def propagate_block(self, sender_id, block, transmission_timestamp):

        # before the block is propagated to the network, must do some bookkeeping
        # 1. build a list of visited peers, which stores their status, namely the two types of nodes in the gossip protocol:
        # susceptible (visited is False) and infected (visited is True)
        peer_received_the_block = [False] * config.n_of_peers

        queue_of_peers_waiting_to_transmit_block = list()
        queue_entry = (sender_id, transmission_timestamp)
        queue_of_peers_waiting_to_transmit_block.append(queue_entry)

        while queue_of_peers_waiting_to_transmit_block:
            sender_id, reception_timestamp = queue_of_peers_waiting_to_transmit_block.pop(0)

            # Keeping track of uncle formation:
            # detect if a block creation of the same depth as a block still in propagation
            # occurs. When this happens, an uncle is created.
            if reception_timestamp >= self.next_block_discovery_time and \
               self.next_cycle in self.cycles_to_be_executed and \
               self.block_discoveries_queue:
                cycle, block_discovery_time = self.block_discoveries_queue.popleft()
                if self.block_discoveries_queue:
                    self.next_cycle, self.next_block_discovery_time = self.block_discoveries_queue[0]
                logging.info("Uncle formed at depth " + str(cycle) + " at " + str(block_discovery_time))
                self.uncles_counter += 1
                self.cycles_to_be_executed.remove(cycle)

            # acquire the neighbors of sender peer
            sender = self.network.nodes[sender_id]['data']
            neighbors = [n for n in self.network.neighbors(sender_id)]

            #if peer is parity, it propagates the block to the square root of its neighbors (randomly chosen)
            if sender.client == 'parity':
                nbr_neighbors = len(neighbors)
                neighbors_to_receive_block = int(math.sqrt(nbr_neighbors))
                neighbors = random.choices(neighbors,
                                           k=neighbors_to_receive_block)

            sender.advertise_and_transfer_block(self.network, block, neighbors, peer_received_the_block,
                                                queue_of_peers_waiting_to_transmit_block, reception_timestamp)

if __name__ == '__main__':
    log.init_logger()
    sim = Simulator()
    uncles_counter, _ = sim.run()
    print("Uncles", str(uncles_counter))
