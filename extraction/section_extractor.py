# extraction/section_extractor.py
import logging
from documents.html_document import HtmlDocument
from data_access.sec_client import safe_get
import json

logger = logging.getLogger(__name__)

def process_filing(metadata, search_patterns):
    """
    Process a single SEC filing using provided Metadata object.
    """

    logger.info(
        f"Processing {metadata.ticker} | "
        f"{metadata.form_type} | {metadata.filed_at}"
    )

    url = metadata.sec_index_url  # ✅ FIX 1: lấy URL từ metadata

    response = safe_get(url)
    if response is None:
        logger.error(f"Failed to fetch filing: {url}")
        return False

    html_text = response.text
    if not html_text:
        logger.error(f"No HTML content for filing: {url}")
        return False

    patterns = search_patterns.get(metadata.form_type, [])
    if not patterns:
        logger.warning(f"No search patterns for form type: {metadata.form_type}")
        return False

    doc = HtmlDocument(
        file_path=url,
        doc_text=html_text,
        extraction_method="regex",
        metadata=metadata,
        search_patterns=patterns  # ✅ BẮT BUỘC
    )

    extracted_text = doc.get_excerpt(search_patterns=patterns)
    
    if not extracted_text:
        logger.warning(f"No section extracted for {metadata.metadata_file_name}")
        return None

    return {
        "cik": metadata.cik,
        "ticker": metadata.ticker,
        "form_type": metadata.form_type,
        "filed_at": metadata.filed_at,
        "accession_number": metadata.accession_number,
        "section": metadata.section_name,
        "content": extracted_text,
        "extraction_method": metadata.extraction_method,
        "warnings": json.dumps(metadata.warnings),
    }

