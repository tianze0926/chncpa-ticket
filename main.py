import yaml
import requests
import time

from type import Concert, PushConfig, Config
from logger import logger

def notify(config: PushConfig, concert: Concert):
    URL = 'https://wxpusher.zjiecode.com/api/send/message'
    message = f"Concert `{concert['name']}` is now open"
    data = {
        "appToken": config["app_token"],
        "content": message,
        "summary": message,
        "contentType": 1,
        "topicIds": config["topic_ids"],
        "uids":config["uids"],
        "url": f"https://ticket.chncpa.org/product-{concert['id']}.html",
        "verifyPay": False
    }
    requests.post(URL, json=data)

def check(concert: Concert) -> bool:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    KEYWORD = '【开票】'
    url = f"https://ticket.chncpa.org/product-{concert['id']}.html"
    response = requests.get(url, headers=HEADERS)
    if KEYWORD in response.text:
        logger.info(f"{concert['name']} is open")
        notify(wx_push_config, concert)
        return True
    return False

with open('config.yml') as f:
    config: Config = yaml.full_load(f)

wx_push_config = config['wx_push']

opened_concerts: dict[str, bool] = {}

while True:
    for concert in config['concerts']:
        if concert["id"] in opened_concerts:
            continue
        try:
            open = check(concert)
        except Exception as e:
            logger.exception(e)
            break
        if open:
            opened_concerts[concert["id"]] = True

    time.sleep(1)
