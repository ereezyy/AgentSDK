import unittest
import os
from unittest.mock import patch, MagicMock, AsyncMock

from client import SyndicateClient

class TestSyndicateClient(unittest.IsolatedAsyncioTestCase):
    def test_init_default(self):
        client = SyndicateClient()
        self.assertEqual(client.api_key, "syndicate_agent_v0.1_key")
        self.assertEqual(client.base_url, "http://localhost:8422/api/v2")
        self.assertEqual(client.headers["X-Agent-API-Key"], "syndicate_agent_v0.1_key")
        self.assertEqual(client.headers["Content-Type"], "application/json")

    def test_init_custom(self):
        client = SyndicateClient(api_key="custom_key", base_url="https://api.example.com/")
        self.assertEqual(client.api_key, "custom_key")
        self.assertEqual(client.base_url, "https://api.example.com")
        self.assertEqual(client.headers["X-Agent-API-Key"], "custom_key")

    @patch.dict(os.environ, {"SYNDICATE_API_KEY": "env_key"})
    def test_init_env_var(self):
        client = SyndicateClient()
        self.assertEqual(client.api_key, "env_key")
        self.assertEqual(client.headers["X-Agent-API-Key"], "env_key")

    @patch('httpx.AsyncClient')
    async def test_get_open_leads(self, mock_async_client):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "auction1", "description": "Lead 1", "min_bid_cents": 100}]
        mock_response.raise_for_status = MagicMock()

        # AsyncClient is used as a context manager `async with httpx.AsyncClient(...) as client:`
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response

        # Setup context manager mock
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        client = SyndicateClient()
        leads = await client.get_open_leads()

        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["id"], "auction1")
        mock_client_instance.get.assert_called_once_with(f"{client.base_url}/syndicate/auction/open")
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()


    @patch('httpx.AsyncClient')
    async def test_topup_credits(self, mock_async_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "credits_added": 100}
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response

        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        client = SyndicateClient()
        result = await client.topup_credits(agent_id="agent1", package="pro")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["credits_added"], 100)
        mock_client_instance.post.assert_called_once_with(
            f"{client.base_url}/syndicate/credits/topup",
            json={"agent_id": "agent1", "package": "pro"}
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()


    @patch('httpx.AsyncClient')
    async def test_place_bid(self, mock_async_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "bid_placed", "auction_id": "auc123"}
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response

        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        client = SyndicateClient()
        result = await client.place_bid(auction_id="auc123", agent_id="agent1", bid_amount_cents=500)

        self.assertEqual(result["status"], "bid_placed")
        mock_client_instance.post.assert_called_once_with(
            f"{client.base_url}/syndicate/auction/auc123/bid",
            json={"agent_id": "agent1", "bid_amount": 500}
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()


    @patch('httpx.AsyncClient')
    async def test_settle_auction(self, mock_async_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "settled", "winner": "agent1", "payout": 400}
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response

        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        client = SyndicateClient()
        result = await client.settle_auction(auction_id="auc123")

        self.assertEqual(result["status"], "settled")
        mock_client_instance.post.assert_called_once_with(
            f"{client.base_url}/syndicate/auction/auc123/settle"
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()


    @patch('httpx.AsyncClient')
    async def test_get_auction_status(self, mock_async_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "open", "high_bid": 600}
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response

        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        client = SyndicateClient()
        result = await client.get_auction_status(auction_id="auc123")

        self.assertEqual(result["status"], "open")
        self.assertEqual(result["high_bid"], 600)
        mock_client_instance.get.assert_called_once_with(
            f"{client.base_url}/syndicate/auction/auc123/status"
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

if __name__ == "__main__":
    unittest.main()
