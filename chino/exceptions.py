from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
__author__ = 'Stefano Tranquillini <stefano@chino.io>'


class ApiError(Exception):
    code = 500

    def __init__(self, message):
        super(ApiError, self).__init__(message)


class ClientError(Exception):
    def __init__(self, message):
        super(ClientError, self).__init__(message)


class CallError(ApiError):
    def __init__(self, code, message):
        super(CallError, self).__init__(message)
        self.code = code
        if isinstance(message, list):
            self.message = ', '.join(message)
        else:
            self.message = message
            
class CallFail(CallError):
    def __init__(self, code, message):
        super(CallFail, self).__init__(code, message)

class MethodNotSupported(ClientError):
    def __init__(self):
        super(MethodNotSupported, self).__init__("Method not supported")
