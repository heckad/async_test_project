import os

import pymongo
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient

from async_test_project.endpoints import routes


def create_app():
    app = web.Application(debug=True)
    app.add_routes(routes)

    async def init_db_clients(app):
        app['db_clients'] = {
            "root": AsyncIOMotorClient(
                os.getenv("MONGO_HOST", "192.168.99.108"),
                os.getenv("MONGO_PORT", 27017),
                username="root",
                password="1234")
        }

        app['db_clients']["root"].test.collections.create_index([("text", pymongo.TEXT)])
        app['db_clients']["root"].test.collections.create_index([("ancestors", 1)])

    app.on_startup.append(init_db_clients)

    async def close_db_clients(app):
        for db_client in app['db_clients'].values():
            db_client.close()

    app.on_cleanup.append(close_db_clients)
    return app
