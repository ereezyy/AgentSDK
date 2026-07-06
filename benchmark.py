import asyncio
import time
import sys
import os
from unittest.mock import patch

try:
    import httpx
except ImportError:
    # Try to find httpx in the environment if not directly available
    # This is a fallback for the specific environment this script was developed in
    POETRY_VENV_PACKAGES = "/home/jules/.local/share/pipx/venvs/poetry/lib/python3.12/site-packages"
    if os.path.exists(POETRY_VENV_PACKAGES):
        sys.path.append(POETRY_VENV_PACKAGES)
        import httpx
    else:
        print("Error: httpx is not installed. Please install it with 'pip install httpx'.")
        sys.exit(1)

from client import SyndicateClient

async def app(scope, receive, send):
    if scope['type'] == 'lifespan':
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                await send({'type': 'lifespan.shutdown.complete'})
                return

    if scope['type'] == 'http':
        await send({'type': 'http.response.start', 'status': 200, 'headers': [[b'content-type', b'application/json']]})
        await send({'type': 'http.response.body', 'body': b'[]'})

class MockAsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        kwargs['transport'] = httpx.ASGITransport(app=app)
        super().__init__(*args, **kwargs)

async def run_comparison():
    N = 1000

    print(f"Running comparison benchmark with {N} concurrent requests...")
    with patch('httpx.AsyncClient', side_effect=MockAsyncClient):
        # Optimized: single shared client with raised connection limits,
        # fired concurrently via asyncio.gather to exercise the pool.
        async with SyndicateClient(api_key="test", base_url="http://test") as client:
            start = time.perf_counter()
            await asyncio.gather(*(client.get_open_leads() for _ in range(N)))
            opt_duration = time.perf_counter() - start
            print(f"Optimized Duration: {opt_duration:.4f}s")

        # Baseline: a fresh client per request, also fired concurrently so the
        # comparison isolates client/pool reuse rather than sequential latency.
        headers = {"X-Agent-API-Key": "test", "Content-Type": "application/json"}

        async def baseline_request():
            async with httpx.AsyncClient(headers=headers, transport=httpx.ASGITransport(app=app)) as client:
                await client.get("http://test/syndicate/auction/open")

        start = time.perf_counter()
        await asyncio.gather(*(baseline_request() for _ in range(N)))
        base_duration = time.perf_counter() - start
        print(f"Baseline Duration: {base_duration:.4f}s")

        improvement = (base_duration - opt_duration) / base_duration * 100
        print(f"Performance Improvement: {improvement:.2f}%")

if __name__ == "__main__":
    asyncio.run(run_comparison())
