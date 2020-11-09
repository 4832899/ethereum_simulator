import latency_times_config as latencies_config
import numpy as np
import random
import config
from numpy import random as numpy_random

class Msg:

    def __init__(self):
        self.avg_latency = latencies_config.mean_latency_msgs
        self.std_latency = latencies_config.std_latency_msgs
        self.max_pow = latencies_config.max_time_pow_validation
        self.min_pow = latencies_config.min_time_pow_validation
        self.status = latencies_config.STATUS_MSG
        self.get_block_headers = latencies_config.GET_BLOCK_HEADERS_MSG
        self.block_header = latencies_config.BLOCK_HEADERS_MSG
        self.pow_validation = latencies_config.POW_VALIDATION
        self.get_block_bodies = latencies_config.GET_BLOCK_BODIES_MSG
        self.mean_block_transfer = latencies_config.mean_block_transfer
        self.std_block_transfer = latencies_config.std_block_transfer

    def calculate_blockchain_sync_delay(self):
        return self.status_delay() + \
                self.get_block_headers_delay() + \
                self.block_headers_delay() + \
                self.pow_validation_delay() + \
                self.get_block_bodies_delay()

    def calculate_network_delay_for_block_transfer(self):
        return abs(np.random.normal(loc=self.mean_block_transfer,
                                    scale=self.std_block_transfer))

    def generate_one_way_latency(self):
        return abs(np.random.normal(loc=self.avg_latency,
                                    scale=self.std_latency))

    def generate_pow_validation_latency(self):
        return random.uniform(self.max_pow, self.min_pow)

    def status_delay(self):
        if self.status:
            return 2*self.generate_one_way_latency()
        else:
            return 0

    def get_block_headers_delay(self):
        if self.get_block_headers:
            return self.generate_one_way_latency()
        else:
            return 0

    def block_headers_delay(self):
        if self.block_header:
            return self.generate_one_way_latency()
        else:
            return 0

    def pow_validation_delay(self):
        if self.pow_validation:
            return self.generate_pow_validation_latency()
        else:
            return 0

    def get_block_bodies_delay(self):
        if self.get_block_bodies:
            return self.generate_one_way_latency()
        else:
            return 0



