from asgiref.sync import async_to_sync
import telegram
from dbsettings.functions import dbsettings

from ..base import BaseGateway


class TelegramGateway(BaseGateway):
    name = "telegram"
    recipient_id_key = "chat_id"

    def __init__(self, token=None):
        self._token = token

    @property
    def token(self):
        return self._token or dbsettings.TELEGRAM_TOKEN

    async def _send_async(self, recipient_id: str, text: str) -> None:
        async with telegram.Bot(token=self.token) as bot:
            await bot.send_message(chat_id=recipient_id, text=text)

    def send_message_to(self, recipient_id: str, text: str) -> None:
        async_to_sync(self._send_async)(recipient_id, text)
