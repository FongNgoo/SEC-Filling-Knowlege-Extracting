# main.py
import os
from config.logging_config import setup_logger
from config.settings import load_ciks
from config.search_patterns import load_search_patterns
from data_access.filing_metadata import fetch_filing_metadata
from extraction.batch_processor import process_filings_batch

def main():
    setup_logger()

    # 1️⃣ Load CIK universe
    ciks_df = load_ciks()

    # 2️⃣ Fetch filing metadata
    filings_df = fetch_filing_metadata(ciks_df)

    if filings_df.empty:
        print("No filings found. Exiting.")
        return

    # 3️⃣ Load section search patterns (ONCE)
    search_patterns = load_search_patterns(
        os.path.join(
            "SEC_Filling_Knowlege_Extracting",
            "config",
            "document_group_section_search.json"
        )
    )

    # 4️⃣ Parallel extraction
    process_filings_batch(
        filings_df,
        search_patterns,
        max_workers=4
    )

if __name__ == "__main__":
    main()
