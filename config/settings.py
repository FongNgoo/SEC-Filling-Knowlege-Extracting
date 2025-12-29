#/config.settings.py
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

HEADERS = os.environ.get('USER_AGENT')
START_DATE = "2023-01-15"
END_DATE = "2025-04-25"
OUTPUT_DIR = os.path.join("SEC_Filling_Knowlege_Extracting","data", "03_primary")

def load_ciks() -> pd.DataFrame:
    """
    Load default CIK universe.
    Single source of truth for pipeline.
    """
    df = pd.DataFrame({
        "cik": [
            "0001318605",  # TSLA
            "0001065280",  # NFLX
            "0000789019",  # MSFT
            "0001018724",  # AMZN
        ],
        "ticker": ["TSLA", "NFLX", "MSFT", "AMZN"]
    })

    return df