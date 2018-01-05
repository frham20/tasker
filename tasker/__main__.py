"""
Main
"""
import sys
import logging
import argparse
from tasker.config import load_config, run_config

def main():
    """Package ran as exec"""

    parser = argparse.ArgumentParser(description='Executes a serie of tasks')
    parser.add_argument('filename', type=str,
                        help='The filename of the JSON file containing the tasks to execute')
    args = parser.parse_args()

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )

    logger = logging.getLogger(__name__)

    try:
        logger.info("Loading config file...")
        cfg = load_config(args.filename)

        logger.info("Running configuration...")
        run_config(cfg)

        logger.info("Done!")
    except Exception as ex:
        logger.exception(ex)


assert __name__ == '__main__'
main()
