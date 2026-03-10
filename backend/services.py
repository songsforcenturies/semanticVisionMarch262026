"""Shared services: email, websocket manager, utility functions."""
import os
import logging
import asyncio
import random
import string
from typing import Dict, List
from fastapi import WebSocket
import resend

logger = logging.getLogger(__name__)

# Email configuration
resend.api_key = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")


async def send_email(to_email: str, subject: str, html: str):
    """Send email via Resend (non-blocking)"""
    params = {"from": SENDER_EMAIL, "to": [to_email], "subject": subject, "html": html}
    try:
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {result}")
        return result
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        raise


def generate_6digit_code():
    return ''.join(random.choices(string.digits, k=6))


class ConnectionManager:
    """Manages WebSocket connections per session"""
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id] = [c for c in self.active_connections[session_id] if c != websocket]
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            dead = []
            for conn in self.active_connections[session_id]:
                try:
                    await conn.send_json(message)
                except Exception:
                    dead.append(conn)
            for d in dead:
                self.disconnect(d, session_id)


ws_manager = ConnectionManager()
