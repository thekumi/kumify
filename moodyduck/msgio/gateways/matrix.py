from asgiref.sync import async_to_sync
from nio import AsyncClient
from dbsettings.functions import dbsettings

from ..base import BaseGateway


class MatrixGateway(BaseGateway):
    name = "matrix"
    recipient_id_key = "room_id"

    def __init__(self, username=None, password=None, homeserver=None):
        self._username = username
        self._password = password
        self._homeserver = homeserver

    @property
    def username(self):
        return self._username or dbsettings.MATRIX_USERNAME

    @property
    def password(self):
        return self._password or dbsettings.MATRIX_PASSWORD

    @property
    def homeserver(self):
        return self._homeserver or dbsettings.MATRIX_HOMESERVER

    async def _send_async(self, room_id: str, text: str) -> None:
        client = AsyncClient(self.homeserver, self.username)
        await client.login(self.password)
        await client.join(room_id)
        await client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": text},
        )
        await client.close()

    def send_message_to(self, recipient_id: str, text: str) -> None:
        async_to_sync(self._send_async)(recipient_id, text)
