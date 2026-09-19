from pathlib import Path

from pytest_httpx import HTTPXMock

from src.blocklist_manager import BlocklistManager


def test_load_local(tmp_path: Path) -> None:
    blocklist_file = tmp_path / "blocklist.txt"
    blocklist_file.write_text(
        "# Title: test\n\nexample.com\n  sub.example.com  \n# comment line\ntest.org\n"
    )

    manager = BlocklistManager(api_key="test-key", base_url="https://api.example.com")
    domains = manager.load_local(str(blocklist_file))

    assert domains == {"example.com", "sub.example.com", "test.org"}


def test_load_local_missing() -> None:
    manager = BlocklistManager(api_key="test-key", base_url="https://api.example.com")
    domains = manager.load_local("nonexistent-file.txt")
    assert domains == set()


def test_prime_success(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://api.example.com/api/blocklist/custom",
        method="POST",
        status_code=200,
    )

    manager = BlocklistManager(api_key="test-key", base_url="https://api.example.com")
    success = manager.prime({"domain1.com", "domain2.com"})

    assert success is True
    assert manager.shadow_blocklist == {"domain1.com", "domain2.com"}


def test_prime_no_new_domains(httpx_mock: HTTPXMock) -> None:
    manager = BlocklistManager(api_key="test-key", base_url="https://api.example.com")
    manager.shadow_blocklist = {"domain1.com"}

    success = manager.prime({"domain1.com"})
    assert success is True
    assert len(httpx_mock.get_requests()) == 0


def test_fetch_and_save_merges_local(tmp_path: Path, httpx_mock: HTTPXMock) -> None:
    blocklist_file = tmp_path / "blocklist.txt"
    blocklist_file.write_text("local-domain.com\nshared-domain.com\n")

    httpx_mock.add_response(
        url="https://api.example.com/api/blocklist/custom",
        method="GET",
        status_code=200,
        json={"domains": ["remote-domain.com", "shared-domain.com"]},
    )

    manager = BlocklistManager(api_key="test-key", base_url="https://api.example.com")
    manager.fetch_and_save(str(blocklist_file))

    # Verify local file contents after fetch_and_save
    content = blocklist_file.read_text()
    assert "local-domain.com" in content
    assert "remote-domain.com" in content
    assert "shared-domain.com" in content

    # Verify shadow blocklist is updated with merged set
    assert manager.shadow_blocklist == {
        "local-domain.com",
        "remote-domain.com",
        "shared-domain.com",
    }
