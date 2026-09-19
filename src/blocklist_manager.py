import os
import time

import httpx
from colorama import Fore, Style

from src.logger import get_logger

logger = get_logger(__name__)


class BlocklistManager:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.shadow_blocklist: set[str] = set()

    def prime(self, blocklist: set[str]) -> bool:
        new_domains = [d for d in blocklist if d not in self.shadow_blocklist]
        if not new_domains:
            logger.info("No new domains to prime.")
            return True

        url = f"{self.base_url}/api/blocklist/custom"
        headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
        payload = {"domains": new_domains}

        logger.info(
            f"Priming blocklist at {Fore.BLUE}{url}{Style.RESET_ALL} "
            f"with {len(new_domains)} new domains..."
        )

        try:
            response = httpx.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                self.shadow_blocklist.update(new_domains)
                return True
            else:
                logger.error(
                    f"Failed to prime blocklist: {response.status_code} - "
                    f"{response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error connecting to API: {e}")
            return False

    def load_local(self, filepath: str = "blocklist.txt") -> set[str]:
        """Reads hostnames from blocklist.txt, ignoring comments and empty lines."""
        if not os.path.exists(filepath):
            logger.warning(
                f"Error: {Style.BRIGHT}{Fore.CYAN}{filepath}{Style.RESET_ALL} "
                "not found."
            )
            return set()

        with open(filepath) as f:
            hostnames: set[str] = set()
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                hostnames.add(line)
            return hostnames

    def fetch_and_save(self, filepath: str = "blocklist.txt") -> None:
        url = f"{self.base_url}/api/blocklist/custom"
        headers = {"X-API-Key": self.api_key}

        try:
            response = httpx.get(url, headers=headers)
            if response.status_code == 200:
                fetched_domains = response.json().get("domains", [])
                local_domains = self.load_local(filepath)
                merged_domains = sorted(list(set(fetched_domains) | local_domains))

                self.shadow_blocklist = set(merged_domains)

                with open(filepath, "w") as f:
                    f.write("# Title: yeti-dabble custom blocklist\n")
                    f.write(
                        "# Description: dynamically curated blocklist, "
                        "maintained at github.com/rm-hull/yeti-dabble\n"
                    )
                    f.write(
                        "# Last modified: "
                        + time.strftime("%d %b %Y %H:%M UTC", time.gmtime())
                        + "\n"
                    )
                    f.write(
                        "# Notes: raise an issue/create a PR to add/remove entries "
                        "from this blocklist\n"
                    )
                    f.write("#\n")
                    for domain in merged_domains:
                        f.write(f"{domain}\n")
                logger.info(
                    f"Successfully updated {Style.BRIGHT}{Fore.CYAN}{filepath}"
                    f"{Style.RESET_ALL} with {len(merged_domains)} domains "
                    f"({len(fetched_domains)} fetched, {len(local_domains)} local)."
                )
            else:
                logger.error(
                    f"Failed to fetch blocklist: {response.status_code} - "
                    f"{response.text}"
                )
        except Exception as e:
            logger.error(f"Error fetching/writing blocklist: {e}")
