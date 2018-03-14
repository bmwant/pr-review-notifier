import logging
from aiohttp_session import setup, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(fmt=logging.Formatter(fmt=logging.BASIC_FORMAT))
logger.addHandler(handler)
