import logging
import urllib.parse

from discord import Embed
from discord.ext import commands

from notilib.email_clients import gmail
from helper import Client


logger = logging.getLogger(__name__)


class Gmail(commands.Cog):
    def __init__(self, client: Client):
        self.client = client


    @commands.Cog.listener()
    async def on_gmail_email_recieve(self, email_address: str) -> None:
        email = await gmail.retrieve_new_email(email_address)

        # false alarm (latest email has already been notified)
        if email is None:
            logger.debug('No new email to send!')
            return

        # obtain email information from email payload headers
        for header in email.payload.headers:
            if header.name.lower() == 'to':
                recipient = header.value
            if header.name.lower() == 'from':
                sender = header.value
            if header.name.lower() == 'subject':
                subject = header.value

        # build embed
        url = f'https://mail.google.com/mail/u/{email_address}/#inbox/{email.id}'

        embed = Embed(title=f'From ({sender})', url=url)
        embed.add_field(name='Recipient', value=f'||{recipient}||')  # spoiler
        embed.add_field(name='Subject', value=subject, inline=False)

        # send notification to all users that have the email address connected
        user_ids = await gmail.email_address_to_discord_ids(email_address)
        for user_id in user_ids:
            user = self.client.get_user(user_id)

            if user is None:
                logger.debug(f'Unable to fetch user with ID: {user_id}')
                continue

            logger.info(f'Sending email notification to user with ID: {user_id}')
            await user.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Gmail(client))
