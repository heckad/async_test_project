from aiohttp import web
from pymongo.errors import DuplicateKeyError

from async_test_project.decorators import async_login_require, with_limit_and_offset
from async_test_project.util import error_response

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
    if "ancestors" in element:
        return error_response("Field 'ancestors' isn't allow")

    parent_id = element.get("parent_id")
    if parent_id is not None:
        parent = await db.find_one({"_id": parent_id})

        if parent is None:
            return error_response(f"Target for parent with id={parent_id} didn't find.")
        else:
            ancestors = parent["ancestors"]
            ancestors.append(parent_id)
            element["ancestors"] = ancestors

    try:
        await db.insert_one(element)
    except DuplicateKeyError as e:
        return error_response("Object with such id already exists")

    return web.json_response(element)


@routes.get("/subtree/{id}")
@async_login_require
@with_limit_and_offset
async def get_subtree(request: web.Request, db, limit, offset, **kwargs):
    id = request.match_info["id"]

    items = await db.find({"ancestors": id}).limit(limit).skip(offset).to_list(length=limit)

    return web.json_response({
        "status": "success",
        "items": items,
    })


@routes.delete("/element/{id}")
@async_login_require
async def delete_element(request: web.Request, db, **kwargs):
    id = request.match_info["id"]

    result = await db.delete_many({"$or": [{"_id": id}, {"list.id": id}]})

    return web.json_response({
        "deleted_count": result.deleted_count
    })
    # element = await db.find_one({"_id": id})
    # if element is not None:
    #     await db.delete_one({"_id": id})
    #     return web.json_response(element)
    # else:
    #     return error_response("Not found", 404)
