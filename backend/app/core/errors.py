from fastapi import HTTPException, status

class EntityNotFound(HTTPException):
    def __init__(self, entity: str = "Entity"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} not found")

class PermissionDenied(HTTPException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class AuthError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
