"""
backend/webhook_receiver/router.py

The HTTP entry point for GitHub events. For now it just confirms
that the route is reachable. We will fill in real logic over the
next 12 steps.
"""

from fastapi import APIRouter, status

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"],
)


@router.post("/github", status_code=status.HTTP_200_OK)
async def receive_github_webhook():
    """Empty handler. Will grow over the next 12 steps."""
    return {"received": True}