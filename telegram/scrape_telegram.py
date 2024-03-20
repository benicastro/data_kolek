# Import telegram sources from file
from telegram_source import telegram_links

# Import modules/libraries
import random
import requests
import pandas as pd
from datetime import *
from selectolax.parser import HTMLParser
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
        continue_scraping = True
        post_number_before = None
        query_params = {"before": None}

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

        while continue_scraping:

            res = self.make_request(channel_name, query_params)

            if not res:
                return

            parsed_html = HTMLParser(res)

            post_number_query = (
                parsed_html.css_first("link").attrs["href"].split("before=")
            )
            if len(post_number_query) == 1:
                print("[!] Channel can't be accessed.")
                return
            post_number = post_number_query[1]

            if post_number == post_number_before:
                print("All posts already scraped. Moving on to next one...")
                continue_scraping = False
                continue
            query_params["before"] = post_number
            print(post_number)

            if int(post_number) < 1800:
                return

    def make_request(self, endpoint, query_params):
        for i in range(3):
            try:
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    params=query_params,
                )
                response.raise_for_status()
                return response.text
            except requests.RequestException as err:
                print(
                    f"Error response {err.response.status_code} while requesting {err.request.url!r}."
                )
            return None

    def get_channel_info(self, telegram_link):
        channel_info = {}
        try:
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
        except IndexError:
            print("[!] {telegram_link} is not a valid telegram link - skipping...")
            return None

    def get_results(self):
        for source in self.sources:
            print(f"Scraping {source.get('url')}...")
            channel_info = self.get_channel_info(source)

            if not channel_info:
                continue

            channel_content = self.scrape_channel(
                channel_info["channel_name"], channel_info["channel_label"]
            )


# Test
telegram_scraper = TelegramScraper([telegram_links[0]])
telegram_scraper.get_results()
