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
from utils import logger, login_required
from database import insert_new_review, get_review, update_reviews_count
from notifier import Notifier


async def index(request):
    return web.Response(text='PR review notifier')


async def handle_pr_event(request):
    data = await request.json()

    action = data.get('action')
    if action == 'labeled':
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
            accept_url = '{base_url}accept/{review_id}'.format(
                base_url=config.BASE_URL, review_id=review_id
            )
            notifier = Notifier()
            message = (f'@here PR _{title}_ by *{user}* '
                       f'is waiting for review <{accept_url}|{page_url}>')
            logger.debug(f'Sending notification about {page_url}')
            await notifier.send_message(message,
                                        channel=config.DEFAULT_SLACK_CHANNEL)

    return web.Response(text='Ok')


@login_required
async def accept_pr_review(request, user):
    review_id = request.match_info['review_id']
    review = await get_review(review_id)

    full_name = '{} {}'.format(user.first_name, user.last_name).strip()
    username = full_name or user.username
    if review is None:
        return aiohttp.web.HTTPNotFound(text='No review with such id')

    pr_name = review.pr_name
    reviews_count = await update_reviews_count(review_id)
    if reviews_count <= config.REQUIRED_REVIEWERS:
        notifier = Notifier()
        message = f':point_right: *{username}* started ' \
                  f'reviewing PR _{pr_name}_'
        await notifier.send_message(message,
                                    channel=config.DEFAULT_SLACK_CHANNEL)

    if reviews_count == config.REQUIRED_REVIEWERS:
        logger.info(f'We have {reviews_count} review '
                    f'on pr {pr_name}, removing label')
        await delete_label(review.issue_number)

    return aiohttp.web.HTTPFound(review.pr_url)


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
    if 'code' not in request.query:
        return web.HTTPFound(github.get_authorize_url(scope='user:email'))

    code = request.query['code']
    token, _ = await github.get_access_token(code)

    session = await aiohttp_session.get_session(request)
    session['token'] = token
    return web.HTTPFound('/')


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/auth', github_auth)
    app.router.add_post('/payload', handle_pr_event)
    app.router.add_get('/accept/{review_id}', accept_pr_review)


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
