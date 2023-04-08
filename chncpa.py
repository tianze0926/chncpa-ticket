"""
Class CHNCPA
"""

import time
from random import Random
from typing import Callable

import requests
from typeguard import check_type

from logger import logger
from type import Concert, Config, DurationConfig, DurationConfigFixed, DurationConfigGamma

class CHNCPA:
    """
    Core logic of CHNCPA tickets
    """

    def __init__(self, config: Config) -> None:
        check_type(config, Config)
        self.keywords = config["keywords"]
        self.concerts = config["concerts"]
        self.push_config = config['wx_push']
        self.timeout = config["timeout"]

        duration = config["duration"]
        def setup_sleep(duration: DurationConfig) -> Callable[[], None]:
            if duration["type"] == 'fixed':
                check_type(duration, DurationConfigFixed)
                def gen_seconds():
                    return duration["len"]
            elif duration["type"] == 'gamma':
                check_type(duration, DurationConfigGamma)
                random = Random()
                def gen_seconds():
                    return random.gammavariate(duration["k"], duration["theta"])
            def sleep():
                seconds = gen_seconds()
                logger.debug('sleeping for %f seconds', seconds)
                time.sleep(seconds)
            return sleep
        self.sleep_inner = setup_sleep(duration["inner"])
        self.sleep_outer = setup_sleep(duration["outer"])

    def notify(self, concert: Concert, message: str) -> None:
        """
        Send a push message about the opened concert
        """
        url = 'https://wxpusher.zjiecode.com/api/send/message'
        data = {
            "appToken": self.push_config["app_token"],
            "content": message,
            "summary": message,
            "contentType": 1,
            "topicIds": self.push_config["topic_ids"],
            "uids": self.push_config["uids"],
            "url": f"https://ticket.chncpa.org/product-{concert['id']}.html",
            "verifyPay": False
        }
        response = requests.post(url, json=data, timeout=self.timeout)
        response_data = response.json()
        if not response_data["success"]:
            raise RuntimeError(f'notify failed: {response_data["msg"]}')

    def check(self, concert: Concert) -> bool:
        """
        Check if the concert is open.
        Returns True if none of the keywords is found.
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'
                ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        url = f"https://ticket.chncpa.org/product-{concert['id']}.html"
        response = requests.get(url, headers=headers, timeout=self.timeout)
        if response.status_code != 200:
            message = f'Concert `{concert["id"]}` `{concert["name"]}` query request failed: {response.status_code} {response.text}'
            self.notify(concert, message)
            raise RuntimeError(message)

        for keyword in self.keywords:
            if keyword in response.text:
                return False
        return True

    def loop(self):
        """
        Iterate over the concerts
        """
        opened_concerts: dict[str, bool] = {}
        while True:
            for concert in self.concerts:
                if concert["id"] in opened_concerts:
                    continue
                try:
                    opened = self.check(concert)
                    if opened:
                        opened_concerts[concert["id"]] = True
                        self.notify(concert, f'Concert `{concert["id"]}` `{concert["name"]}` is now open')
                        logger.info("%s %s is open", concert["id"], concert["name"])
                    else:
                        logger.debug('%s %s not opened', concert["id"], concert["name"])

                except Exception as err:
                    logger.exception(err)
                    break

                self.sleep_inner()

            self.sleep_outer()
