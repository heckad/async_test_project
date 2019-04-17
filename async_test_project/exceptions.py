class AsyncTestProjectException(Exception):
    """Generic error class."""


class ValueErrorWithVarName(AsyncTestProjectException, ValueError):
    def __init__(self, message, var_name):
        ValueError.__init__(self, message)
        self.var_name = var_name
