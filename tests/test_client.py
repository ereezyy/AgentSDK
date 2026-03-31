import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx

from client import SyndicateClient

class TestSyndicateClient(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.client = SyndicateClient(api_key="test_key", base_url="http://test")

    @patch("client.httpx.AsyncClient")
    async def test_get_open_leads_success(self, mock_async_client_class):
        # Setup mock
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "1", "description": "lead 1"}]
        mock_response.raise_for_status.return_value = None

        mock_client_instance.get.return_value = mock_response

        # Call method
        result = await self.client.get_open_leads()

        # Verify
        self.assertEqual(result, [{"id": "1", "description": "lead 1"}])
        mock_client_instance.get.assert_called_once_with("http://test/syndicate/auction/open")
        mock_response.raise_for_status.assert_called_once()

    @patch("client.httpx.AsyncClient")
    async def test_get_open_leads_http_error(self, mock_async_client_class):
        # Setup mock
        mock_client_instance = AsyncMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client_instance

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=MagicMock()
        )

        mock_client_instance.get.return_value = mock_response

        # Call and verify error
        with self.assertRaises(httpx.HTTPStatusError):
            await self.client.get_open_leads()

        mock_client_instance.get.assert_called_once_with("http://test/syndicate/auction/open")

if __name__ == "__main__":
    unittest.main()
