import argparse
import json
import os

import httpx
from colorama import Fore, Style
from dotenv import load_dotenv

from src.logger import get_logger

from .blocklist_manager import BlocklistManager
from .debouncer import Debouncer

# Load environment variables from .env
load_dotenv()

logger = get_logger(__name__)

API_KEY = os.getenv("DOT_BLOCK_API_KEY")
BASE_URL = os.getenv("DOT_BLOCK_BASE_URL")


def listen_to_sse(domains: list[str], manager: BlocklistManager) -> None:
    if not API_KEY or not BASE_URL:
        logger.error("DOT_BLOCK_API_KEY or DOT_BLOCK_BASE_URL not found in .env file.")
        return

    # Initialize debouncer with a 5-second window
    debouncer = Debouncer(interval_seconds=5.0, callback=manager.prime)

    # Assuming API handles comma-separated domains or similar
    domain_query: str = ",".join(domains)
    sse_url: str = (
        f"{BASE_URL.rstrip('/')}/api/events?domain={domain_query}&blocked=false"
    )
    headers: dict = {"X-API-Key": API_KEY, "Accept": "text/event-stream"}

    logger.info(f"Connecting to {Fore.BLUE}{sse_url}{Style.RESET_ALL}...")

    try:
        with httpx.stream("GET", sse_url, headers=headers, timeout=None) as response:
            if response.status_code != 200:
                error_msg = response.read().decode("utf-8")
                logger.error(f"Failed to connect: {response.status_code} - {error_msg}")
                return

            logger.info("Connected. Listening for events...")
            for line in response.iter_lines():
                if line.startswith("data:"):
                    try:
                        data: dict = json.loads(line[len("data:") :].strip())
                        domain = data.get("domain")
                        query_type = data.get("queryType")
                        if domain:
                            logger.info(
                                f"Event received for {query_type} domain: "
                                f"{Fore.MAGENTA}{domain}{Style.RESET_ALL}"
                            )
                            debouncer.add(domain)
                        else:
                            logger.warning(f"Received event without domain: {data}")
                    except json.JSONDecodeError:
                        logger.debug(f"Received non-JSON data: {line}")
                elif line.strip() == "":
                    continue
    except KeyboardInterrupt:
        logger.warning("Stopping...")
        debouncer.flush()
        manager.fetch_and_save()


def main() -> None:
    parser = argparse.ArgumentParser(description="SSE Client for blocklist monitoring")
    parser.add_argument(
        "--domains", required=True, help="Comma-separated list of domains to monitor"
    )
    args = parser.parse_args()

    domains = [d.strip() for d in args.domains.split(",")]

    if not API_KEY or not BASE_URL:
        logger.error("DOT_BLOCK_API_KEY or DOT_BLOCK_BASE_URL not found in .env file.")
        exit(1)

    manager = BlocklistManager(API_KEY, BASE_URL)
    blocklist = manager.load_local()
    logger.info(
        f"Loaded {len(blocklist)} hostnames from {Style.BRIGHT}{Fore.CYAN}"
        f"blocklist.txt{Style.RESET_ALL}."
    )

    if manager.prime(blocklist):
        listen_to_sse(domains, manager)
    else:
        logger.error("Failed to prime blocklist, exiting.")


if __name__ == "__main__":
    main()
