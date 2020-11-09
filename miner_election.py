import config
import pandas as pd
from random import choices
import random

class MinerElection:
    """This class elects the peer that will propose the block in the cycle miner"""

    def __init__(self):
        self.n_peers = config.n_of_peers
        self.hash_rate_dist = config.hash_power_distribution_file
        self.weighted = config.use_hash_power_dist
        self.one_pool = config.one_pool


    def election(self, network):
        """Elect the next miner that will find a block"""
        if self.weighted:
            return self.weighted_election(network)
        elif self.one_pool:
            return self.one_pool_election()
        else:
            return self.simple_election()

    def weighted_election(self, network):
        """Pick the next peer according to the hashrate distribution of the network
            (https://www.etherchain.org/charts/topMiners)"""

        hashrates = self.get_hashpower_dist_from_input()
        most_powerful_miners = len(hashrates)
        total_hashpower_perc = sum(hashrates)
        hashrates = self.build_hashrate_dist_whole_network(hashrates, most_powerful_miners, total_hashpower_perc, network)
        population = list(network.nodes)
        # pick the next miner to find a new block through a weighted selection based on the hashrate distribution
        block_miner_id = choices(population=population,
                                 weights=hashrates)[0]
        return block_miner_id

    def simple_election(self):
        """A simple random selection"""
        return random.randint(1, self.n_peers)

    def one_pool_election(self):
        """One pool detains 100% oh hashrate"""
        return 1

    def build_hashrate_dist_whole_network(self, hashrates, most_powerful_miners, total_hashpower, network):
        """Distribute the remaining hashpower (apart from that in input list) to the rest of peers"""
        hashrate_rest = 1 - total_hashpower
        # the rest of the miners have in average the following hashrate
        n_peers_in_network = len(list(network.nodes))
        hashrate_each = hashrate_rest / (n_peers_in_network - most_powerful_miners)
        # build a list of hashrates of all peers in the network
        hashrates = hashrates + [hashrate_each] * (n_peers_in_network - most_powerful_miners)
        return hashrates

    def get_hashpower_dist_from_input(self):
        """Get the hashpower distribution of input file"""
        hashrates = pd.read_csv(self.hash_rate_dist)
        hashrates = hashrates.apply(lambda x: x / 100)
        hashrates = hashrates['hashrates'].tolist()
        return hashrates
