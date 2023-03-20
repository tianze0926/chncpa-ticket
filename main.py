"""
Main logic
"""

import yaml

from type import Config
from chncpa import CHNCPA


if __name__ == '__main__':
    with open('config.yml', encoding='utf_8') as f:
        config: Config = yaml.full_load(f)

    chncpa = CHNCPA(config)
    chncpa.loop()
