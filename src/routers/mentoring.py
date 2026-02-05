from uuid import UUID
from fastapi import APIRouter, Body, Form, HTTPException, Header, Request, Response, UploadFile, File
from fastapi.datastructures import Headers
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND

from src.models.login import get_current_user
from src.models.mentoring import MentoringModel
import base64

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

@router.post("/send-file")
async def send_file(file: bytes = File(),title:str=Form(),file_type:str=Form(), mentee_id: str = Form(), authorization : str = Header()):
    token = authorization.split(" ")[1]
    MentoringModel.send_file(file, title, file_type, token, mentee_id)
    return {}

@router.get("/get-files/")
async def get_file(mentee_id: str,request : Request, response : Response):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        files = MentoringModel.get_files(token, mentee_id)
        if files is None:
            response.status_code = HTTP_401_UNAUTHORIZED
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)
        result = []
        for file in files:
            result.append({
                "id" : file[0],
                "title" : file[1],
                "type" : file[2],
                "size" : file[3]
            })
        return result
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

@router.get("/download-file")
async def download_file(file_id: str ,request: Request, response : Response):
     authorization = request.headers.get("authorization")
     if authorization is not None:
         token = authorization.split(" ")[1]
         file = MentoringModel.download_file(token, file_id)
         if file is None or file == '':
             response.status_code = HTTP_401_UNAUTHORIZED
             raise HTTPException(status_code=HTTP_404_NOT_FOUND)
         return base64.b64encode(file)
     else:
         response.status_code = HTTP_401_UNAUTHORIZED
         raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

@router.delete("/delete-file/{file_id}")
async def delete_file(request: Request, response: Response, file_id: str):
    authorization = request.headers.get("authorization")
    if authorization is not None and file_id is not None and file_id != "":
        token = authorization.split(" ")[1]
        MentoringModel.delete_file(token, file_id)
        return {}
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
