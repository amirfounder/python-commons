from fastapi import Header, Depends
from fastapi.security import HTTPBearer

http_bearer = HTTPBearer(auto_error=False)


def get_referer():
    def dependency(referer: str = Header(default=None)):
        return referer
    return Depends(dependency)


def get_bearer_token():
    def dependency(token: str = Depends(http_bearer)):
        return token
    return Depends(dependency)
