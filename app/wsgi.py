from aiohttp_wsgi import WSGIHandler, serve
from app.main import create_app

application = create_app()
wsgi_handler = WSGIHandler(application)


if __name__ == "__main__":
    serve(application)
