from aiohttp import web
from pymongo.errors import DuplicateKeyError

from async_test_project.decorators import async_login_require, with_limit_and_offset
from async_test_project.util import error_response, get_parents_for_item

routes = web.RouteTableDef()


@routes.get("/")
async def get_version(request: web.Request):
    response = {"status": "success", "version": "1"}
    return web.json_response(response)


@routes.get("/element")
@async_login_require
@with_limit_and_offset
async def get_element(request: web.Request, db, limit, offset, **kwargs):
    query = request.query.get("query")
    if query is not None:
        query = db.find({"$text": {
            "$search": query}})
    else:
        query = db.find()

    items = await query.limit(limit).skip(offset).to_list(length=limit)

    for item in items:
        item["parents"] = await get_parents_for_item(item, db)

    return web.json_response({
        "status": "success",
        "items": items,
    })


@routes.post("/element")
@async_login_require
async def add_element(request: web.Request, db, **kwargs):
    element = await request.json()

    if "_id" not in element:
        return error_response("Id not specify")
    if not isinstance(element["_id"], str):
        return error_response("Id should be a string")
    if "__children__" in element:
        return error_response("Field '__children__' isn't allow")

    id = element['_id']
    parent_id = element.get("parent_id")
    if parent_id is not None:
        parent = await db.find_one({"_id": parent_id})

        if parent is None:
            return error_response(f"Target for parent with id={parent_id} didn't find.")
        else:
            try:
                parent['__children__'].append(id)
            except KeyError:
                parent['__children__'] = [id]
        await db.update_one({"_id": parent["_id"]}, {"$set": parent}, upsert=False)

    try:
        await db.insert_one(element)
    except DuplicateKeyError as e:
        return error_response("Object with such id already exists")

    element["id"] = str(element.pop("_id"))
    return web.json_response(element)


@routes.get("/subtree/{id}")
@async_login_require
@with_limit_and_offset
async def get_subtree(request: web.Request, db, limit, offset, **kwargs):
    id = request.match_info["id"]

    target = await db.find_one({"_id": id})
    if target is None:
        return error_response("Not found", 404)

    children_ids = target.get("__children__", [])

    items = []
    while children_ids and limit > 0:
        child_id = children_ids.pop()
        child = await db.find_one({"_id": child_id})

        child["id"] = str(child.pop("_id"))
        child["parents"] = await get_parents_for_item(child, db)

        children_ids.extend(child.get("__children__", []))

        if offset > 0:
            offset -= 1
            continue

        limit -= 1
        child.pop("__children__", None)
        items.append(child)

    return web.json_response({
        "status": "success",
        "items": items,
    })


@routes.delete("/element/{id}")
@async_login_require
async def delete_element(request: web.Request, db, **kwargs):
    id = request.match_info["id"]

    element = await db.find_one({"_id": id})
    if element is not None:
        await db.delete_one({"_id": id})
        return web.json_response(element)
    else:
        return error_response("Not found", 404)
