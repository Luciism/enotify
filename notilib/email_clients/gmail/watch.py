import json
import os
from textwrap import dedent
from uuid import uuid4

from aiogoogle import Aiogoogle
from aiogoogle.auth import UserCreds
from aiohttp import ClientSession

from .credentials import (
    client_creds
)


async def watch_user_inbox(user_creds: UserCreds) -> None:
    """
    Watches a user's inbox, so that the topic is notified whenever
    a new email is received.
    :param user_creds: the user's google oauth2 credentials
    """
    async with Aiogoogle(
        user_creds=user_creds,
        client_creds=client_creds
    ) as google:
        gmail = await google.discover("gmail", "v1")

        await google.as_user(
            gmail.users.watch(
                userId="me",
                topicName=os.getenv('gcloud_topic_name')
            )
        )


def build_batch_request_body(
    requests_data: list[dict],
    boundary: str
) -> str:
    """
    Builds the request body for a batch request
    :param request_data: the request data to build from
    :param boundary: the boundary name for the batches
    """
    # https://developers.google.com/gmail/api/guides/batch
    body = ''
    for req in requests_data:
        # add each batched request
        body += dedent(f"""
            --{boundary}
            Content-Type: application/http
            Content-ID: {req["headers"]["Content-ID"]}

            {req["method"]} {req["url"]}
            Content-Length: {len(req["data"])}
            Authorization: {req["headers"]["Authorization"]}


            {req["data"]}
        """)  # remove any leading whitespace from indentation

    # boundary closing
    body += f'--{boundary}--'
    return body


def build_watch_batch_data(
    user_creds: UserCreds,
    label_ids: list[str] = ['INBOX']
) -> dict:
    """
    Returns the data necessary for building a batch request body
    :param user_creds: the google oauth2 credentials of the user
    :param label_ids: the labels to watch (INBOX, SPAM, ETC)
    """
    # request content
    data = {
        "labelIds": label_ids,
        "topicName": os.getenv('gcloud_topic_name')
    }

    # entire request
    request_data = {
        'method': 'POST',
        'url': 'https://gmail.googleapis.com/gmail/v1/users/me/watch',
        'headers': {
            'Content-ID': str(uuid4()),
            'Authorization': f'Bearer {user_creds.access_token}'
            },
        'data': json.dumps(data)
        }
    return request_data


async def batch_watch_requests(user_creds_list: list[UserCreds]) -> None:
    """
    Batches inbox watch requests to the gmail api for a list of given users
    :param user_creds_list: a list of respective google oauth2 user credentials to\
        watch the user inboxs with
    """
    boundary = 'batch_watch_inbox'

    # Headers for the batch request
    headers = {
        'Content-Type': f'multipart/mixed; boundary={boundary}',
    }

    # limit it to 100 api calls per batch request
    max_calls_per_batch = 100

    for i in range(0, len(user_creds_list), max_calls_per_batch):
        # create sublist of next 100 elements
        user_creds_sublist = user_creds_list[i:i+max_calls_per_batch]

        # Build the request data dictionary from credentials
        requests_data = [
            build_watch_batch_data(user_creds)
            for user_creds in user_creds_sublist
        ]

        # build the request body string with all the requests for the batch
        body = build_batch_request_body(requests_data, boundary)

        async with ClientSession() as session:
            await session.post(
                url='https://www.googleapis.com/batch/gmail/v1',
                headers=headers,
                data=body,
                timeout=15
            )
