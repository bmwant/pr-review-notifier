import os
from functools import partial
from aiohttp import web


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


app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/payload', handle_pr_event)


if __name__ == '__main__':
    uprint = partial(print, flush=True)
    port = int(os.environ.get('PORT', 8080))
    web.run_app(app, print=uprint, port=port)
