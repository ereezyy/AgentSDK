import asyncio
import sys
import os
import json
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

MOCK_RESPONSE_AUCTION_OPEN = json.dumps([{"id": "auction1", "description": "test", "min_bid_cents": 100}]).encode()
MOCK_RESPONSE_CREDITS_TOPUP = json.dumps({"new_balance_cents": 1000}).encode()
MOCK_RESPONSE_BID = json.dumps({"bid_id": "bid123"}).encode()
MOCK_RESPONSE_SETTLE = json.dumps({"net_payout_cents": 80, "syndicate_tax_cents": 20}).encode()
MOCK_RESPONSE_STATUS = json.dumps({"status": "open"}).encode()

async def app(scope, receive, send):
    if scope['type'] == 'http':
        path = scope['path']

        status = 200
        body = b"{}"

        if path == "/syndicate/auction/open":
            body = MOCK_RESPONSE_AUCTION_OPEN
        elif path == "/syndicate/credits/topup":
            body = MOCK_RESPONSE_CREDITS_TOPUP
        elif "/bid" in path:
            body = MOCK_RESPONSE_BID
        elif "/settle" in path:
            body = MOCK_RESPONSE_SETTLE
        elif "/status" in path:
            body = MOCK_RESPONSE_STATUS

        await send({'type': 'http.response.start', 'status': status, 'headers': [[b'content-type', b'application/json']]})
        await send({'type': 'http.response.body', 'body': body})

class MockAsyncClient(httpx.AsyncClient):
    def __init__(self, *args, **kwargs):
        kwargs['transport'] = httpx.ASGITransport(app=app)
        super().__init__(*args, **kwargs)

async def test_functional():
    print("Starting functional tests...")
    with patch('httpx.AsyncClient', side_effect=MockAsyncClient):
        async with SyndicateClient(api_key="test", base_url="http://test") as client:
            # Test get_open_leads
            leads = await client.get_open_leads()
            assert len(leads) == 1
            assert leads[0]["id"] == "auction1"
            print("✓ get_open_leads passed")

            # Test topup_credits
            topup = await client.topup_credits(agent_id="agent1")
            assert topup["new_balance_cents"] == 1000
            print("✓ topup_credits passed")

            # Test place_bid
            bid = await client.place_bid(auction_id="auction1", agent_id="agent1", bid_amount_cents=120)
            assert bid["bid_id"] == "bid123"
            print("✓ place_bid passed")

            # Test settle_auction
            settle = await client.settle_auction(auction_id="auction1")
            assert settle["net_payout_cents"] == 80
            print("✓ settle_auction passed")

            # Test get_auction_status
            status = await client.get_auction_status(auction_id="auction1")
            assert status["status"] == "open"
            print("✓ get_auction_status passed")

    print("All functional tests passed!")

if __name__ == "__main__":
    asyncio.run(test_functional())
