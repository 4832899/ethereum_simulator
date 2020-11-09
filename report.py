import logging
import os
import statistics as stats
from datetime import timedelta

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config
import latency_times_config as latency
from main import Simulator
from utils import log


class Report:

    def __init__(self):
        self.total_n_peers = config.n_of_peers
        self.dir_simulation_results = config.dir_simulation_results


    def collect_block_propagation(self, block_times):

        logging.info("Running simulator with different block times to capture the block propagation times")

        # running 100 simulations for each block time
        config.n_of_block_discoveries = 100

        for block_time in block_times:

            logging.info("Simulator Run for Block time " + str(block_time))

            # adjusting the block propagation latencies to reflect the block time.
            # The longer the block time, the more transactions can be added to a block,
            # hence the increase in block size and the longer network transmission and PoW validation times.
            # Note that there is a discussion that higher block sizes cause higher propagation times and
            # some miners would tend to create smaller blocks to decrease the probability of mining
            # a stale block. Here, we do not consider this scenario.
            # We consider the latencies to be proportional to the real block time as of October 2020 (13.24)

            ratio = block_time/13.24

            latency.mean_block_transfer = 0.5*ratio
            latency.std_block_transfer = 0.1*ratio

            # Mean  and std deviation for msg latency do not change because it does not depend
            # on block size. Shown here for visualization purposes
            latency.mean_latency_msgs = 0.3
            latency.std_latency_msgs = 0.1

            # Time interval to execute PoW validation
            latency.max_time_pow_validation = 0.2*ratio
            latency.min_time_pow_validation = 0.1*ratio

            # run the simulation for a specific block time
            config.block_discovery_rate = block_time
            sim = Simulator()
            _, network = sim.run()

            # collect the times to receive each block from all peers in this run
            block_reception_times = []
            for peer_id in network.nodes:
                peer = network.nodes[peer_id]['data']

                for entry in peer.blocks_reception_history.values():
                    block_mined_at = entry.block.timestamp
                    block_received_at = entry.received_at
                    time_to_receive_block = block_received_at - block_mined_at
                    time_to_receive_block_in_secs = time_to_receive_block.total_seconds()
                    block_reception_times.append(time_to_receive_block_in_secs)

            #save  the collected times to receive a block for block time N in a CSV file for posterior analysis
            path = os.path.join(self.dir_simulation_results, "block_time_" + str(block_time) + "_block_reception_times.txt")
            logging.info("Saving block propagation times for block time " + str(block_time) + " in " + path)
            with open(path, "w") as f:
                for t in block_reception_times:
                    f.write(str(t) + "\n")

            #Save the statistic in the log file for this run
            logging.info("Mean propagation time: ")
            logging.info(stats.mean(block_reception_times))

            logging.info("Standard deviation: ")
            logging.info(stats.stdev(block_reception_times))

            logging.info("First received in ")
            logging.info(min(block_reception_times))

            logging.info("Last received in ")
            logging.info(max(block_reception_times))

            logging.info("Median: ")
            logging.info(stats.median(block_reception_times))

    def plot_block_propagation(self, block_times):
        n_bins = list(np.arange(0, 50, 0.00001))
        fig, ax = plt.subplots(figsize=(8, 6))

        font = {'family': 'sans-serif',
               'weight': 'bold',
               'size': 16}
        matplotlib.rc('font', **font)
        plt.style.use('ggplot')

        for block_time in block_times:
            simulation_filename = "block_time_" + str(block_time) + "_block_reception_times.txt"
            path = os.path.join(self.dir_simulation_results, simulation_filename)
            block_reception_times = pd.read_csv(path).values.tolist()
            block_reception_times = [item for sublist in block_reception_times for item in sublist]

            print(block_reception_times)

            curve_label = str(block_time)
            n, bins, patches = ax.hist(block_reception_times,
                                       n_bins,
                                       histtype='step',
                                       density=True,
                                       cumulative=True,
                                       label=curve_label)
        ax.grid(True)
        ax.legend(loc="center right", title='Block Time [s]')
        ax.set_title('Block Propagation')
        ax.set_xlabel('Elapsed time since block creation [s]')
        ax.set_ylabel('CDF')
        plt.show()



    def collect_stats_for_number_of_confirmations(self, block_times, confirmations):
        """Collect statistics about the time to reach consensus based on the n of confirmations required"""

        logging.info("Analyzing time to reach consensus for number of confirmations " + str(confirmations))

        path = os.path.join(self.dir_simulation_results, "_block_time_vs_confirmations_median_time_to_receive.txt")
        with open(path, "a") as f:
            f.write("block_discoveries,last_block_that_confirmedconfirmations,block_time,median_time,uncles")

        # running 100 simulations for each block time
        config.n_of_block_discoveries = 300
        config.n_confirmations_to_reach_consensus = confirmations

        for block_time in block_times:

            logging.info("Simulator Run for Block time " + str(block_time))

            ratio = block_time/13.24

            latency.mean_block_transfer = 0.5*ratio
            latency.std_block_transfer = 0.1*ratio

            # Mean  and std deviation for msg latency do not change because it does not depend
            # on block size. Shown here for visualization purposes
            latency.mean_latency_msgs = 0.3
            latency.std_latency_msgs = 0.1

            # Time interval to execute PoW validation
            latency.max_time_pow_validation = 0.2*ratio
            latency.min_time_pow_validation = 0.1*ratio

            # run the simulation for a specific block time
            config.block_discovery_rate = block_time
            sim = Simulator()
            uncles, network = sim.run()

            logging.info(str(uncles) + "uncles formed")

            last_block_reception_times = []
            block_observed = None
            for peer_id in network.nodes:
                peer = network.nodes[peer_id]['data']
                try:
                    block_observed_created_at = peer.blocks_reception_history[1].block.timestamp
                    last_entry_id = next(reversed(peer.blocks_reception_history))
                    last_entry = peer.blocks_reception_history[last_entry_id].received_at
                    block_observed = last_entry_id
                    delta = last_entry - block_observed_created_at
                    deta_to_sec = delta.total_seconds()
                    last_block_reception_times.append(deta_to_sec)
                except:
                    continue

            median_to_receive_block = int(stats.median(last_block_reception_times))
            # #save  the collected times to receive a block for block time N in a CSV file for posterior analysis
            logging.info("Saving last time to receive block for block time " + str(block_time) + " and confirmations " + str(confirmations))


            with open(path, "a") as f:
                    # block_discoveries, last block that confirmed, confirmations, block time, median time, uncles
                    f.write(str(config.n_of_block_discoveries) + ", " +\
                            str(block_observed) + ", " +\
                            str(confirmations) + ", " + \
                            str(block_time) + ", " +\
                            str(median_to_receive_block) +  ", " + \
                            str(uncles) + "\n")

    def get_stats_from_confirmation_run(self):

        fig, ax = plt.subplots(figsize=(10, 6))
        font = {'family': 'sans-serif',
               'weight': 'bold',
               'size': 16}
        matplotlib.rc('font', **font)
        plt.style.use('ggplot')

        for confirmation in [20, 30, 35, 50]:
            simulation_filename = "_block_time_vs_confirmations_" + str(confirmation) + ".txt"
            df = pd.read_csv(r'simulation_data/' + simulation_filename)
            df['median_time'] = df['median_time'].apply(lambda x: str(timedelta(seconds=x)))
            df['last_block_that_confirmed'] = df['last_block_that_confirmed'] -1
            print(df.to_string())

            path = os.path.join(self.dir_simulation_results, simulation_filename)
            confirmations_df = pd.read_csv(path) #.values.tolist()
            block_time = confirmations_df['block_time'].apply(lambda x: int(x)).values.tolist()
            blocks_mined_until_confirmation_df = confirmations_df['last_block_that_confirmed'] -1
            blocks_mined_until_confirmation = blocks_mined_until_confirmation_df.values.tolist()

            curve_label = str(confirmation) + ' confirmations'
            ax.plot(block_time, blocks_mined_until_confirmation, label=curve_label)
        ax.grid(True)
        ax.legend(title='Block Time [s]')
        ax.set_title('Blocks Mined Until Number of Confirmations is Achieved')
        ax.set_xlabel('Block Time [s]')
        ax.set_ylabel('Number of Blocks Mined')
        plt.xticks(block_time)
        plt.show()

    def get_number_of_uncles_vs_block_time(self):
        # collecting number of uncles for block time from 1 to 30
        for block_time in range(1,30):
            logging.info("Generating number of uncles for block time " + str(block_time))
            config.block_discovery_rate = block_time
            config.n_of_block_discoveries = 200
            sim = Simulator()
            uncles_count, _ = sim.run()

            #save  the collected number of uncles in a CSV file for posterior analysis
            path = os.path.join(self.dir_simulation_results, "uncles_vs_block_time_2txt")
            with open(path, "a") as f:
                f.write(str(block_time) + ', ' + str(uncles_count) + "\n")

    def plot_uncles_vs_block_time(self):
        fig, ax = plt.subplots(figsize=(8, 6))

        font = {'family': 'sans-serif',
               'weight': 'bold',
               'size': 16}
        matplotlib.rc('font', **font)
        plt.style.use('ggplot')

        df = pd.read_csv(os.path.join(self.dir_simulation_results, 'uncles_vs_block_time.txt'))
        block_times = (df["block_time"]).values.tolist()
        n_sims = int(config.n_of_block_discoveries)
        df["uncles_count"] = (df["uncles_count"]/n_sims)*100
        uncles_perc = df["uncles_count"].values.tolist()

        ax.bar(block_times, uncles_perc)
        plt.xticks(block_times)
        ax.set_title('Uncle Rate x Block Time')
        ax.set_xlabel('Block time [s]')
        ax.set_ylabel('Uncle Rate [%]')
        plt.show()



if __name__ == '__main__':
    log.init_logger()
    report = Report()

    # create the CDF of block propagation
    #block_times = [1,2,3,4,5,6,7,8,9,10,11,12,13.24,14,15,16,17,18,19,20,21,22,23,24,25] #[1,2,3,4,5,6,7,8,9,
    block_times = [1]
    report.collect_block_propagation(block_times)
    #report.plot_block_propagation(block_times)
    #report.get_number_of_uncles_vs_block_time()
    #report.plot_uncles_vs_block_time()

    # create stats on time to consensus based on number of confirmations
    #for confirmation in [20,30,35,50]:
        #report.collect_stats_for_number_of_confirmations(block_times, 20)
        #.get_stats_from_confirmation_run()


