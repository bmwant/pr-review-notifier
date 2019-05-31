import os
import asyncio
import base64
from functools import partial
from http import HTTPStatus

import aiohttp
import aiohttp_session
from aiohttp import web
from aioauth_client import GithubClient
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

import config
from utils import logger
from database import (
    insert_new_review,
    update_reviews_count,
    get_review_by_id,
    get_review_by_issue_number,
)
from notifier import Notifier


async def index(request):
    return web.Response(text='PR review notifier')


async def _handle_labeled(data):
    label = data['label']
    pr = data['pull_request']
    issue_number = pr['number']
    title = pr['title']
    page_url = pr['html_url']
    user = pr['user']['login']
    if label['name'] == config.DEFAULT_LABEL_NAME:
        review_id = await insert_new_review(
            issue_number=issue_number,
            pr_name=title,
            pr_url=page_url,
        )
        notifier = Notifier()
        message = (f'@here PR _{title}_ by *{user}* '
                   f'is waiting for review <{page_url}>')
        logger.debug(f'Sending notification about {page_url}')
        await notifier.send_message(message,
                                    channel=config.DEFAULT_SLACK_CHANNEL)


async def _handle_reviewed(data):
    state = data['review']['state']
    issue_number = data['pull_request']['number']
    if state == 'approved':
        review = await get_review_by_issue_number(issue_number)
        if review is None:
            logger.error('Got approve but PR is not in the database, '
                         'probably label was missing')
            return

        reviews_count = await update_reviews_count(review.id)
        pr_name = review.pr_name
        if reviews_count == config.REQUIRED_APPROVES:
            logger.info(f'We have {reviews_count} approves '
                        f'for pr {pr_name}, removing label')
            await delete_label(review.issue_number)
            notifier = Notifier()
            message = f':green_check_mark: PR _{pr_name}_ has ' \
                      f'{reviews_count} approves and can be merged!'
            await notifier.send_message(
                message, channel=config.DEFAULT_SLACK_CHANNEL)


async def handle_pr_event(request):
    data = await request.json()

    action = data.get('action')
    if action == 'labeled':
        await _handle_labeled(data)
    elif action == 'submitted':
        await _handle_reviewed(data)
    else:
        logger.debug(f'Unknown action {action}')

    return web.Response(text='Ok')


async def delete_label(issue_number):
    url = 'repos/{owner}/{repo}/issues/{issue}/labels/{label}'.format(
        owner=config.OWNER_NAME,
        repo=config.REPO_NAME,
        issue=issue_number,
        label=config.DEFAULT_LABEL_NAME,
    )
    endpoint = '{}{}?access_token={}'.format(
        config.GITHUB_API_BASE, url, config.GITHUB_ACCESS_TOKEN)

    async with aiohttp.ClientSession() as session:
        async with session.delete(endpoint) as resp:
            if resp.status == HTTPStatus.NOT_FOUND:
                logger.info('Label has been already removed')
            elif resp.status == HTTPStatus.OK:
                logger.debug('Label was successfully removed')
            else:
                message = (await resp.json())['message']
                logger.error('Unexpected response: %s', message)


async def healthcheck():
    endpoint = config.HEALTHCHECK_ENDPOINT
    if not endpoint:
        logger.info('Healthcheck service is disabled')
        return

    while True:
        logger.debug('Sending healthcheck...')
        async with aiohttp.ClientSession() as session:
            async with session.get(config.HEALTHCHECK_ENDPOINT) as resp:
                if resp.status != HTTPStatus.OK:
                    text = await resp.text()
                    logger.error('Request failed %s', text)
        await asyncio.sleep(config.HEALTHCHECK_INTERVAL)


async def start_healthcheck(app):
    app.loop.create_task(healthcheck())


async def github_auth(request):
    github = GithubClient(
        client_id=config.GITHUB_CLIENT_ID,
        client_secret=config.GITHUB_CLIENT_SECRET,
    )
    session = await aiohttp_session.get_session(request)

    if 'code' not in request.query:
        redirect_uri = request.query.get('redirect_uri', '/')
        session['redirect_uri'] = redirect_uri
        return web.HTTPFound(github.get_authorize_url(scope='user:email'))

    code = request.query['code']
    token, _ = await github.get_access_token(code)

    session['token'] = token
    next_uri = session.pop('redirect_uri', '/')
    logger.debug('Redirecting back to %s', next_uri)
    return web.HTTPFound(next_uri)


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/auth', github_auth)
    app.router.add_post('/payload', handle_pr_event)


def main():
    uprint = partial(print, flush=True)
    port = int(os.environ.get('PORT', 8080))
    app = web.Application()
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    aiohttp_session.setup(app, EncryptedCookieStorage(secret_key))
    setup_routes(app)
    app.on_startup.append(start_healthcheck)
    web.run_app(app, print=uprint, port=port)


if __name__ == '__main__':
    main()
