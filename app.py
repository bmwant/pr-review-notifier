import os
from functools import partial
from aiohttp import web

import aiohttp

import config


async def index(request):
    return web.Response(text='PR review notifier')


async def handle_pr_event(request):
    data = await request.json()

    action = data['action']
    if action == 'labeled':
        label = data['label']
        pr = data['pull_request']
        page_url = pr['html_url']
        user = pr['user']['login']
        if label['name'] == 'Needs review':
            print(user, page_url)

    return web.Response(text='Ok')


async def accept_pr_review(request):

    url = '/repos/{owner}/{repo}/issues/{issue}/labels/{label}'.format(
        owner=config.OWNER_NAME,
        repo=config.REPO_NAME,
        issue=4062,
        label='bug'
    )

    api_base = 'https://api.github.com'

    endpoint = '{}{}?access_token={}'.format(api_base, url, config.GITHUB_ACCESS_TOKEN)
    async with aiohttp.ClientSession() as session:
        async with session.delete(endpoint) as resp:
            print(resp.status)
            print(await resp.text())

    return web.Response(text='Ok')


app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/payload', handle_pr_event)
app.router.add_get('/accept', accept_pr_review)


if __name__ == '__main__':
    uprint = partial(print, flush=True)
    port = int(os.environ.get('PORT', 8080))
    web.run_app(app, print=uprint, port=port)
