import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="SEC Filing Scraper & Section Extractor"
    )

    parser.add_argument(
        "--ciks",
        type=str,
        required=True,
        help="Comma-separated list of CIKs (e.g. 0000320193,0000789019)",
    )

    parser.add_argument(
        "--forms",
        type=str,
        default="10-K,10-Q",
        help="Comma-separated SEC form types",
    )

    parser.add_argument(
        "--start-date",
        type=str,
        help="Start filing date (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--end-date",
        type=str,
        help="End filing date (YYYY-MM-DD)",
    )

    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Parallel workers for extraction",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )

    return parser.parse_args()
