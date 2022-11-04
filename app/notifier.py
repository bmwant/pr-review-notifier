import aiohttp

from app import config


class Notifier(object):
    def __init__(self):
        pass

    async def send_message(self, message, *, channel: str):
        if not channel.startswith('#'):
            raise ValueError('Channel name should start with #')

        data = {
            'token': config.SLACKBOT_TOKEN,
            'text': message,
            'unfurl_links': False,
            'link_names': True,
            'channel': channel,
            'parse': 'none',
            'username': config.DEFAULT_SLACK_BOT_NAME,
            'icon_emoji': config.DEFAULT_SLACK_ICON,
        }

        url = 'https://slack.com/api/chat.postMessage'
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                result = await response.json()
