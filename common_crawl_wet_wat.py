# 2025. Common Crawl WET/WAT extractor

import argparse
import logging
import requests
import gzip

from enum import Enum
from io import BytesIO
from pydantic import validate_call, Field, StringConstraints
from typing import Annotated


class CommonCrawlFileType(str, Enum):
    WET = "wet"
    WAT = "wat"


# Get a logger instance
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Step 1: Get the list of available crawls
@validate_call
def get_available_crawls(
    most_recent_crawls: Annotated[
        int, Field(gt=0, description="Number of recent crawls to show")
    ],
):
    """Fetch list of available CommonCrawl crawls"""
    url = "https://index.commoncrawl.org/collinfo.json"
    response = requests.get(url)
    crawls = response.json()

    logger.info("Recent crawls:")
    for crawl in crawls[:most_recent_crawls]:  # Show 5 most recent
        logger.info(f"  {crawl['id']} - {crawl['name']}")

    return crawls


# Step 2: Get WET/WAT file paths for a specific crawl
@validate_call
def get_file_paths(
    crawl_id: Annotated[
        str, Field(default="CC-MAIN-2024-10", min_length=1, description="Crawl ID")
    ],
    file_type: CommonCrawlFileType = CommonCrawlFileType.WET,
    # file_type=Annotated[CommonCrawlFileType, Field(default=CommonCrawlFileType.WET)],
):
    """
    Get paths for WET or WAT files

    Args:
        crawl_id: The crawl identifier (e.g., 'CC-MAIN-2024-10')
        file_type: 'wet' for text or 'wat' for metadata
    """
    base_url = f"https://data.commoncrawl.org/crawl-data/{crawl_id}/"
    paths_file = f"{file_type.value}.paths.gz"

    url = base_url + paths_file
    response = requests.get(url)

    # Decompress the gzipped paths file
    with gzip.open(BytesIO(response.content), "rt") as f:
        paths = [line.strip() for line in f]

    logger.info(f"Found {len(paths)} {file_type.value.upper()} files")
    return paths


# Step 3: Download and read a specific WET/WAT file
@validate_call
def download_file(
    file_path: Annotated[str, Field(min_length=1, description="WET or WAT file path")],
    max_records: Annotated[int, Field(ge=1, description="Maximum number of records")],
):
    """
    Download and parse a WET or WAT file

    Args:
        file_path: Path to the file (from get_file_paths)
        max_records: Maximum number of records to read
    """
    url = f"https://data.commoncrawl.org/{file_path}"
    logger.info(f"Downloading: {url}")

    response = requests.get(url, stream=True)

    # WET/WAT files are gzipped WARC format
    with gzip.open(
        BytesIO(response.content), "rt", encoding="utf-8", errors="ignore"
    ) as f:
        content = f.read()

    # Split by WARC record separator
    records = content.split("WARC/1.0")

    logger.info(f"\nFound {len(records)} records")
    logger.info("\n" + "=" * 80)

    # Display first few records
    for i, record in enumerate(records[1 : max_records + 1], 1):
        logger.info(f"\n--- Record {i} ---")
        # Show first 500 characters of each record
        logger.info(record[:500])
        logger.info("...")

    return records


@validate_call
def run(file_type: CommonCrawlFileType):
    logger.info("CommonCrawl WET/WAT File Downloader\n")

    # 1. List available crawls
    most_recent_crawls = 5
    crawls = get_available_crawls(most_recent_crawls=most_recent_crawls)

    # 2. Use most recent crawl
    latest_crawl = crawls[0]["id"]
    logger.info(f"\nUsing crawl: {latest_crawl}\n")

    # 3. Get WET file paths (use 'wat' for WAT files)
    wet_paths = get_file_paths(crawl_id=latest_crawl, file_type=file_type)

    # 4. Download first WET file (just a sample)
    logger.info(f"\nDownloading first WET file as example...\n")
    records = download_file(file_path=wet_paths[0], max_records=3)

    logger.info(f"Downloaded {len(records)} records")


# Example usage
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Common crawl wet/wat file downloader."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--wat", action="store_true", help="Download wat file.")
    group.add_argument("-e", "--wet", action="store_true", help="Download wet file.")

    args = parser.parse_args()
    if args.wat:
        file_type = CommonCrawlFileType.WAT
    else:
        assert args.wet
        file_type = CommonCrawlFileType.WET
    run(file_type)
