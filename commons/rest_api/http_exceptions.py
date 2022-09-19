from commons.datetime import now
from fastapi import HTTPException


def generate_detail_obj(status, error, message):
    return {
        'status': status,
        'timestamp': now().isoformat(),
        'error': error,
        'error_message': message
    }


class NotFoundException(HTTPException):
    def __init__(self, message=''):
        super().__init__(status_code=404, detail=generate_detail_obj(404, 'Not Found', message))


class BadRequestException(HTTPException):
    def __init__(self, message=''):
        super().__init__(status_code=400, detail=generate_detail_obj(400, 'Bad Request', message))


class ConflictException(HTTPException):
    def __init__(self, message=''):
        super().__init__(status_code=409, detail=generate_detail_obj(409, 'Conflict', message))


class InternalServerErrorException(HTTPException):
    def __init__(self, message=''):
        super().__init__(status_code=500, detail=generate_detail_obj(500, 'Internal Server Error', message))


class UnauthorizedException(HTTPException):
    def __init__(self, message=''):
        super().__init__(status_code=401, detail=generate_detail_obj(401, 'Unauthorized', message))


class ForbiddenException(HTTPException):
    def __init__(self, message=''):
        super().__init__(status_code=403, detail=generate_detail_obj(403, 'Forbidden', message))


class NotImplementedException(HTTPException):
    def __init__(self, message=''):
        super().__init__(status_code=501, detail=generate_detail_obj(501, 'Not Implemented', message))


class BadGatewayException(HTTPException):
    def __init__(self, message=''):
        super().__init__(status_code=502, detail=generate_detail_obj(502, 'Bad Gateway', message))
