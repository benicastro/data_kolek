# Import telegram sources from file
from telegram_source import telegram_links

# Import modules/libraries
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
    number_of_views: int | None
    extracted_urls: list | None
