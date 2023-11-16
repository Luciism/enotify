def default_avatar_url(discord_info: dict) -> str:
    """
    Returns the default avatar url from a discord raw response data
    :param discord_info: the discord response data to form the avatar url from
    """
    discord_id = int(discord_info.get('id', 0))
    discriminator = int(discord_info.get('discriminator', 0))

    if discriminator == 0:
        avatar_index = (discord_id >> 22) % 5
    else:
        avatar_index = discriminator % 5

    avatar_url = f"https://cdn.discordapp.com/embed/avatars/{avatar_index}.png"
    return avatar_url


def get_discord_avatar(discord_info: dict):
    """
    Returns the avatar url from a discord raw response data
    :param discord_info: the discord response data to form the avatar url from
    """
    avatar = discord_info.get('avatar')

    if avatar is None:
        return default_avatar_url(discord_info)

    discord_id = discord_info.get('id')
    return f'https://cdn.discordapp.com/avatars/{discord_id}/{avatar}'
