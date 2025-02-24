import hashlib
import json
from pathlib import Path
import requests
import logging
import shutil

logging.basicConfig(level=logging.DEBUG)

from ibdb import etl as ibdb_etl

BASE_DIR = '.data'
STRUCTED_DATA_BASE_DIR = '.structured-data'
BROWSERLESS_API_KEY = "RlvARtDCQau1vs07cc53e9a1a984752441fe5823f2"
BROWSERLESS_URL = f"https://chrome.browserless.io/content?token={BROWSERLESS_API_KEY}"

def fetch_url(url, cache_path=None):
    """Fetch a URL using Browserless API to bypass IP restrictions."""
    response_file = Path(cache_path)
    
    if not response_file.exists():
        logging.info("Fetching %s via Browserless", url)
        payload = {
            "url": url,
            "waitFor": 5000,
            "gotoOptions": {
                "waitUntil": "networkidle0",
                "timeout": 30000
            }
        }
        
        response = requests.post(BROWSERLESS_URL, json=payload)
        logging.debug("Response status: %s", response.status_code)
        logging.debug("Response headers: %s", dict(response.headers))
        
        if response.status_code == 200:
            Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
            content = response.text
            logging.debug("First 1000 characters of response: %s", content[:1000])
            response_file.write_text(content)
            return content
        else:
            logging.error("Failed to fetch %s. Status: %s", url, response.status_code)
            logging.debug("Response content: %s", response.text[:500])
            return None
    else:
        logging.info("Using cached response from %s", cache_path)
    
    return response_file.read_text()

def persist_structured_data(data, cache_path=None):
    """Persist structured data to a file."""
    Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
    Path(cache_path).write_text(json.dumps(data, indent=2))
    logging.info("Structured data saved to %s", cache_path)

urls_to_scrape = {
    "ibdb.com": {
        "etl_function": ibdb_etl,
        "urls": [
            "https://www.ibdb.com/broadway-production/-juliet-534962#Statistics"
        ]
    }
}

if __name__ == '__main__':
    # Clear existing cache
    for path in [BASE_DIR, STRUCTED_DATA_BASE_DIR]:
        if Path(path).exists():
            shutil.rmtree(path)
            logging.info(f"Cleared cache directory: {path}")
    
    for domain, domain_configs in urls_to_scrape.items():
        urls = domain_configs['urls']
        etl_function = domain_configs['etl_function']
        cache_path = f"{BASE_DIR}/{domain}"
        cache_path_structured = f"{STRUCTED_DATA_BASE_DIR}/{domain}"
        Path(cache_path).mkdir(parents=True, exist_ok=True)
        Path(cache_path_structured).mkdir(parents=True, exist_ok=True)
        
        for url in urls:
            logging.info("Fetching %s", url)
            url_id = hashlib.md5(url.encode()).hexdigest()
            response_html = fetch_url(url, cache_path=f"{cache_path}/{url_id}.html")
            
            if response_html:
                structured_data = etl_function(response_html)
                persist_structured_data(structured_data, cache_path=f"{cache_path_structured}/{url_id}.json")
