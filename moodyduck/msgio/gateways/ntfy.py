import requests

from ..base import BaseGateway


class NtfyGateway(BaseGateway):
    name = "ntfy"
    recipient_id_key = "topic_url"

    def send_message_to(self, recipient_id: str, text: str) -> None:
        """recipient_id is the full ntfy topic URL."""
        requests.post(
            recipient_id,
            data=text.encode("utf-8"),
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Title": "MoodyDuck",
            },
            timeout=10,
        )
