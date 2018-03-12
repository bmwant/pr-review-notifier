import os
from functools import partial

import aiohttp
from aiohttp import web

import config
from utils import logger
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


async def accept_pr_review(request):
    review_id = request.match_info['review_id']
    review = await get_review(review_id)
    if review is None:
        return aiohttp.web.HTTPNotFound(text='No review with such id')

    pr_name = review.pr_name
    reviews_count = await update_reviews_count(review_id)
    if reviews_count <= config.REQUIRED_REVIEWERS:
        notifier = Notifier()
        message = f':point_right: review of _{pr_name}_ has been started'
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
            if resp.status == 404:
                logger.info('Label has been already removed')
            elif resp.status == 200:
                logger.debug('Label was successfully removed')
            else:
                message = (await resp.json())['message']
                logger.error('Unexpected response: %s', message)


async def test(request):
    import database
    await database.insert_new_review(1, "Test name", "http://googl.com")


app = web.Application()
app.router.add_get('/', index)
app.router.add_get('/t', test)
app.router.add_post('/payload', handle_pr_event)
app.router.add_get('/accept/{review_id}', accept_pr_review)


if __name__ == '__main__':
    uprint = partial(print, flush=True)
    port = int(os.environ.get('PORT', 8080))
    web.run_app(app, print=uprint, port=port)
