import re
import functools

from aiohttp import web

from async_test_project.util import error_response, get_limit_and_offset

from cryptography.fernet import Fernet

key = b'fEaV-F4930xPfBKAGrWF0Rm9uSbyjhRbsV1kbrUATCs='
cipher = Fernet(key)


def async_login_require(f):
    @functools.wraps(f)
    async def decorated(request: web.Request, *args, **kwargs):
        try:
            token = request.headers["Authorization"]
        except KeyError:
            return error_response("Authorization header didn't set.")

        try:
            user_id_and_role = re.match(r"^Basic (\S+)$", token).group(1)
        except:
            return error_response("Authorization header wrong format.")

        try:
            user_id_and_role = cipher.decrypt(user_id_and_role.encode()).decode()
        except:
            return error_response("Can`t decode token. Check that it is encoded in base64.")

        if ":" in user_id_and_role:
            user_id, role = user_id_and_role.split(":")
        else:
            return error_response("Token invalid")

        try:
            result = request.app['db_clients'][role]
        except KeyError:
            return error_response("Token invalid")

        return await f(*args, request=request,
                       db=result.test.collections,  # Захардклжен путь до бд
                       **kwargs)

    return decorated


def with_limit_and_offset(f):
    @functools.wraps(f)
    async def decorated(request, *args, **kwargs):
        limit_and_offset = get_limit_and_offset(request)
        if isinstance(limit_and_offset, web.Response):
            return limit_and_offset
        else:
            limit, offset = limit_and_offset
        return await f(*args, request=request, limit=limit, offset=offset, **kwargs)

    return decorated
