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
    assert {'text': 'hello2', 'id': '2', 'parents': ['1']} in items
    assert {'text': 'hello3', 'id': '3', 'parents': ['2', '1']} in items
    assert {'text': 'hello4', 'id': '4', 'parents': ['3', '2', '1']} in items
    assert {'text': 'hello5', 'id': '5', 'parents': ['4', '3', '2', '1']} in items
    assert {'text': 'hello6', 'id': '6', 'parents': ['3', '2', '1']} in items
    assert {'text': 'hello7', 'id': '7', 'parents': ['3', '2', '1']} in items


async def test_get_elements_in_not_existing_node(client, prepare_data):
    resp = await client.get("/subtree/{}".format(100))
    assert resp.status == 404, await resp.text()


async def test_get_elements_in_node_with_offset(client, prepare_data):
    resp = await client.get("/subtree/{}".format(1), params=dict(offset=3))
    assert resp.status == 200, await resp.text()
