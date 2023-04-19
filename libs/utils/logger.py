import logging
import os

def get(name:str, level = logging.DEBUG ) -> logging.Logger:
    # init logger object
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # create file handler if it doesn't exist
    if not len(logger.handlers):
        if not os.path.exists("logs"):
            os.makedirs("logs")
        fh = logging.FileHandler(f"logs/{name}.txt")
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
    return logger