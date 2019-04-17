async def test_insert_data_with_occupied_id(client, prepare_data):
    el = {"_id": "1", "text": "hello"}
    resp = await client.post("/element", json=el)
    assert resp.status == 400
    assert "Object with such id already exists" == (await resp.json())["message"]


async def test_insert_data_without_id(client, prepare_data):
    el = {"text": "hello"}
    resp = await client.post("/element", json=el)
    assert resp.status == 400
    assert "Id not specify" == (await resp.json())["message"]


async def test_insert_data_with_parent_id_on_existing_element(client, prepare_data):
    el = {"_id": "10", "text": "hello", "parent_id": "2"}
    resp = await client.post("/element", json=el)
    assert resp.status == 200, resp.text()
    resp = await client.delete("element/10")
    assert resp.status == 200, resp.text()


async def test_insert_data_with_parent_id_on_existing_list_element(client, prepare_data):
    el = {"_id": "10", "text": "hello", "parent_id": "5"}
    resp = await client.post("/element", json=el)
    assert resp.status == 200
    resp = await client.delete("element/10")
    assert resp.status == 200


async def test_insert_data_with_parent_id_on_not_existing_element(client, prepare_data):
    el = {"_id": "10", "text": "hello", "parent_id": "200"}
    resp = await client.post("/element", json=el)
    assert resp.status == 400
    assert "Target for parent with id=200 didn't find." == (await resp.json())["message"]


async def test_insert_data_with_int_id(client, prepare_data):
    el = {"_id": 1, "text": "hello"}
    resp = await client.post("/element", json=el)
    assert resp.status == 400
    assert "Id should be a string" == (await resp.json())["message"]


async def test_insert_data_with___children___field(client, prepare_data):
    el = {"_id": "10", "text": "hello", "parent_id": "2", "__children__": ["32", "3"]}
    resp = await client.post("/element", json=el)
    assert resp.status == 400
    assert "Field '__children__' isn't allow" == (await resp.json())["message"]
