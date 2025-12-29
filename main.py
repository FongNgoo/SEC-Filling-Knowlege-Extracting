# main.py
import os
from config.logging_config import setup_logger
from config.settings import load_ciks
from config.search_patterns import load_search_patterns
from data_access.filing_metadata import fetch_filing_metadata
from extraction.batch_processor import fetch_content_batch
import polars as pl

def main():
    logger = setup_logger()

    # 1️⃣ Load CIK universe
    ciks_df = load_ciks()

    # 2️⃣ Fetch filing metadata
    filings_df = fetch_filing_metadata(ciks_df)

    if filings_df.empty:
        print("No filings found. Exiting.")
        return

    search_patterns = load_search_patterns(
        "SEC_Filling_Knowlege_Extracting/config/document_group_section_search.json"
    )

    content_data = fetch_content_batch(
        filings_df,
        search_patterns_path=search_patterns,
        max_workers=8
    )
    content_df = pl.DataFrame(content_data)

    content_df = content_df.filter(
        pl.col("content").is_not_null()
    )

    content_df.write_parquet(
        os.path.join("SEC_Filling_Knowlege_Extracting","data", "03_primary", "filing_data.parquet")
    )

    logger.info(f"Saved {len(content_df)} extracted sections")


if __name__ == "__main__":
    main()
