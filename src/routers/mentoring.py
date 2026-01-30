from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from src.models.login import get_current_user
from src.models.mentoring import MentoringModel


router = APIRouter()

class OtherId(BaseModel):
    other_id : str

@router.post("/get-messages")
def get_messages(data : OtherId, request: Request, response: Response):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        messages = MentoringModel.get_messages(token, data.other_id)
        if messages is None:
            response.status_code = HTTP_401_UNAUTHORIZED
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)
        return messages
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
