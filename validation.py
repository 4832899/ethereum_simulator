from datetime import date, timedelta
import pandas as pd
from main import Simulator
import config

blocks_simulator_network_file = r'validation/blocks_per_day_simulator.csv'
blocks_real_network_file = r'validation/blocks_per_day_etherchain.csv'

uncles_simulator_network_file = r'validation/perc_uncles_simulator.csv'
uncles_real_network_file = r'validation/uncles_per_day_etherchain.csv'

def calculate_moments_blocks_per_day_in_simulator():
    calculate_moments_blocks_per_day(blocks_simulator_network_file)

def calculate_moments_blocks_per_day_in_real_ethereum():
    calculate_moments_blocks_per_day(blocks_real_network_file)

def collect_number_of_uncles_in_simulator():
    for i in range(300):
        config.simulation_type = 'block_discoveries'
        config.n_of_block_discoveries = 400
        sim = Simulator()
        sim.build_network()
        sim.build_queue_of_events()
        uncles_counter, _ = sim.run()
        print("uncles", str(uncles_counter))
        n_uncles_file = open(r'validation/perc_uncles_simulator.csv', 'a')
        n_uncles_file.write(str(uncles_counter) + '\n')
        n_uncles_file.close()

def calculate_moments_uncles_in_simulator():
    blocks = pd.read_csv(uncles_simulator_network_file)['uncles']
    mean = int(blocks.mean())
    print("Average perentage of uncles is ", str(mean))
    std = int(blocks.std())
    print("Standard deviation uncles is", str(std))
    return mean, std

def calculate_moments_uncles_per_day_in_real_ethereum():
    uncles = pd.read_csv(uncles_real_network_file)
    blocks = pd.read_csv(blocks_real_network_file)
    perc_uncles_uncles_real_network_file = uncles['uncles']/blocks['blocks']
    mean = perc_uncles_uncles_real_network_file.mean()*100
    print("Percentage of uncles in real Ethereum is ", str(mean))
    std = perc_uncles_uncles_real_network_file.std()*100
    print("Standard deviation of uncles in real Ethereum is", str(std))
    return mean, std

def calculate_moments_blocks_per_day(data_file):
    blocks = pd.read_csv(data_file)['blocks']
    mean = int(blocks.mean())
    print("Average number of blocks added to the blockchain in 24 hours is ", str(mean))
    std = int(blocks.std())
    print("Standard deviation of blocks added to the blockchain in 24 hours is", str(std))
    return mean, std

def generate_dates_between_two_dates(start_date, end_date):
    delta = end_date - start_date
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        print(day)


if __name__ == '__main__':
    calculate_moments_uncles_in_simulator()