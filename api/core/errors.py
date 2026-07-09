from fastapi import HTTPException


class ApiError(HTTPException):
    """HTTPException with a typed {code, message} body instead of a bare string."""

    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(status_code=status_code, detail={"code": code, "message": message})
