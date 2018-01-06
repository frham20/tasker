"""
Main
"""
import sys
import os
import logging
import argparse
import tempfile
import datetime
from tasker.config import load_config, run_config

class App(object):
    """Main application class"""
    def __init__(self):
        self.logger = logging.getLogger()
        self.log_filename = None
        self.log_directory = None
        self.config_filename = None
        self._init()

    def _init_logger(self):
        log_level = logging.INFO
        if __debug__:
            log_level = logging.DEBUG
        self.logger.setLevel(log_level)

        log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

        # stdout handler
        log_sh = logging.StreamHandler(sys.stdout)
        log_sh.setLevel(log_level)
        log_sh.setFormatter(log_formatter)
        self.logger.addHandler(log_sh)

        # log file handler
        if self.log_directory is None:
            if self.log_filename is None:
                log_fd, log_fname = tempfile.mkstemp(suffix='.log',
                                                     prefix='tasker_',
                                                     dir=None,
                                                     text=True)
                if log_fd is not None:
                    os.close(log_fd)
                self.log_directory, self.log_filename = os.path.split(log_fname)
            else:
                self.log_directory = tempfile.gettempdir()
        else:
            if self.log_filename is None:
                cur_date = datetime.datetime.now()
                self.log_filename = 'tasker_{:4d}_{:02d}_{:02d}_T{:02d}_{:02d}_{:02d}.log'.format(
                    cur_date.year, cur_date.month, cur_date.day,
                    cur_date.hour, cur_date.minute, cur_date.second)

            # Make sure output dir exists
            os.makedirs(self.log_directory, mode=0o777, exist_ok=True)

        log_fh = logging.FileHandler(os.path.join(self.log_directory, self.log_filename))
        log_fh.setLevel(log_level)
        log_fh.setFormatter(log_formatter)
        self.logger.addHandler(log_fh)

    def _parse_cmdargs(self):
        parser = argparse.ArgumentParser(description='Executes a series of tasks')

        parser.add_argument('filename', type=str,
                            help='The filename of the JSON file containing the tasks to execute')
        parser.add_argument('-ld', '--log-directory', type=str,
                            help='The log output directory')
        parser.add_argument('-lf', '--log-filename', type=str,
                            help='The log output filename')

        args = parser.parse_args()

        self.config_filename = args.filename
        self.log_directory = args.log_directory
        self.log_filename = args.log_filename

    def _init(self):
        """Initialize the app"""
        self._parse_cmdargs()
        self._init_logger()

    def run(self):
        """Run the app"""
        try:
            self.logger.info("Loading config file %s...", self.config_filename)
            cfg = load_config(self.config_filename)

            self.logger.info("Running tasks...")
            run_config(cfg)

            self.logger.info("Done!")
        except Exception as ex:
            self.logger.exception(ex)

        # If there were some errors, open the log
        # TODO, parse log for :ERROR: or :CRITICAL: tags
        if (self.log_directory is not None) and (self.log_filename is not None):
            os.startfile(os.path.join(self.log_directory, self.log_filename))


def main():
    """Package ran as exec"""
    app = App()
    app.run()

assert __name__ == '__main__'
main()
