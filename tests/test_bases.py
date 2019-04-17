async def test_get_version(client):
    resp = await client.get("/")
    assert resp.status == 200


async def test_insert_and_delete_data(client):
    el = {"_id": "1", "text": "hello"}
    resp = await client.post("/element", json=el)
    assert resp.status == 200, await resp.text()
    resp = await client.delete("/element/{}".format("1"))
    assert resp.status == 200, await resp.text()
