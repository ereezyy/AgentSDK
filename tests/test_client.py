import unittest
from unittest.mock import patch, AsyncMock, MagicMock
from client import SyndicateClient

class TestSyndicateClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = SyndicateClient(api_key="test_key", base_url="http://test_url")

    @patch("client.httpx.AsyncClient")
    async def test_get_auction_status(self, mock_async_client_class):
        # Setup mock for httpx.AsyncClient context manager
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

        # Setup mock for the get response
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "open", "high_bid": 500}
        mock_response.raise_for_status = MagicMock()
        # Ensure get is awaitable and returns mock_response
        mock_client_instance.get.return_value = mock_response

        # Call the method
        result = await self.client.get_auction_status("auction_123")

        # Verify
        mock_client_instance.get.assert_called_once_with("http://test_url/syndicate/auction/auction_123/status")
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, {"status": "open", "high_bid": 500})

if __name__ == '__main__':
    unittest.main()
