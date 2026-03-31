import unittest
import urllib.parse
from unittest.mock import patch, MagicMock
from client import SyndicateClient
import httpx
import asyncio

class TestSyndicateClient(unittest.IsolatedAsyncioTestCase):
    async def test_place_bid_url_encoding(self):
        client = SyndicateClient(api_key="test_key", base_url="http://test")
        auction_id = "test/id with space"
        encoded_id = urllib.parse.quote(auction_id, safe='')

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            await client.place_bid(auction_id, "agent_1", 100)

            mock_post.assert_called_once()
            called_url = mock_post.call_args[0][0]
            self.assertIn(f"/syndicate/auction/{encoded_id}/bid", called_url)
            self.assertNotIn(f"/syndicate/auction/{auction_id}/bid", called_url)


    async def test_settle_auction_url_encoding(self):
        client = SyndicateClient(api_key="test_key", base_url="http://test")
        auction_id = "test/id with space"
        encoded_id = urllib.parse.quote(auction_id, safe='')

        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            await client.settle_auction(auction_id)

            mock_post.assert_called_once()
            called_url = mock_post.call_args[0][0]
            self.assertIn(f"/syndicate/auction/{encoded_id}/settle", called_url)
            self.assertNotIn(f"/syndicate/auction/{auction_id}/settle", called_url)

    async def test_get_auction_status_url_encoding(self):
        client = SyndicateClient(api_key="test_key", base_url="http://test")
        auction_id = "test/id with space"
        encoded_id = urllib.parse.quote(auction_id, safe='')

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            await client.get_auction_status(auction_id)

            mock_get.assert_called_once()
            called_url = mock_get.call_args[0][0]
            self.assertIn(f"/syndicate/auction/{encoded_id}/status", called_url)
            self.assertNotIn(f"/syndicate/auction/{auction_id}/status", called_url)

if __name__ == '__main__':
    unittest.main()
