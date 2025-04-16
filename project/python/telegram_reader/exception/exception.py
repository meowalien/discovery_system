import http

class KnownException(Exception):
    status_code = http.HTTPStatus.INTERNAL_SERVER_ERROR
    def __init__(self, message):
        if message is None:
            message = "Internal Server Error"
        super().__init__(message)
        self.message = message

class EventHandlerAlreadyExistError(KnownException):
    status_code = http.HTTPStatus.BAD_REQUEST
    def __init__(self):
        super().__init__("Event handler already exists.")