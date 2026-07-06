import unittest
import os
import urllib.parse
import httpx
from unittest.mock import patch, MagicMock, AsyncMock

from client import SyndicateClient

class TestSyndicateClient(unittest.IsolatedAsyncioTestCase):
    async def test_init_default(self):
        async with SyndicateClient() as client:
            self.assertEqual(client.api_key, "syndicate_agent_v0.1_key")
            self.assertTrue(client.base_url.startswith("https://"))
            self.assertEqual(client.base_url, "https://localhost:8422/api/v2")
            self.assertEqual(client.headers["X-Agent-API-Key"], "syndicate_agent_v0.1_key")
            self.assertEqual(client.headers["Content-Type"], "application/json")

    async def test_init_custom(self):
        async with SyndicateClient(api_key="custom_key", base_url="https://api.example.com/") as client:
            self.assertEqual(client.api_key, "custom_key")
            self.assertEqual(client.base_url, "https://api.example.com")
            self.assertEqual(client.headers["X-Agent-API-Key"], "custom_key")

    @patch.dict(os.environ, {"SYNDICATE_API_KEY": "env_key"})
    async def test_init_env_var(self):
        async with SyndicateClient() as client:
            self.assertEqual(client.api_key, "env_key")
            self.assertEqual(client.headers["X-Agent-API-Key"], "env_key")

    @patch('httpx.AsyncClient')
    async def test_get_open_leads(self, mock_async_client):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "auction1", "description": "Lead 1", "min_bid_cents": 100}]
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)

        mock_async_client.return_value = mock_client_instance
        mock_client_instance.__aenter__.return_value = mock_client_instance

        client = SyndicateClient()
        leads = await client.get_open_leads()

        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["id"], "auction1")
        mock_client_instance.get.assert_called_once_with(client._open_leads_url)
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

    @patch('httpx.AsyncClient')
    async def test_topup_credits(self, mock_async_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "credits_added": 100}
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)

        mock_async_client.return_value = mock_client_instance
        mock_client_instance.__aenter__.return_value = mock_client_instance

        client = SyndicateClient()
        result = await client.topup_credits(agent_id="agent1", package="pro")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["credits_added"], 100)
        mock_client_instance.post.assert_called_once_with(
            client._topup_credits_url,
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
        mock_client_instance.post = AsyncMock(return_value=mock_response)

        mock_async_client.return_value = mock_client_instance
        mock_client_instance.__aenter__.return_value = mock_client_instance

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
        mock_client_instance.post = AsyncMock(return_value=mock_response)

        mock_async_client.return_value = mock_client_instance
        mock_client_instance.__aenter__.return_value = mock_client_instance

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
        mock_client_instance.get = AsyncMock(return_value=mock_response)

        mock_async_client.return_value = mock_client_instance
        mock_client_instance.__aenter__.return_value = mock_client_instance

        client = SyndicateClient()
        result = await client.get_auction_status(auction_id="auc123")

        self.assertEqual(result["status"], "open")
        self.assertEqual(result["high_bid"], 600)
        mock_client_instance.get.assert_called_once_with(
            f"{client.base_url}/syndicate/auction/auc123/status"
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

    async def test_place_bid_url_encoding(self):
        auction_id = "test/id with space"
        encoded_id = urllib.parse.quote(auction_id, safe='')

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            async with SyndicateClient(api_key="test_key", base_url="https://test") as client:
                await client.place_bid(auction_id, "agent_1", 100)

            mock_post.assert_called_once()
            called_url = mock_post.call_args[0][0]
            self.assertIn(f"/syndicate/auction/{encoded_id}/bid", called_url)
            self.assertNotIn(f"/syndicate/auction/{auction_id}/bid", called_url)

    async def test_settle_auction_url_encoding(self):
        auction_id = "test/id with space"
        encoded_id = urllib.parse.quote(auction_id, safe='')

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            async with SyndicateClient(api_key="test_key", base_url="https://test") as client:
                await client.settle_auction(auction_id)

            mock_post.assert_called_once()
            called_url = mock_post.call_args[0][0]
            self.assertIn(f"/syndicate/auction/{encoded_id}/settle", called_url)
            self.assertNotIn(f"/syndicate/auction/{auction_id}/settle", called_url)

    async def test_get_auction_status_url_encoding(self):
        auction_id = "test/id with space"
        encoded_id = urllib.parse.quote(auction_id, safe='')

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            async with SyndicateClient(api_key="test_key", base_url="https://test") as client:
                await client.get_auction_status(auction_id)

            mock_get.assert_called_once()
            called_url = mock_get.call_args[0][0]
            self.assertIn(f"/syndicate/auction/{encoded_id}/status", called_url)
            self.assertNotIn(f"/syndicate/auction/{auction_id}/status", called_url)

    @patch('httpx.AsyncClient')
    async def test_get_open_leads_error_handling(self, mock_async_client):
        # Setup mock response with error status
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Server Error",
            request=MagicMock(),
            response=mock_response
        )

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)

        mock_async_client.return_value = mock_client_instance
        mock_client_instance.__aenter__.return_value = mock_client_instance

        async with SyndicateClient(api_key="test_key") as client:
            with self.assertRaises(httpx.HTTPStatusError):
                await client.get_open_leads()

if __name__ == '__main__':
    unittest.main()
