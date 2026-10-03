from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=False)


def require_admin(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    # stub: any bearer token passes, real jwt decode + role check comes later
    if creds is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
