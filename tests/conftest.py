import os
import pytest
import pymongo
from aiohttp.test_utils import TestClient

from cryptography.fernet import Fernet


@pytest.fixture(scope="session")
def example_data():
    return [
        {"_id": "1", "text": "hello", "ancestors": []},
        {"_id": "2", "text": "hello2", "parent_id": "1", "ancestors": ["1"]},
        {"_id": "3", "text": "hello3", "parent_id": "2", "ancestors": ["1", "2"]},
        {"_id": "4", "text": "hello4", "parent_id": "3", "ancestors": ["1", "2", "3"]},
        {"_id": "5", "text": "hello5", "parent_id": "4", "ancestors": ["1", "2", "3", "4"]},
        {"_id": "6", "text": "hello6", "parent_id": "3", "ancestors": ["1", "2", "3"]},
        {"_id": "7", "text": "hello7", "parent_id": "3", "ancestors": ["1", "2", "3"]},
    ]


@pytest.fixture
def app():
    from async_test_project.app import create_app
    return create_app()


@pytest.fixture
async def client(app, aiohttp_client) -> TestClient:
    key = b'fEaV-F4930xPfBKAGrWF0Rm9uSbyjhRbsV1kbrUATCs='
    return await aiohttp_client(app, headers={
        "Authorization": "Basic {}".format(
            Fernet(key).encrypt("1:root".encode()).decode()),
        "Test": "True"
    })


@pytest.fixture
async def base_client(app, aiohttp_client) -> TestClient:
    client = aiohttp_client(app)
    return await client


@pytest.fixture(scope="module")
def prepare_data(example_data):
    try:
        client = pymongo.MongoClient(
            os.environ["MONGO_HOST"],
            os.environ.get("MONGO_PORT", 27017),
            username=os.environ["MONGO_USERNAME"],
            password=os.environ["MONGO_PASSWORD"])
    except KeyError as e:
        raise Exception("{} not add in environment".format(e))

    collection = client.test.collections

    element_ids = []
    for el in example_data:
        result = collection.insert_one(el)
        element_ids.append(result.inserted_id)

    yield element_ids

    for id in element_ids:
        collection.delete_one({"_id": id})
