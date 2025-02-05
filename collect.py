import hashlib
import json
from pathlib import Path
import requests
import logging

logging.basicConfig(level=logging.INFO)

from ibdb import etl as ibdb_etl

BASE_DIR = '.data'
STRUCTED_DATA_BASE_DIR = '.structured-data'

# todo: integrate https://www.browserbase.com/ to fetch the page
def fetch_url(url, cache_path=None):
    # check if we have already downloaded this page
    # if so, return the contents
    # if not, download the page

    response_file = Path(cache_path)

    # todo: check if file is older than X days, then refresh
    if not response_file.exists():
        # new_url = f"browserbase.io?API_KEY={API_KEY}&url={url}"
        response = requests.get(url)
        
        # todo: save the raw data to s3 as well as your local storage
        Path(cache_path).mkdir(parents=True, exist_ok=True)
        response_file.write_text(response.text)

        return response.text

    return response_file.read_text()

def persist_structured_data(data, cache_path=None):
    # todo: save this to a database
    Path(cache_path).write_text(json.dumps(data, indent=2))
    logging.info("Structured data saved to %s", cache_path)


urls_to_scape = {
    "ibdb.com":{
        "etl_function": ibdb_etl,
        "urls": [
            "https://www.ibdb.com/broadway-production/-juliet-534962#Statistics"
        ]
    }
} 

if __name__ == '__main__':
    for domain, domain_configs in urls_to_scape.items():
        urls = domain_configs['urls']
        etl_function = domain_configs['etl_function']
        # TODO: Add more shows to this list
        cache_path = f"{BASE_DIR}/{domain}"
        cache_path_structured = f"{STRUCTED_DATA_BASE_DIR}/{domain}"
        Path(cache_path).mkdir(parents=True, exist_ok=True)
        Path(cache_path_structured).mkdir(parents=True, exist_ok=True)

        for url in urls:
            logging.info("Fetching %s", url)
            url_id = hashlib.md5(url.encode()).hexdigest()
            response_html = fetch_url(url, cache_path=f"{cache_path}/{url_id}.html")
            structured_data = etl_function(response_html)
            persist_structured_data(structured_data, cache_path=f"{cache_path_structured}/{url_id}.json")