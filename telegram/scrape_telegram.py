# Import telegram sources from file
from telegram_source import telegram_links

# Import modules/libraries
import time
import random
import requests
import datetime
import pandas as pd
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
    def __init__(self, telegram_sources, posts_per_source):
        self.base_url = "https://t.me/s/"
        self.headers = {
            "User-Agent": self.get_useragent(),
        }
        self.sources = telegram_sources
        self.posts_limit = posts_per_source

    def get_useragent(self):
        """This function returns a random user agent from a specified list for header purposes."""
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

            if post_number == query_params["before"]:
                print("All posts already scraped. Moving on to next one...")
                continue_scraping = False
                continue
            query_params["before"] = post_number

            print(f"Scraping posts from batch identifier - {post_number}...")

            posts = parsed_html.css(
                "div.tgme_widget_message_wrap.js-widget_message_wrap"
            )

            if not posts:
                print("[!] No posts found.")
                return

            for i, post in enumerate(posts):

                # Extract post text information
                try:
                    text_node = post.css_first(
                        "div.tgme_widget_message_text.js-message_text"
                    )
                    if text_node is None:
                        continue
                    else:
                        post_text = text_node.text()
                except Exception as err:
                    post_text = "null"

                # Extract the mentioned urls in the post
                extracted_urls = []
                a_tags = text_node.css("a")
                if a_tags:
                    for tag in a_tags:
                        extracted_urls.append(tag.attrs["href"])

                # Extract the username and user link of the one who posted
                username_link = post.css_first(
                    "a.tgme_widget_message_owner_name"
                ).attrs["href"]
                username = username_link.split("t.me/")[-1]

                # Extract number of views
                units = {
                    "K": 1000,
                    "M": 1000000,
                    "B": 1000000000,
                }  # Create dictionary representing the values for each letter
                try:
                    views_raw = post.css_first("span.tgme_widget_message_views").text()
                    try:
                        number_of_views = float(views_raw)
                    except Exception as err:
                        unit = views_raw[-1]
                        number_of_views = float(views_raw[:-1]) * units[unit]
                except Exception as err:
                    number_of_views = 0

                post_link_date = post.css_first("a.tgme_widget_message_date")
                post_link = ""
                date = ""

                entry = self.get_entry(
                    channel_name=channel_name,
                    channel_label=channel_label,
                    username=username,
                    username_link=username_link,
                    post_text=post_text,
                    post_link=post_link,
                    date=date,
                    number_of_views=number_of_views,
                    extracted_urls=extracted_urls,
                )

                posts_list.append(asdict(entry))

                if len(posts_list) == self.posts_limit:
                    print(f"{len(posts_list)} posts returned.")
                    return posts_list

            time.sleep(
                random.randint(1, 3)
            )  # Limit request frequency per post batch identifier

    def make_request(self, endpoint, query_params):
        """This function attempts to make an http request given the endpoint and query parameters. It returns the response in text format."""
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
        """This function obtains the channel name and channel label from the given telegram link source."""
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

    def get_entry(
        self,
        channel_name,
        channel_label,
        username,
        username_link,
        post_text,
        post_link,
        date,
        number_of_views,
        extracted_urls,
    ):
        """This function creates an entry for the output data with the recommended schema using information from the website."""
        new_entry = PostInfo(
            channel_name=channel_name,
            channel_label=channel_label,
            username=username,
            username_link=username_link,
            post_text=post_text,
            post_link=post_link,
            date=date,
            number_of_views=number_of_views,
            extracted_urls=extracted_urls,
        )
        return new_entry

    def get_results(self):
        """This function outputs the result of the scraping process."""
        scraping_results = []
        for source in self.sources:
            print(f"Scraping {source.get('url')}...")
            channel_info = self.get_channel_info(source)

            if not channel_info:
                continue

            channel_content = self.scrape_channel(
                channel_info["channel_name"], channel_info["channel_label"]
            )

            print("###################################################################")

            if channel_content:
                scraping_results.extend(channel_content)

        return scraping_results


# Test
telegram_scraper = TelegramScraper(telegram_links[:3], 25)
scraped_data = telegram_scraper.get_results()
df = pd.DataFrame(scraped_data)
df.to_csv("scraped_output.csv", encoding="utf-8", index=False)
print(df)
