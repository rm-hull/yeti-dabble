import time

from src.debouncer import Debouncer


def test_debouncer_aggregates_and_triggers() -> None:
    results: list[set[str]] = []

    def callback(domains: set[str]) -> None:
        results.append(domains)

    debouncer = Debouncer(interval_seconds=0.1, callback=callback)

    debouncer.add("domain1.com")
    debouncer.add("domain2.com")
    debouncer.add("domain1.com")  # duplicate

    # Wait for timer to expire
    time.sleep(0.25)

    assert len(results) == 1
    assert results[0] == {"domain1.com", "domain2.com"}


def test_debouncer_flush() -> None:
    results: list[set[str]] = []

    def callback(domains: set[str]) -> None:
        results.append(domains)

    debouncer = Debouncer(interval_seconds=1.0, callback=callback)

    debouncer.add("domain1.com")
    debouncer.add("domain3.com")

    # Flush immediately before timer expires
    debouncer.flush()

    assert len(results) == 1
    assert results[0] == {"domain1.com", "domain3.com"}

    # Ensure timer was cancelled and won't trigger again later
    time.sleep(1.2)
    assert len(results) == 1
