# Mean and std deviation for block transfer delay
mean_block_transfer = 0.5
std_block_transfer = 0.2

# Mean  and std deviation for msg latency
mean_latency_msgs = 0.3 #reported peer latency in Ethereum is 0.171 and we consider 0.129 as time the peer takes
                        #to process the message internally and send a response
std_latency_msgs = 0.1

#Time interval to execute PoW validation
max_time_pow_validation = 0.2
min_time_pow_validation = 0.1

# Status message contains the network id, hash of genesis block, fork id.
# It determines if the clients are in the same network with same genesis block
# and which peer has the most outdated blockchain
STATUS_MSG = True

# Peer with outdated blockchain will request the block headers first through this message
GET_BLOCK_HEADERS_MSG = True

# Peer checks if  received headers have valid PoW. If so, it proceeds sending the next BLOCK_HEADERS_MSG
POW_VALIDATION = True

# Peer receives the block headers
BLOCK_HEADERS_MSG = True

# Peer requests the block bodies
GET_BLOCK_BODIES_MSG = True

# BLOCK_BODIES_MSG: Peer receives the block bodies (this latency is simulated by the block transfer delay in msg_exchange)


