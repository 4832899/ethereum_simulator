from collections import deque

from numpy import random
from datetime import datetime, timedelta
import logging
import config


class BlockDiscoveriesScheduler:

    def __init__(self):
        self.block_discoveries_queue = deque()
        self.cycles_to_be_executed = []

    def initialize_block_discovery_queue(self):
        if config.simulation_type == 'block_discoveries':
            return self.build_queue_for_number_of_block_discoveries()
        elif config.simulation_type == 'simulation_time':
            return self.build_queue_for_total_simulation_time()

    def build_queue_for_number_of_block_discoveries(self):
        """builds the queue of the times at which the block discoveries should be triggered.
           used when the user opts to run the simulation with a certain number of block discoveries"""

        # this is the time when the simulation started
        start_time = datetime.now()
        logging.info("Simulation started at " + str(start_time))

        #for each of the scheduled block discoveries
        for block_discovery in range(1, config.n_of_block_discoveries+1):

            #draw a value from the Poisson distribution
            block_time = BlockDiscoveriesScheduler.block_discovery_time()

            #add incrementally the block time in seconds to an absolute time
            block_discovery_time = start_time + timedelta(seconds=block_time)
            start_time = block_discovery_time

            #write to the log file when (block_discovery_time),  which  block (block_discovery) will be mined and
            #the block time of that round (block_time)
            logging.info("Block " + str(block_discovery) + " will be mined in " + str(block_time) + " seconds at " +\
                          str(block_discovery_time))

            #append the block number and block discovery time to the queue
            self.block_discoveries_queue.append((block_discovery, block_discovery_time))

            #create a list "cycles_to_be_executed" with the number of block discoveries from 1 to the last.
            #this list is necessary to keep track of how many blocks have already been discovered during the simulation
            self.cycles_to_be_executed = list(range(1, config.n_of_block_discoveries + 1))

        return self.block_discoveries_queue, self.cycles_to_be_executed

    def build_queue_for_total_simulation_time(self):
        """builds the queue of the times at which the block discoveries should be triggered.
           used when the user opts to run the simulation according to a duration time.
           the method calculates how many block discoveries will take place in this time"""

        # this is the time when the simulation started
        start_time = datetime.now()
        logging.info("Simulation started at " + str(start_time))

        #user configuration for the duration of the simulation
        simulation_time = timedelta(seconds=config.simulation_time)

        #keep track of absolute time every time a new block time is added to the events queue
        total_time = timedelta(seconds=0)

        #keep track of the total number of blocks that will be discovered at every mining round
        block_count = 1

        while total_time < simulation_time:

            #draw a value from the Poisson distribution
            block_time = BlockDiscoveriesScheduler.block_discovery_time()

            #add the block time in seconds to the absolute time incrementally
            block_discovery_time = start_time + timedelta(seconds=block_time)

            #the start time of the next mining round
            start_time = block_discovery_time

            #write to the log file when (block_discovery_time),  which  block (block_discovery) will be mined and
            #the block time of that round (block_time)
            logging.info("Block " + str(block_count) + " will be mined in " + str(block_time) + " seconds at " +\
                         str(block_discovery_time))

            total_time += timedelta(seconds=block_time)
            block_count += 1

            #append the block number and block discovery time to the queue
            self.block_discoveries_queue.append((block_count, block_discovery_time))

            #create a list "cycles_to_be_executed" with the number of block discoveries from 1 to the last.
            #this list is necessary to keep track of how many blocks have already been discovered during the simulation
            self.cycles_to_be_executed.append(block_count)

        return self.block_discoveries_queue, self.cycles_to_be_executed

    @staticmethod
    def block_discovery_time():
        """Returns the time for the block discovery according to a Poisson distribution"""
        return int(random.poisson(lam=config.block_discovery_rate, size=1))


