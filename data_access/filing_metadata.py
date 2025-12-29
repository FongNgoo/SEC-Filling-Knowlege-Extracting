# data_access/filing_metadata.py
import logging
import pandas as pd
from tqdm import tqdm

from config.settings import START_DATE, END_DATE
from .sec_client import safe_get

logger = logging.getLogger(__name__)

def fetch_filing_metadata(ciks_df: pd.DataFrame) -> pd.DataFrame:
    """
    Fetch 10-K / 10-Q filings metadata for given CIK universe.
    """
    all_filings = []

    for _, row in tqdm(ciks_df.iterrows(), total=len(ciks_df), desc="Fetching filings"):
        cik = row["cik"]
        ticker = row["ticker"]

        try:
            response = safe_get(f"https://data.sec.gov/submissions/CIK{cik}.json")
            if response is None:
                continue

            data = response.json()
            filings = data.get("filings", {}).get("recent", {})
            if not filings:
                continue

            df = pd.DataFrame(filings)
            df = df[df["form"].isin(["10-K", "10-Q"])]

            if df.empty:
                continue

            df["filingDate"] = pd.to_datetime(df["filingDate"], errors="coerce")
            df = df[
                (df["filingDate"] >= START_DATE) &
                (df["filingDate"] <= END_DATE)
            ]

            if df.empty:
                continue

            df["cik"] = cik
            df["ticker"] = ticker

            df["filingUrl"] = df.apply(
                lambda x: (
                    f"https://www.sec.gov/Archives/edgar/data/"
                    f"{cik}/{x['accessionNumber'].replace('-', '')}/{x['primaryDocument']}"
                ),
                axis=1
            )

            all_filings.append(
                df[[
                    "cik",
                    "ticker",
                    "form",
                    "filingDate",
                    "accessionNumber",
                    "primaryDocument",
                    "filingUrl"
                ]]
            )

        except Exception as e:
            logger.exception(f"Error fetching filings for CIK {cik}")

    if not all_filings:
        return pd.DataFrame()

    return pd.concat(all_filings, ignore_index=True)
