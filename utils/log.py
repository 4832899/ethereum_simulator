import logging
import sys
import os
from datetime import datetime
import config

def init_logger():
    filename = create_filename()
    log_file_path = os.path.join(config.dir_simulation_log, filename)
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(message)s",
                        datefmt="%d-%m-%> %H:%M:%S",
                        handlers=[logging.FileHandler(log_file_path),
                                  logging.StreamHandler(sys.stdout)
                        ])

def create_filename():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = timestamp + '_simulation.log'
    return filename

