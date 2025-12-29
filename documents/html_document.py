import re
import time
import json
import logging
from statistics import median
from bs4 import BeautifulSoup, NavigableString, Comment

from documents.base import Document

logger = logging.getLogger(__name__)


class HtmlDocument(Document):
    def __init__(
        self,
        file_path,
        doc_text,
        extraction_method,
        metadata,
        search_patterns
    ):
        super().__init__(
            file_path=file_path,
            doc_text=doc_text,
            extraction_method=extraction_method,
            metadata=metadata,
            search_patterns=search_patterns
        )

    # ==========================================================
    # Preprocessing
    # ==========================================================

    def prepare_text(self):
        html_text = self.doc_text

        html_text = re.sub(r"<\s", "<", html_text)
        html_text = re.sub(r"(<small>|</small>)", "", html_text, flags=re.IGNORECASE)
        html_text = re.sub(
            r"(\nITEM\s{1,10}[1-9])", r"<br>\1", html_text, flags=re.IGNORECASE
        )

        start_time = time.process_time()
        try:
            self.soup = BeautifulSoup(html_text, "lxml")
        except Exception:
            self.soup = BeautifulSoup(html_text, "html.parser")

        parsing_time = time.process_time() - start_time
        self.log_cache.append(
            (
                "DEBUG",
                f"HTML parsed in {parsing_time:.2f}s | "
                f"{len(html_text):,} chars | {len(self.soup.find_all()):,} nodes",
            )
        )

        if self.soup.find_all():
            if len(html_text) / len(self.soup.find_all()) > 500:
                html_text = re.sub(r"\n\n", "<br>", html_text)
                self.soup = BeautifulSoup(html_text, "html.parser")

        for table in self.soup.find_all("table"):
            if self.should_remove_table(table):
                table.replace_with(self.table_to_json(table))

        self.plaintext = self._dom_to_plaintext()

    # ==========================================================
    # Public API (NEW – IMPORTANT)
    # ==========================================================

    def get_excerpt(self, search_patterns, skip_existing_excerpts=False):
        """
        Extract all defined sections for a filing using provided search patterns.
        """
        start_time = time.process_time()
        self.prepare_text()

        for section in search_patterns:
            section_name = section.get("itemname", "unknown_section")
            search_pairs = section.get("html", [])

            text, summary, start_text, end_text, warnings = self.extract_section(
                search_pairs
            )

            metadata = self.metadata
            metadata.section_name = section_name
            metadata.extraction_method = self.extraction_method
            metadata.endpoints = [start_text, end_text]
            metadata.warnings = warnings
            metadata.time_elapsed = round(time.process_time() - start_time, 2)

            if text:
                metadata.section_n_characters = len(text)
                self.extracted_content[section_name] = text
                self.log_cache.append(
                    ("INFO", f"Extracted section [{section_name}] ({len(text)} chars)")
                )
            else:
                self.log_cache.append(
                    ("WARNING", f"Failed to extract section [{section_name}]")
                )

        return self.extracted_content

    # ==========================================================
    # Core extraction logic
    # ==========================================================

    def extract_section(self, search_pairs):
        start_text, end_text = None, None
        warnings = []
        text_extract = None
        longest_match = 0

        for pair in search_pairs:
            pattern = pair["start"] + r"[\s\S]*?" + pair["end"]
            matches = re.findall(pattern, self.plaintext, re.IGNORECASE | re.DOTALL)

            if not matches:
                continue

            for match in matches:
                if isinstance(match, tuple):
                    warnings.append("Regex groups detected; please fix patterns")
                    continue

                if len(match) > longest_match:
                    text_extract = match.strip()
                    longest_match = len(match)

            if text_extract:
                lines = text_extract.split("\n")
                start_text = lines[0][:100]
                end_text = lines[-1][:100]
                break

        if not text_extract:
            warnings.append("Section extraction failed for HTML document")
            return None, "html_document_failed", None, None, warnings

        text_extract = re.sub(
            r"\n\s{,5}Table of Contents\n",
            "",
            text_extract,
            flags=re.IGNORECASE,
        )

        return text_extract, "html_document", start_text, end_text, warnings

    # ==========================================================
    # Helpers
    # ==========================================================

    def should_remove_table(self, table):
        char_lengths = [len(t) for t in table.stripped_strings if t]
        contains_item = any(
            re.search(r"ITEM\s*\d+[A-Z]?", t, re.IGNORECASE)
            for t in table.stripped_strings
        )

        if not char_lengths:
            return False

        return len(char_lengths) > 5 and median(char_lengths) < 30 and not contains_item

    def table_to_json(self, table):
        rows = []
        headers = []

        header_row = table.find("tr")
        if header_row:
            headers = [
                h.get_text(strip=True)
                for h in header_row.find_all("th")
                if h.get_text(strip=True)
            ]

        for row in table.find_all("tr"):
            cells = [
                c.get_text(strip=True)
                for c in row.find_all(["td", "th"])
                if c.get_text(strip=True)
            ]
            if not cells:
                continue

            if headers and len(headers) == len(cells):
                rows.append(dict(zip(headers, cells)))
            else:
                rows.append(cells)

        return json.dumps(rows, ensure_ascii=False)

    def _dom_to_plaintext(self):
        document_string = ""
        is_in_paragraph = True
        element = self.soup.find()

        while element:
            if self.is_line_break(element) or element.next_element is None:
                if is_in_paragraph:
                    is_in_paragraph = False
                    document_string += "\n\n"
            else:
                if isinstance(element, NavigableString) and not isinstance(
                    element, Comment
                ):
                    text = re.sub(r"\s+", " ", element.strip())
                    if text:
                        if not is_in_paragraph:
                            is_in_paragraph = True
                            document_string += text
                        else:
                            document_string += " " + text
            element = element.next_element

        document_string = re.sub(r"\n{3,}", "\n\n", document_string)
        return document_string.strip()

    def is_line_break(self, element):
        block_tags = {
            "p",
            "div",
            "br",
            "hr",
            "tr",
            "table",
            "form",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        }

        is_block = element.name in block_tags
        if is_block and element.parent and element.parent.name == "td":
            if len(element.parent.find_all(element.name)) == 1:
                is_block = False

        is_styled_block = False
        if hasattr(element, "attrs") and "style" in element.attrs:
            is_styled_block = bool(
                re.search(r"margin-(top|bottom)", element["style"])
            )

        return is_block or is_styled_block
