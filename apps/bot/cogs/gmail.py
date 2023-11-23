import logging

from discord.ext import commands, tasks

from notilib import InvalidRefreshTokenError
from notilib.email_clients import gmail
from helper import Client, build_gmail_received_embed


logger = logging.getLogger(__name__)


class Gmail(commands.Cog):
    def __init__(self, client: Client):
        self.client = client


    @commands.Cog.listener()
    async def on_gmail_email_receive(self, email_address: str) -> None:
        try:
            email = await gmail.retrieve_new_email(email_address)
        except InvalidRefreshTokenError:
            return  # user credentials couldn't be refreshed

        # false alarm (latest email has already been notified)
        if email is None:
            logger.debug('No new email to send!')
            return

        embed = build_gmail_received_embed(email_address, email)

        # send notification to all users that have the email address connected
        user_ids = await gmail.email_address_to_discord_ids(email_address)

        for user_id in user_ids:
            # dont notify the user if the email properties go against the
            # user's filter settings
            if await gmail.check_filters(user_id, email_address, email) is False:
                continue

            user = self.client.get_user(user_id)

            if user is None:
                logger.debug(f'Unable to fetch user with ID: {user_id}')
                continue

            logger.info(f'Sending email notification to user with ID: {user_id}')
            await user.send(embed=embed)


    # rewatch all user inboxes every 24 hours
    @tasks.loop(hours=24)
    async def rewatch_inboxes(self) -> None:
        user_creds_list = await gmail.load_all_user_credentials()
        await gmail.batch_watch_requests(user_creds_list)


    async def cog_load(self):
        self.rewatch_inboxes.start()


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Gmail(client))
