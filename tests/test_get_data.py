import pytest


async def test_get_elements(client, prepare_data):
    resp = await client.get("/element")
    assert resp.status == 200, await resp.text()


async def test_get_elements_with_limit(client, prepare_data):
    resp = await client.get("/element", params=dict(limit=4, offset=4))
    assert resp.status == 200, await resp.text()


@pytest.mark.parametrize("limit", [
    -5, 101, "fas"
])
async def test_get_elements_with_invalid_limit(client, prepare_data, limit):
    resp = await client.get("/element", params=dict(limit=limit, offset=4))
    assert resp.status == 400, await resp.text()


async def test_get_elements_with_invalid_offset(client, prepare_data):
    resp = await client.get("/element", params=dict(offset=-5))
    assert resp.status == 400, await resp.text()


async def test_get_elements_with_query(client, prepare_data):
    resp = await client.get("/element", params=dict(query="hello4"))
    assert resp.status == 200, await resp.text()


async def test_remove_not_existing_element(client, prepare_data):
    resp = await client.delete("/element/{}".format(max(prepare_data)) + "1")
    assert resp.status == 404, await resp.text()


async def test_get_elements_in_node(client, prepare_data):
    resp = await client.get("/subtree/{}".format(1))
    assert resp.status == 200, await resp.text()

    items = (await resp.json())["items"]
    assert {"_id": "2", "text": "hello2", "parent_id": "1", "ancestors": ["1"]} in items
    assert {"_id": "3", "text": "hello3", "parent_id": "2", "ancestors": ["1", "2"]} in items
    assert {"_id": "4", "text": "hello4", "parent_id": "3", "ancestors": ["1", "2", "3"]} in items
    assert {"_id": "5", "text": "hello5", "parent_id": "4", "ancestors": ["1", "2", "3", "4"]} in items
    assert {"_id": "6", "text": "hello6", "parent_id": "3", "ancestors": ["1", "2", "3"]}in items
    assert {"_id": "7", "text": "hello7", "parent_id": "3", "ancestors": ["1", "2", "3"]}in items


async def test_get_elements_in_not_existing_node(client, prepare_data):
    resp = await client.get("/subtree/{}".format(100))
    assert resp.status == 200, await resp.text()
    assert len((await resp.json())["items"]) == 0


async def test_get_elements_in_node_with_offset(client, prepare_data):
    resp = await client.get("/subtree/{}".format(1), params=dict(offset=3))
    assert resp.status == 200, await resp.text()
