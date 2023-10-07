from aiogoogle.auth import UserCreds
from aiogoogle.utils import _dict
from googleapiclient.discovery import build


class Message(_dict):
    def __init__(self, message_info: dict):
        """this is going to change"""
        self.id: str = message_info.get('id')
        self.thread_id: str = message_info.get('threadId')
        self.label_ids: list[str] = message_info.get('labelIds')
        self.snippet: str = message_info.get('snippet')
        self.history_id: str = message_info.get('historyId')
        self.internal_date: str = message_info.get('internalDate')
        self.payload: object = message_info.get('payload')
        self.size_estimate: int = message_info.get('sizeEstimate')
        self.raw: str = message_info.get('raw')


async def reply(message: Message, credentials: UserCreds) -> bool:
    service = build('gmail', 'v1', credentials=credentials)
