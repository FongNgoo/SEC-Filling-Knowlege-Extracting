import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

import pandas as pd

from documents.metadata import Metadata
from extraction.section_extractor import process_filing
from config.settings import OUTPUT_DIR

logger = logging.getLogger(__name__)


def fetch_content_batch(
    filings_df: pd.DataFrame,
    search_patterns_path: dict,
    max_workers: int = 8,
) -> List[Dict]:
    """
    Parallel extraction of SEC filings content.

    Parameters
    ----------
    filings_df : pd.DataFrame
        Output of fetch_filing_metadata()
    search_patterns_path : str
        Path to document_group_section_search.json
    max_workers : int
        Thread pool size

    Returns
    -------
    List[Dict]
        Extracted sections ready for Parquet
    """

    if filings_df.empty:
        logger.warning("No filings to process")
        return []

    # 1️⃣ Load search patterns ONCE
    search_patterns = search_patterns_path

    tasks = []
    results = []

    logger.info(f"Starting parallel extraction with {max_workers} workers")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for _, row in filings_df.iterrows():

            metadata = Metadata(
                cik=row["cik"],
                ticker=row["ticker"],
                form_type=row["form"],
                filed_at=row["filingDate"],
                accession_number=row["accessionNumber"],
                document_url=row["filingUrl"],
            )

            tasks.append(
                executor.submit(
                    process_filing,
                    metadata,
                    search_patterns,
                )
            )

        for future in as_completed(tasks):
            try:
                result = future.result()
                if result is not None:
                    results.append(result)
            except Exception as e:
                logger.exception("Extraction failed", exc_info=e)

    logger.info(f"Extracted {len(results)} sections successfully")
    return results
