import json
import logging

logger = logging.getLogger(__name__)

class Metadata:
    def __init__(self, cik, ticker, form_type, filed_at, accession_number, document_url):
        self.metadata_file_name = f"{cik}_{accession_number.replace('-', '')}"
        self.cik = cik
        self.ticker = ticker
        self.form_type = form_type
        self.filed_at = filed_at
        self.accession_number = accession_number
        self.sec_index_url = document_url
        self.section_name = None
        self.extraction_method = None
        self.endpoints = [None, None]
        self.warnings = []
        self.time_elapsed = 0
        self.section_end_time = None
        self.section_n_characters = 0
        self.output_file = None

    def save_to_json(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(vars(self), f, indent=2)

    def save_to_db(self):
        logger.info(f"Would save metadata to DB for {self.metadata_file_name}")