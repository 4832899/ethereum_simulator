import random
from itertools import permutations

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np
import logging
from utils import log
import config
from peer import Peer
from utils import util


class Network:
    """This class builds a random connected graph that represents the peer-to-peer network."""

    def __init__(self):
        self.n_peers = config.n_of_peers
        self.degrees_of_connectivity_file = config.degrees_of_connectivity_file
        self.n_peers_using_geth_client = int(config.geth_perc_clients_in_network * self.n_peers)
        self.n_peers_using_parity_client = int(config.parity_perc_clients_in_network * self.n_peers)
        self.seed = config.seed
        self.perc_failing_nodes = config.perc_failing_nodes
        self.geth_peers = {}
        self.parity_peers = {}
        self.graph = nx.Graph()

    def create_peers(self) -> None:
        """ Creating the peers for the network"""

        #create Geth peers
        for peer_id in range(1, self.n_peers_using_geth_client + 1):
            geth_peer = Peer(id=peer_id, client='geth')
            self.graph.add_node(peer_id, data=geth_peer)
            self.geth_peers[peer_id] = geth_peer

        #create Parity peers
        for peer_id in range(self.n_peers_using_geth_client+1, self.n_peers + 1):
            parity_peer = Peer(id=peer_id, client='parity')
            self.graph.add_node(peer_id, data=parity_peer)
            self.parity_peers[peer_id] = parity_peer

    def calculate_moments_of_degree_of_connectivity(self):
        """Using a sample of the real degrees of connectivity
           from Ethereum. Data acquired from Ethereum explorer https://ethstats.net/"""
        degrees = pd.read_csv(self.degrees_of_connectivity_file)
        mean = int(degrees.mean())
        std = int(degrees.std())
        if not config.other_network_size:
            logging.info("Mean degree of connectivity of the network is " + str(mean))
            logging.info("Standard deviation for the degree of connectivity of the network is " + str(std))
        return mean, std

    def connect_peers(self) -> None:
        """Connect peers randomly according to avg degree"""

        avg_degree, std_degree = self.calculate_moments_of_degree_of_connectivity()

        if config.analysis_different_network_sizes:
            n_of_peers = config.n_of_peers
            other_network_size = config.other_network_size
            ratio = other_network_size/n_of_peers
            avg_degree = int(avg_degree*ratio)
            std_degree = int(std_degree*ratio)
            logging.info("Mean degree of connectivity of the network is " + str(avg_degree))
            logging.info("Standard deviation for the degree of connectivity of the network is " + str(std_degree))

        #connect Geth peers
        for peer_id in self.geth_peers.keys():
            degree = np.random.normal(loc=avg_degree,
                                      scale=std_degree)
            self.add_edges_until_degree_reached(peer_id=peer_id, n_neighbors=degree)

        #connect Parity peers
        for peer_id in range(self.n_peers_using_geth_client+1, self.n_peers + 1):
            degree = np.random.normal(loc=avg_degree,
                                      scale=std_degree)
            self.add_edges_until_degree_reached(peer_id=peer_id, n_neighbors=degree)

    def connect_powerful_miners(self) -> None:
        """Connect powerful miners among themselves.
            Implemented, but not being used"""
        n_miners = util.get_number_powerful_miners()
        edges = list(permutations(range(1, n_miners+1), 2))
        for edge in edges:
            self.add_connection(edge[0], edge[1])


    def add_edges_until_degree_reached(self, peer_id: int, n_neighbors: int) -> None:
        """Connect one peer to other peers until the maximum number of neighbors
        is reached"""
        random.seed(self.seed)
        neighbor_counter = len(list(self.graph.neighbors(peer_id)))
        while neighbor_counter < n_neighbors:
            neighbor = random.randint(1, self.n_peers)
            if neighbor == peer_id:
                continue
            neighbor_counter = self.add_connection(peer_id, neighbor, neighbor_counter)

    def add_connection(self, peer_id, neighbor_id, neighbor_counter) -> int:
        """Add edge from peer i to neighbor"""
        self.graph.add_edge(peer_id, neighbor_id)
        print("Connecting peer ID", str(peer_id), "to peer ID", str(neighbor_id))
        neighbor_counter += 1
        return neighbor_counter

    def list_all_edges(self):
        """Show all connections in the graph"""
        for peer in range(1, self.n_peers+1):
            print("Peer", str(peer), "has ", end='')
            counter = self.count_neighbors(peer)
            print(str(counter), "neighbours")

    def count_neighbors(self, peer_id: int) -> int:
        """Count number of neighbors of peer i"""
        return len([n for n in self.graph.neighbors(peer_id)])

    def list_neighbors_of_peer(self, peer_id: int) -> None:
        """Show neighbors of peer i"""
        n_neighbors = self.count_neighbors(peer_id)
        print("Peer", str(peer_id), "has ", n_neighbors)

        for n, neighbor in enumerate(self.graph.neighbors(peer_id)):
            print("Neighbor", n, '=>', str(neighbor))

    def calc_avg_connectivity_degree_of_network(self) -> int:
        """ Calculate the average degree of connectivity of the network"""
        total = 0
        for peer in range(1, self.n_peers+1):
            total += self.count_neighbors(peer)
        return int(total/self.n_peers)

    def draw_network(self) -> None:
        plt.figure(figsize=(8, 6))
        nx.draw(self.graph, node_size=10, node_color='black', with_labels=True)
        plt.title('Graph Representation', size=15)
        plt.show()

    def fail_nodes(self):
        n_failing_nodes = int((self.perc_failing_nodes/100)*self.n_peers)
        print("Number of failing nodes is", n_failing_nodes)
        failing_nodes = set()
        while len(failing_nodes) < n_failing_nodes:
            fail_node = random.randint(1, self.n_peers)
            if self.graph.has_node(fail_node):
                print("Setting node", str(fail_node), "as failing node")
                self.graph.remove_node(fail_node)
                failing_nodes.add(fail_node)
            else:
                continue


