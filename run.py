import json
import logging.config

from pyCD.controller import PyCD


def setup_logging(path: str = "logging.json") -> None:
    with open(path, "rt") as f:
        config = json.load(f)
    logging.config.dictConfig(config)


if __name__ == '__main__':
    dispatcher = PyCD()
    dispatcher.continuous_delivering(30)
