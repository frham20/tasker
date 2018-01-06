"""
Main
"""
import sys
import os
import logging
import argparse
import tempfile
import contextlib
from tasker.config import load_config, run_config

class App(object):
    """Main application class"""
    def __init__(self):
        self.logger = logging.getLogger()
        self.log_fd = None
        self.log_filename = ''
        self.config_filename = ''
        self._init()

    def _init_logger(self):
        log_level = logging.INFO
        if __debug__:
            log_level = logging.DEBUG

        self.logger.setLevel(log_level)

        log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

        log_sh = logging.StreamHandler(sys.stdout)
        log_sh.setLevel(log_level)
        log_sh.setFormatter(log_formatter)
        self.logger.addHandler(log_sh)

        self.log_fd, self.log_filename = tempfile.mkstemp(suffix='.log',
                                                          prefix='tasker_',
                                                          dir=None,
                                                          text=True)
        log_fh = logging.FileHandler(self.log_filename)
        log_fh.setLevel(log_level)
        log_fh.setFormatter(log_formatter)
        self.logger.addHandler(log_fh)

    def _parse_cmdargs(self):
        parser = argparse.ArgumentParser(description='Executes a series of tasks')
        parser.add_argument('filename', type=str,
                            help='The filename of the JSON file containing the tasks to execute')
        args = parser.parse_args()
        self.config_filename = args.filename

    def _init(self):
        """Initialize the app"""
        self._parse_cmdargs()
        self._init_logger()

    def close(self):
        """Close and clean-up the app"""
        # Close log file
        if self.log_fd is not None:
            os.close(self.log_fd)

        # If there were some errors, open the log
        # TODO, parse log for :ERROR: or :CRITICAL: tags
        if isinstance(self.log_filename, str):
            os.startfile(self.log_filename)

    def run(self):
        """Run the app"""
        try:
            self.logger.info("Loading config file...")
            cfg = load_config(self.config_filename)

            self.logger.info("Running config tasks...")
            run_config(cfg)

            self.logger.info("Done!")
        except Exception as ex:
            self.logger.exception(ex)


def main():
    """Package ran as exec"""
    with contextlib.closing(App()) as app:
        app.run()

assert __name__ == '__main__'
main()
