from fastapi import Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

http_bearer = HTTPBearer(auto_error=False)


def get_referer():
    def dependency(referer: str = Header(default=None)):
        return referer
    return Depends(dependency)


def get_bearer_token():
    def dependency(token: HTTPAuthorizationCredentials = Depends(http_bearer)):
        return token.credentials
    return Depends(dependency)
