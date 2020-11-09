import sys

##############################################################################
# Simulation Settings
##############################################################################

#block time
block_discovery_rate = 13.24

#Specify if the simulation should be executed according to 'block_discoveries' or 'simulation_time'
simulation_type = 'block_discoveries'

#If simulation_type = 'block_discoveries', set the number of of block discoveries that should occur
#in one simulation run

n_of_block_discoveries = 2

#If simulation_type = 'simulation_time', set the simulation duration in seconds
simulation_time = 86400  #24 hours

##############################################################################
# Network Settings
# #######################################################

#number_of_peers
n_of_peers = 8703

#degrees of connectivity data from from Ethereum exlorer https://ethstats.net/
degrees_of_connectivity_file = r'input_parameters/peers_degree_of_connectivity.csv'

#random number generator uses a seed
#seed is useful to make the network topology replicable
seed = 234

##############################################################################
# Geth Client Settings
##############################################################################
geth_perc_clients_in_network = 0.809 #fraction of Geth clients in the p2p network

##############################################################################
# Parity Client Settings
##############################################################################
parity_perc_clients_in_network = 0.191 #fraction of Parity clients in the p2p network

#######################################
# Miner Election Settings
#######################################

#Set to True to use the network hashrate distribution in the file input_parameters/hashrate-dist-2019.csv
#Set to False to use a plain simple random selection for the miner election
use_hash_power_dist = True
#Set to True to simulate that one pool control 100% hashrate in the network
one_pool = False

#network hashrate distribution file
hash_power_distribution_file = r'input_parameters/hashrate-dist.csv'

#######################################
# Block Finalization Settings
#######################################

#Specify block_finalization as 'ghost' or 'longest_chain_rule'
block_finalization = 'ghost'

#######################################
# Anaylsis Settings
#######################################

analysis_different_network_sizes = False

other_network_size = 1000000

# percentage of failing nodes
perc_failing_nodes = 0 #20

#directory to save the simulation results
dir_sim_output = r"simulation_data"

#######################################
# Results of Simulations Settings
#######################################

#results of simulation will be stored in this folder
dir_simulation_results = r'simulation_data'

#######################################
# Logs Settings
#######################################
dir_simulation_log = r'logs'

#######################################
# Consensus Setting
#######################################
n_confirmations_to_reach_consensus = 0 #must be set to zero if not interested in analyzing this metric
