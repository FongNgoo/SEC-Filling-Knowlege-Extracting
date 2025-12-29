# extraction/batch_processor.py
import logging
from concurrent.futures import ThreadPoolExecutor
from extraction.section_extractor import process_filing
from documents.metadata import Metadata

logger = logging.getLogger(__name__)

def process_filings_batch(filings_df, search_patterns, max_workers=4):
    tasks = []

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
                    search_patterns
                )
            )

        for t in tasks:
            t.result()
