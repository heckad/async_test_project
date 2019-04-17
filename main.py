from aiohttp import web

from async_test_project.app import create_app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app)
