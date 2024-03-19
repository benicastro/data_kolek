# Import telegram sources from file
from telegram_source import telegram_links

# Import modules/libraries
import random
import requests
import pandas as pd
from datetime import *
from dataclasses import dataclass, asdict


# Create dataframe schema
@dataclass
class PostInfo:
    channel_name: str
    channel_label: str
    username: str
    username_link: str
    post_text: str
    post_link: str
    date: str
    number_of_views: int
    extracted_urls: list


# Create TelegramScraper class
class TelegramScraper:
    def __init__(self, telegram_sources):
        self.base_url = "https://t.me/s/"
        self.headers = {
            "User-Agent": self.get_useragent(),
        }
        self.sources = telegram_sources

    def get_useragent(self):
        useragent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
        ]

        return random.choice(useragent_list)

    def scrape_channel(self, channel_name, channel_label):
        posts_list = []

        # # Restrict the number of scraped items
        # if channel_name in explored_channels:
        #     time_filter = 7  # 1 week - return to 7
        #     print(
        #         f"channel {channel_name} has been previously scraped, proceed to collect posts only for the last seven days."
        #     )
        # else:
        #     time_filter = 90  # 3 months
        #     print(
        #         f"channel {channel_name} is a new channel, proceed to scraping posts for the last 90 days."
        #     )

        query_params = {"": ""}

        res = self.make_request(channel_name, query_params)
        print(res)

    def make_request(self, endpoint, query_params):
        for i in range(3):
            try:
                response = requests.get(
                    f"{self.base_url}/{endpoint}", headers=self.headers
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as err:
                print(f"Error making request: {err}")
                continue
            return None

    def get_channel_info(self, telegram_link):
        channel_info = {}
        channel_info["channel_name"] = (
            telegram_link.get("url")
            .split(".me/")[1]
            .replace("joinchat/", "")
            .replace("s/", "")
            .split("/")[0]
            .split("?")[0]
            .split("&")[0]
        )
        channel_info["channel_label"] = telegram_link.get("label")
        return channel_info

    def get_results(self):
        for source in self.sources:
            channel_info = self.get_channel_info(source)
            print(channel_info)


# Test
telegram_scraper = TelegramScraper([telegram_links[0]])
telegram_scraper.get_results()
