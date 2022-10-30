from fastapi import Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

http_bearer = HTTPBearer(auto_error=False)


def get_referer():
    def dependency(referer: str = Header(default=None)):
        return referer
    return Depends(dependency)


def get_host():
    def dependency(host: str = Header(default=None)):
        return host
    return Depends(dependency)


def get_origin():
    def dependency(origin: str = Header(default=None)):
        return origin
    return Depends(dependency)


def get_bearer_token():
    def dependency(token: HTTPAuthorizationCredentials = Depends(http_bearer)):
        if token:
            return token.credentials
    return Depends(dependency)


def get_db_session(engine: Engine):
    def dependency():
        session = Session(engine)
        try:
            yield session
        finally:
            session.close()
    return Depends(dependency)
