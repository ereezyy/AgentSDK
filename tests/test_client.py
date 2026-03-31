import unittest
from unittest.mock import patch, MagicMock
import httpx

from client import SyndicateClient

class TestSyndicateClient(unittest.IsolatedAsyncioTestCase):

    @patch('httpx.AsyncClient.get')
    async def test_get_open_leads_error_handling(self, mock_get):
        # Setup mock response with error status
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Server Error",
            request=MagicMock(),
            response=mock_response
        )
        mock_get.return_value = mock_response

        client = SyndicateClient()

        with self.assertRaises(httpx.HTTPStatusError):
            await client.get_open_leads()
