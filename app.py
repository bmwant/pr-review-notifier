import os
from functools import partial
from aiohttp import web


async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

app = web.Application()
app.router.add_get('/', handle)
app.router.add_get('/{name}', handle)


if __name__ == '__main__':
    uprint = partial(print, flush=True)
    port = os.environ.get('PORT', 8080)
    web.run_app(app, print=uprint, port=port)