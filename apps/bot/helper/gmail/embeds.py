from discord import Embed

from notilib.email_clients.gmail import Email

def build_gmail_received_embed(email_address: str, email: Email) -> Embed:
    """
    Builds an email received embed from the provided email data
    :param email_address: the email address of the recipient
    :param email: the email data to build the embed with
    """
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

    return embed
