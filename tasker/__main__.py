"""
Main
"""
import sys
import os
import logging
from tasker.config import load_config, run_config

def main():
    """Package ran as exec"""
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

    logger = logging.getLogger(__name__)
    logger.info("Loading config file...")

    config_filename = os.path.join(os.getcwd(), "config.json")
    cfg = load_config(config_filename)
    run_config(cfg)

    logger.info("Done!")

assert __name__ == '__main__'
main()
