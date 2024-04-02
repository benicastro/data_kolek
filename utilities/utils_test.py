# TEST FILE #

# Import Files
import utils as utils

# Test extract_domain function

sample_urls = [
    "www.abc.au.uk",
    "https://github.com",
    "http://github.ca",
    "https://www.google.ru",
    "http://www.google.co.uk",
    "www.yandex.com",
    "yandex.ru",
]

for url in sample_urls:
    domain = utils.extract_domain(url)
    print(domain)
