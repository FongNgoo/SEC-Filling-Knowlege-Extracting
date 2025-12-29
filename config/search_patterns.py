# config/search_patterns.py
import json
import os
import copy
import logging

logger = logging.getLogger(__name__)

def load_search_patterns(json_path: str) -> dict:
    if not os.path.exists(json_path):
        logger.error(f"Search terms file not found: {json_path}")
        raise FileNotFoundError(json_path)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            search_terms = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in file {json_path}: {e}")
        raise

    if not isinstance(search_terms, dict) or not search_terms:
        raise ValueError("Search terms JSON must be a non-empty dictionary")

    search_terms_regex = copy.deepcopy(search_terms)

    for filing, sections in search_terms.items():
        if not isinstance(sections, list):
            logger.warning(f"Invalid sections format for filing {filing}")
            continue

        for sec_idx, section in enumerate(sections):
            if not isinstance(section, dict) or "html" not in section:
                logger.warning(f"Invalid section structure: {filing}[{sec_idx}]")
                continue

            for pat_idx, pattern in enumerate(section["html"]):
                if not isinstance(pattern, dict):
                    continue
                if not {"start", "end"}.issubset(pattern):
                    logger.warning(
                        f"Missing start/end in pattern: {filing}[{sec_idx}][{pat_idx}]"
                    )
                    continue

                for key in ("start", "end"):
                    regex_string = pattern[key]
                    if not isinstance(regex_string, str):
                        continue

                    regex_string = regex_string.replace("_", r"\s{,5}")
                    regex_string = regex_string.replace("\n", r"\n")

                    search_terms_regex[filing][sec_idx]["html"][pat_idx][key] = regex_string

    logger.info(
        "Loaded search patterns for filings: %s",
        ", ".join(search_terms_regex.keys())
    )

    return search_terms_regex
