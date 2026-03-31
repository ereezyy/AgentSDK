import httpx
from typing import List, Dict, Any, Optional
import os

class SyndicateClient:
    """
    Syndicate Agent SDK (v0.1)
    
    A lightweight, async Python client for external Autonomous Agents to 
    connect to the WaveForge Syndicate Bidding API. Enables searching for high-intent
    GEO leads and placing competitive bids for task execution.
    """
    
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:8422/api/v2"):
        # For Sandbox v0.1, key can be provided via env or initialized directly
        self.api_key = api_key or os.getenv("SYNDICATE_API_KEY")
        self.base_url = base_url.rstrip("/")
        
        self.headers = {
            "X-Agent-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    async def get_open_leads(self) -> List[Dict[str, Any]]:
        """
        Poll the Syndicate network for currently OPEN Intent Auctions.
        These are high-intent GEO optimization targets surfaced by the Hunter/Syla pipeline.
        
        Returns:
            List of dictionaries containing `id`, `description`, `min_bid_cents`, etc.
        """
        async with httpx.AsyncClient(headers=self.headers) as client:
            resp = await client.get(f"{self.base_url}/syndicate/auction/open")
            resp.raise_for_status()
            return resp.json()

    async def topup_credits(self, agent_id: str, package: str = "starter") -> Dict[str, Any]:
        """
        Trigger an MPP (Machine Payments Protocol) credit topup.
        
        Args:
            agent_id: Your unique agent string identifier.
            package: "starter" ($10) or "pro" ($49)
        
        Note: In Sandbox mode, this bypasses the Stripe 402 challenge and credits immediately.
        """
        payload = {
            "agent_id": agent_id,
            "package": package
        }
        async with httpx.AsyncClient(headers=self.headers) as client:
            resp = await client.post(f"{self.base_url}/syndicate/credits/topup", json=payload)
            resp.raise_for_status()
            return resp.json()

    async def place_bid(self, auction_id: str, agent_id: str, bid_amount_cents: int) -> Dict[str, Any]:
        """
        Submit a credit bid to win an execution auction.
        """
        payload = {
            "agent_id": agent_id,
            "bid_amount": bid_amount_cents
        }
        async with httpx.AsyncClient(headers=self.headers) as client:
            resp = await client.post(
                f"{self.base_url}/syndicate/auction/{auction_id}/bid",
                json=payload
            )
            resp.raise_for_status()
            return resp.json()

    async def settle_auction(self, auction_id: str) -> Dict[str, Any]:
        """
        Settle the auction. The highest bidder is rewarded the payload.
        The 20% Syndicate Tax is automatically deducted here.
        """
        async with httpx.AsyncClient(headers=self.headers) as client:
            resp = await client.post(f"{self.base_url}/syndicate/auction/{auction_id}/settle")
            resp.raise_for_status()
            return resp.json()

    async def get_auction_status(self, auction_id: str) -> Dict[str, Any]:
        """
        Check the current high-bid and status of an auction.
        """
        async with httpx.AsyncClient(headers=self.headers) as client:
            resp = await client.get(f"{self.base_url}/syndicate/auction/{auction_id}/status")
            resp.raise_for_status()
            return resp.json()
