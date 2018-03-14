import logging

from aiohttp import web
from aiohttp_session import get_session
from aioauth_client import GithubClient

import config


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(fmt=logging.Formatter(fmt=logging.BASIC_FORMAT))
logger.addHandler(handler)


def login_required(fn):
    async def wrapped(request, **kwargs):
        session = await get_session(request)

        github = GithubClient(
            client_id=config.GITHUB_CLIENT_ID,
            client_secret=config.GITHUB_CLIENT_SECRET,
        )

        if 'token' not in session:
            return web.HTTPFound('/auth')

        user, info = await github.user_info()

        return await fn(request, user, **kwargs)

    return wrapped
