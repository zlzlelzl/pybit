import telepot
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse


def send_message(message):
    # 봇 토큰
    token = ""

    # 보낼사람 ID

    bot = telepot.Bot(token)

    bot.sendMessage(message)


def py_telegram(url):
    link, last_sentence = "", ""

    while True:

        try:
            text = requests.get(url).text
            soup = BeautifulSoup(text, "html")

            panel = soup.find(class_="panel panel-default gathering-panel")
            list_group_item = panel.find_all(class_="list-group-item")
            list_group_item_heading = list_group_item[0].find(
                class_="list-group-item-heading")
            link = urlparse(url).hostname + \
                list_group_item_heading.a.get("href")
            if last_sentence != link:
                last_sentence = link
                send_message(link)

            time.sleep(30)
        except:
            pass


if __name__ == "__main__":
    # main_url = ""
    # py_telegram(main_url)
    pass
