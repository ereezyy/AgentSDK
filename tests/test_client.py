import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx

from client import SyndicateClient

class TestSyndicateClient(unittest.IsolatedAsyncioTestCase):

    @patch("client.httpx.AsyncClient")
    async def test_get_open_leads(self, mock_async_client_class):
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "1", "min_bid_cents": 100}]

        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.aclose = AsyncMock()

        async with SyndicateClient(api_key="test_key") as client:
            leads = await client.get_open_leads()

            self.assertEqual(leads, [{"id": "1", "min_bid_cents": 100}])
            mock_client_instance.get.assert_called_once_with(f"{client.base_url}/syndicate/auction/open")
            mock_response.raise_for_status.assert_called_once()

        mock_client_instance.aclose.assert_called_once()

    @patch("client.httpx.AsyncClient")
    async def test_topup_credits(self, mock_async_client_class):
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.json.return_value = {"new_balance_cents": 1000}

        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.aclose = AsyncMock()

        async with SyndicateClient(api_key="test_key") as client:
            res = await client.topup_credits("agent1", "pro")
            self.assertEqual(res, {"new_balance_cents": 1000})
            mock_client_instance.post.assert_called_once_with(
                f"{client.base_url}/syndicate/credits/topup",
                json={"agent_id": "agent1", "package": "pro"}
            )

        mock_client_instance.aclose.assert_called_once()

    @patch("client.httpx.AsyncClient")
    async def test_place_bid(self, mock_async_client_class):
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.json.return_value = {"bid_id": "b1"}

        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client_instance.aclose = AsyncMock()

        async with SyndicateClient(api_key="test_key") as client:
            res = await client.place_bid("a1", "agent1", 150)
            self.assertEqual(res, {"bid_id": "b1"})
            mock_client_instance.post.assert_called_once_with(
                f"{client.base_url}/syndicate/auction/a1/bid",
                json={"agent_id": "agent1", "bid_amount": 150}
            )

        mock_client_instance.aclose.assert_called_once()

    async def test_secure_default_base_url(self):
        """Verify that the default base_url uses HTTPS."""
        with patch("client.httpx.AsyncClient"):
            client = SyndicateClient(api_key="test_key")
            self.assertTrue(client.base_url.startswith("https://"))
            self.assertEqual(client.base_url, "https://localhost:8422/api/v2")

    @patch('client.httpx.AsyncClient.get')
    async def test_get_open_leads_error_handling(self, mock_get):
        # Setup mock response with error status
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Server Error",
            request=MagicMock(),
            response=mock_response
        )
        mock_get.return_value = mock_response

        async with SyndicateClient(api_key="test_key") as client:
            with self.assertRaises(httpx.HTTPStatusError):
                await client.get_open_leads()

if __name__ == '__main__':
    unittest.main()
