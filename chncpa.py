"""
Class CHNCPA
"""

import time

import requests

from logger import logger
from type import Concert, Config

class CHNCPA:
    """
    Core logic of CHNCPA tickets
    """

    def __init__(self, config: Config) -> None:
        self.concerts = config["concerts"]
        self.push_config = config['wx_push']
        self.duration = config["duration"]
        self.timeout = config["timeout"]

    def notify(self, concert: Concert) -> None:
        """
        Send a push message about the opened concert
        """
        url = 'https://wxpusher.zjiecode.com/api/send/message'
        message = f"Concert `{concert['name']}` is now open"
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
        requests.post(url, json=data, timeout=self.timeout)

    def check(self, concert: Concert) -> bool:
        """
        Check if the concert is open
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'
                ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        keyword = '【开票】'
        url = f"https://ticket.chncpa.org/product-{concert['id']}.html"
        response = requests.get(url, headers=headers, timeout=self.timeout)

        return keyword in response.text

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
                        self.notify(concert)
                        logger.info("%s is open", concert['name'])
                    else:
                        logger.debug('%s not opened', concert['name'])

                except Exception as err:
                    logger.exception(err)
                    break

            time.sleep(self.duration)
