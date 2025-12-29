# data_access/sec_client.py
import requests
import time
import logging
from config.settings import HEADERS

logger = logging.getLogger(__name__)

def safe_get(url, retries=3, sleep=0.5):
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers={"User-Agent": HEADERS}, timeout=30)
            if resp.status_code == 200:
                return resp
            logger.warning(f"HTTP {resp.status_code} for {url}")
        except Exception as e:
            logger.warning(f"Request error ({attempt+1}/{retries}): {e}")
        time.sleep(sleep)
    logger.error(f"Failed to fetch URL after {retries} attempts: {url}")
    return None
