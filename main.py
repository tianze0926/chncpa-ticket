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
    requests.post(URL, json=data, timeout=TIMEOUT)

def check(concert: Concert) -> bool:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    KEYWORD = '【开票】'
    url = f"https://ticket.chncpa.org/product-{concert['id']}.html"
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)

    return KEYWORD in response.text

with open('config.yml') as f:
    config: Config = yaml.full_load(f)

wx_push_config = config['wx_push']
DURATION = config["duration"]
TIMEOUT = config["timeout"]

opened_concerts: dict[str, bool] = {}

while True:
    for concert in config['concerts']:
        if concert["id"] in opened_concerts:
            continue
        try:
            opened = check(concert)
            if opened:
                opened_concerts[concert["id"]] = True
                notify(wx_push_config, concert)
                logger.info(f"{concert['name']} is open")
            else:
                logger.debug(f'{concert["name"]} not opened')
        
        except Exception as e:
            logger.exception(e)
            break

    time.sleep(DURATION)
