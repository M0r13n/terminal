import logging
import sys


def setup_logger(level=logging.INFO, stream=True):
    logging.basicConfig(filename='log.log', filemode='w')
    # create logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    if stream:
        # Set handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        # Set format handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)
