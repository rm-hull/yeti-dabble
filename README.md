# Yeti-dabble

Yeti-dabble is a real-time monitoring and synchronization daemon designed to bridge domain event streams with custom blocklists. 

### Why Yeti-Dabble Exists

When managing infrastructure security, DNS filtering, or threat intelligence feeds, maintaining static blocklists is inefficient and slow. Yeti-dabble solves this by:

1. **Priming & Syncing**: Reading local blocklists (from `blocklist.txt`) and initializing remote security/API endpoints on startup.
2. **Real-Time SSE Streaming**: Listening continuously to a Server-Sent Events (SSE) feed for incoming domain events.
3. **Smart Debouncing**: Aggregating rapid-fire burst events over a sliding window (e.g., 5 seconds) to prevent API rate-limiting or redundant synchronization requests.
4. **Persistent Reconciliation**: Fetching the latest curated state from the remote API and saving it back to disk upon shutdown, keeping local files and remote state in sync.

## Setup

1. Ensure you have [uv](https://github.com/astral-sh/uv) installed.
2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and add your configuration:
   ```env
   DOT_BLOCK_API_KEY=your_actual_api_key_here
   DOT_BLOCK_BASE_URL=https://your-base-url.com
   ```

## Running

The script reads hostnames from `blocklist.txt` and primes them to the API before starting the SSE stream for specified domains.

Run the script using `uv`:

```bash
uv run yeti-dabble --domains=example.com,test.org
```

This will automatically create a virtual environment, install the dependencies, and start the script.

## Development

- **Linting & Formatting**: `ruff`
- **Type Checking**: `mypy`

To run checks using `uv`:

```bash
uv run ruff check src/
uv run ruff format src/
uv run mypy src/
```
