import os
from functools import partial

import aiohttp
from aiohttp import web
from slackclient import SlackClient

import config
from utils import logger
from database import insert_new_review, get_review


class Notifier(object):
    BOT_NAME = 'gitbot'
    BOT_ICON = config.DEFAULT_SLACK_ICON

    def __init__(self):
        self.client = SlackClient(config.SLACKBOT_TOKEN)

    def send_message(self, message, *, channel):
        self.client.api_call(
            'chat.postMessage',
            channel=channel,
            text=message,
            parse='full',
            username=self.BOT_NAME,
            icon_emoji=self.BOT_ICON,
        )


async def index(request):
    return web.Response(text='PR review notifier')


async def handle_pr_event(request):
    data = await request.json()

    action = data.get('action')
    if action == 'labeled':
        label = data['label']
        pr = data['pull_request']
        pr_id = pr['id']
        title = pr['title']
        page_url = pr['html_url']
        user = pr['user']['login']
        if label['name'] == config.DEFAULT_LABEL_NAME:
            review = await insert_new_review(
                pr_id=pr_id,
                pr_name=title,
                pr_url=page_url,
            )
            accept_url = '{base_url}accept/{review_id}'.format(
                base_url=config.BASE_URL, review_id=review.id
            )
            notifier = Notifier()
            message = (f'@here PR _{title}_ by *{user}* '
                       f'is waiting for review {accept_url}')
            logger.debug(f'Sending notification about {page_url}')
            notifier.send_message(message,
                                  channel=config.DEFAULT_SLACK_CHANNEL)

    return web.Response(text='Ok')


async def accept_pr_review(request):
    review_id = request.match_info['review_id']
    # logic to track pr reviews
    review = await get_review(review_id)
    if review is None:
        return aiohttp.web.HTTPNotFound(text='No review with such id')

    return aiohttp.web.HTTPFound(review.pr_url)


async def delete_label():
    url = 'repos/{owner}/{repo}/issues/{issue}/labels/{label}'.format(
        owner=config.OWNER_NAME,
        repo=config.REPO_NAME,
        issue=4062,
        label='bug'
    )
    endpoint = '{}{}?access_token={}'.format(
        config.GITHUB_API_BASE, url, config.GITHUB_ACCESS_TOKEN)

    async with aiohttp.ClientSession() as session:
        async with session.delete(endpoint) as resp:
            print(resp.status)
            print(await resp.text())

    return web.Response(text='Ok')


app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/payload', handle_pr_event)
app.router.add_get('/accept/{review_id}', accept_pr_review)


if __name__ == '__main__':
    uprint = partial(print, flush=True)
    port = int(os.environ.get('PORT', 8080))
    web.run_app(app, print=uprint, port=port)
