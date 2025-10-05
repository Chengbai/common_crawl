# 2025. Common Crawl dataset extractor.

import logging
import json

from bs4 import BeautifulSoup
from pydantic import validate_call, Field
from tqdm import tqdm
from typing import Annotated
from warcio.archiveiterator import ArchiveIterator


# Get a logger instance
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@validate_call
def extract_html_from_warc(
    warc_file_path: Annotated[str, Field(description="Path to the WARC file")],
    max_samples: Annotated[
        int, Field(gt=0, description="Max number of samples to extract")
    ],
) -> list[dict]:
    """
    Parses a Common Crawl WARC file and extracts HTML content from 'response' records.
    Args:
        warc_file_path (str): The path to the WARC file (can be gzipped).
        max_samples (int): Maximum number of HTML samples
    Returns:
        list: A list of dictionaries, where each dictionary contains
              'url' and 'html_content' for extracted HTML records.
    """
    extracted_data = []

    # Open the WARC file, handling gzipped files automatically
    with open(warc_file_path, "rb") as stream:
        with tqdm(unit="B", unit_scale=True, desc="Processing stream") as pbar:

            for idx, record in enumerate(ArchiveIterator(stream)):
                # We are interested in 'response' records that contain actual web page content
                # logger.info(f"record type : {record.rec_type}")

                pbar.update(1)
                pbar.set_description(f"Processing item {idx}")

                if record.rec_type == "response":
                    # logger.info(f"record.http_headers: {record.http_headers}")

                    # Check if the content type is HTML
                    content_type = record.http_headers.get_header("Content-Type")
                    if content_type and "text/html" in content_type:
                        try:
                            # Read the payload (HTML content)
                            html_bytes = record.content_stream().read()
                            # Decode the bytes to a string
                            html_content = html_bytes.decode("utf-8", errors="ignore")

                            # Optionally, use BeautifulSoup to further process or clean the HTML
                            soup = BeautifulSoup(html_content, "xml")
                            # soup = BeautifulSoup(html_content, "lxml")
                            # soup = BeautifulSoup(html_content, "html.parser")
                            cleaned_html = (
                                soup.prettify()
                            )  # Example: pretty-print the HTML

                            extracted_data.append(
                                {
                                    "url": record.rec_headers.get_header(
                                        "WARC-Target-URI"
                                    ),
                                    "html_content": cleaned_html,  # html_content
                                }
                            )

                            if len(extracted_data) >= max_samples:
                                break

                        except Exception as e:
                            logger.error(
                                f"Error processing record for {record.rec_headers.get_header('WARC-Target-URI')}: {e}"
                            )
    return extracted_data


# Save the html data into a give file.
@validate_call
def save_html_data(
    extracted_data: Annotated[list[dict], Field(min_length=1)],
    output_file: Annotated[str, Field(..., description="output file path")],
):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, ensure_ascii=True)


def run():
    # Download data to local from https://data.commoncrawl.org/commoncrawl/crawl-data/CC-MAIN-2013-20/segments/1368696381249/warc/CC-MAIN-20130516092621-00000-ip-10-60-113-184.ec2.internal.warc.gz
    warc_file_path = "/Users/chengbai/ml/dataset/common_crawl/CC-MAIN-20130516092621-00000-ip-10-60-113-184.ec2.internal.warc"
    max_samples = 2
    extracted_html_pages = extract_html_from_warc(
        warc_file_path=warc_file_path, max_samples=max_samples
    )
    logger.info(f"Extracted {len(extracted_html_pages)} from {warc_file_path}")

    # Save the extracted HTML content to a file
    output_file = "/tmp/common_crawl_extracted_data.json"
    save_html_data(extracted_data=extracted_html_pages, output_file=output_file)
    logger.info(
        f"Save the extracted {len(extracted_html_pages)} html pages to {output_file}"
    )


if __name__ == "__main__":
    run()
