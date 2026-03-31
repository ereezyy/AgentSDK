import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from client import SyndicateClient
import httpx

class TestSyndicateClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = SyndicateClient(api_key="test_key", base_url="http://test.local")

    @patch("client.httpx.AsyncClient.post", new_callable=AsyncMock)
    async def test_place_bid(self, mock_post):
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "bid_id": "123"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        # Act
        result = await self.client.place_bid("auction_1", "agent_1", 1500)

        # Assert
        mock_post.assert_called_once_with(
            "http://test.local/syndicate/auction/auction_1/bid",
            json={"agent_id": "agent_1", "bid_amount": 1500}
        )
        mock_response.raise_for_status.assert_called_once()
        self.assertEqual(result, {"status": "success", "bid_id": "123"})

    @patch("client.httpx.AsyncClient.post", new_callable=AsyncMock)
    async def test_place_bid_error(self, mock_post):
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock())
        mock_post.return_value = mock_response

        # Act & Assert
        with self.assertRaises(httpx.HTTPStatusError):
            await self.client.place_bid("auction_1", "agent_1", 1500)

if __name__ == "__main__":
    unittest.main()
