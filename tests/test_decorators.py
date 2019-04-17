import json
from unittest import mock

from aiohttp.test_utils import make_mocked_request
from cryptography.fernet import Fernet

from async_test_project.decorators import async_login_require


async def same_function(request, **kwargs):
    return "Same function"


async def eval_decorator(headers=None):
    request = make_mocked_request("GET", "/element", headers=headers,
                                  app={"db_clients":
                                           {"root": mock.Mock()}
                                       })
    decorated_func = async_login_require(same_function)
    return await decorated_func(request)


async def test_decorator__async_login_require(base_client):
    resp = await eval_decorator()
    assert "Authorization header didn't set." == json.loads(resp.text)["message"]

    resp = await eval_decorator({"Authorization": "fsdfdw"})
    assert "Authorization header wrong format." == json.loads(resp.text)["message"]

    resp = await eval_decorator({"Authorization": "Basic bvrsdzf"})
    assert "Can`t decode token. Check that it is encoded in base64." == json.loads(resp.text)["message"]

    resp = await eval_decorator({"Authorization": "Basic {}".format(
        Fernet(b'fEaV-F4930xPfBKAGrWF0Rm9uSbyjhRbsV1kbrUATCs=').encrypt("1root".encode()).decode()
    )})
    assert "Token invalid" == json.loads(resp.text)["message"]

    resp = await eval_decorator({"Authorization": "Basic {}".format(
        Fernet(b'fEaV-F4930xPfBKAGrWF0Rm9uSbyjhRbsV1kbrUATCs=').encrypt("1:roottt".encode()).decode()
    )})
    assert "Token invalid" == json.loads(resp.text)["message"]

    resp = await eval_decorator({"Authorization": "Basic {}".format(
        Fernet(b'fEaV-F4930xPfBKAGrWF0Rm9uSbyjhRbsV1kbrUATCs=').encrypt("1:root".encode()).decode()
    )})
    assert "Same function" == resp
