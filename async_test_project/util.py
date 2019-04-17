import os
import json

from aiohttp import web

from async_test_project.exceptions import ValueErrorWithVarName


def error_response(message: str, error_code: int = 400) -> web.Response:
    response = {"status": "error", "message": message}
    return web.Response(text=json.dumps(response), status=error_code, content_type="application/json")


def get_request_args(args, arg_name: str, cast_to: type = str, default=None):
    res = args.get(arg_name)
    if res is not None:
        try:
            return cast_to(res)
        except ValueError as e:
            raise ValueErrorWithVarName(str(e), arg_name)
    else:
        return default


def get_limit_and_offset(request):
    try:
        limit = get_request_args(request.query, "limit", int, 32)
        if limit < 1:
            return error_response("Min limit is 1")
        if limit > 100:
            return error_response("Max limit is 100")
        offset = get_request_args(request.query, "offset", int, 0)
        if offset < 0:
            return error_response("Min offset is 0")
    except ValueErrorWithVarName as e:
        return error_response("{} must be a int".format(e.var_name))
    return limit, offset


async def get_parents_for_item(item, db):
    parent_ids = []
    parent_id = item.pop('parent_id', None)
    while parent_id is not None:
        el = await db.find_one({"_id": parent_id})
        parent_ids.append(el["_id"])
        parent_id = el.get("parent_id")
    return parent_ids
