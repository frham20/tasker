"""
Main
"""
import sys
import os
import logging
import argparse
import tempfile
from tasker.config import load_config, run_config

def main():
    """Package ran as exec"""

    # Parse command line args
    parser = argparse.ArgumentParser(description='Executes a series of tasks')
    parser.add_argument('filename', type=str,
                        help='The filename of the JSON file containing the tasks to execute')
    args = parser.parse_args()

    # Initialize logger
    log_level = logging.INFO
    if __debug__:
        log_level = logging.DEBUG

    logger = logging.getLogger()
    logger.setLevel(log_level)

    log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

    log_sh = logging.StreamHandler(sys.stdout)
    log_sh.setLevel(log_level)
    log_sh.setFormatter(log_formatter)
    logger.addHandler(log_sh)

    log_fd, log_filename = tempfile.mkstemp(suffix='.log', prefix='tasker_', dir=None, text=True)
    log_fh = logging.FileHandler(log_filename)
    log_fh.setLevel(log_level)
    log_fh.setFormatter(log_formatter)
    logger.addHandler(log_fh)

    # Load config and run the tasks
    try:
        logger.info("Loading config file...")
        cfg = load_config(args.filename)

        logger.info("Running config tasks...")
        run_config(cfg)

        logger.info("Done!")
    except Exception as ex:
        logger.exception(ex)

    # Close log file
    os.close(log_fd)

    # If there were some errors, open the log
    # TODO, parse log for :ERROR: or :CRITICAL: tags
    os.startfile(log_filename)

assert __name__ == '__main__'
main()
