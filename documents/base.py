import copy
import time
from abc import ABCMeta, abstractmethod
from datetime import datetime


class Document(metaclass=ABCMeta):
    def __init__(
        self,
        file_path: str,
        doc_text: str,
        extraction_method: str,
        metadata,
        search_patterns: dict,
    ):
        self.file_path = file_path
        self.doc_text = doc_text
        self.extraction_method = extraction_method
        self.metadata = metadata
        self.search_patterns = search_patterns

        self.log_cache = []
        self.extracted_content = {}

    def get_excerpt(self, form_type: str):
        """
        Template method:
        - prepare text
        - iterate sections
        - extract content
        - return structured result
        """
        start_time = time.process_time()
        self.prepare_text()
        prep_time = time.process_time() - start_time

        for section_def in self.search_patterns.get(form_type, []):
            section_start = time.process_time()

            section_metadata = copy.copy(self.metadata)
            section_name = section_def["itemname"]
            search_pairs = section_def["html"]

            (
                text_extract,
                extraction_summary,
                start_text,
                end_text,
                warnings,
            ) = self.extract_section(search_pairs)

            elapsed = time.process_time() - section_start

            section_metadata.section_name = section_name
            section_metadata.extraction_method = self.extraction_method
            section_metadata.endpoints = [
                start_text[:100] if start_text else None,
                end_text[:100] if end_text else None,
            ]
            section_metadata.warnings = warnings
            section_metadata.time_elapsed = round(prep_time + elapsed, 1)
            section_metadata.section_end_time = datetime.utcnow().isoformat()

            if text_extract:
                section_metadata.section_n_characters = len(text_extract)
                self.extracted_content[section_name] = {
                    "content": text_extract,
                    "metadata": section_metadata,
                }
                self.log_cache.append(
                    ("DEBUG", f"Extracted section: {section_name}")
                )
            else:
                self.log_cache.append(
                    ("WARNING", f"No content for section: {section_name}")
                )

        return self.extracted_content, self.log_cache

    @abstractmethod
    def prepare_text(self):
        pass

    @abstractmethod
    def extract_section(self, search_pairs):
        pass
