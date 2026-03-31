import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
from client import SyndicateClient

class TestSyndicateClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = SyndicateClient(api_key="test_key", base_url="http://test.local")

    @patch('client.httpx.AsyncClient')
    async def test_settle_auction_success(self, mock_async_client):
        # Setup mock for async context manager
        mock_instance = AsyncMock()
        mock_async_client.return_value.__aenter__.return_value = mock_instance

        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "amount_settled": 1000}
        mock_instance.post.return_value = mock_response

        # Call method
        result = await self.client.settle_auction("auc_123")

        # Assertions
        mock_instance.post.assert_called_once_with("http://test.local/syndicate/auction/auc_123/settle")
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, {"status": "success", "amount_settled": 1000})

    @patch('client.httpx.AsyncClient')
    async def test_settle_auction_error(self, mock_async_client):
        # Setup mock for async context manager
        mock_instance = AsyncMock()
        mock_async_client.return_value.__aenter__.return_value = mock_instance

        # Setup mock response to raise HTTPStatusError
        mock_response = MagicMock()
        # Mocking raise_for_status to raise an exception
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="404 Not Found",
            request=MagicMock(),
            response=MagicMock()
        )
        mock_instance.post.return_value = mock_response

        # Call method and expect exception
        with self.assertRaises(httpx.HTTPStatusError):
            await self.client.settle_auction("auc_123")

        mock_instance.post.assert_called_once_with("http://test.local/syndicate/auction/auc_123/settle")

if __name__ == "__main__":
    unittest.main()
