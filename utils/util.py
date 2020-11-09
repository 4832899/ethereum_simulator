import os
import statistics as stats

import pandas as pd

import config as cnf


def get_block_height(tip):
    return tip.split(" ")[2]

def get_number_powerful_miners():
    file = cnf.hash_power_distribution_file
    counter = 0
    with open(file, 'r') as f:
        for line in f:
            counter += 1
    return counter-1

def get_stats_from_propagation_times():
    mean_prop_times = []
    file = cnf.block_prop_times_file
    df = pd.read_csv(file)
    for _, column_data in df.iteritems():
        mean_prop_times.append(column_data.mean())
    mean = stats.mean(mean_prop_times)/1000
    std = stats.stdev(mean_prop_times)/1000
    median = stats.median(mean_prop_times)/1000
    return mean, std, median, mean_prop_times

def block_prop_samples():
    for rtt in ['200', '100', '50', '25', '10', '5', '1']:
        filename = "block_arrival_times_" + rtt + "_pow_cte.txt"
        yield os.path.join(cnf.dir_sim_output, filename)


