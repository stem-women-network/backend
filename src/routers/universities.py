from typing import Literal
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, Response
from starlette.status import HTTP_401_UNAUTHORIZED
from src.controllers.university_controller import (
    UniversityController,
    UniversityResponse,
    UniversityCreate,
    UniversityUpdate,
)
from src.database import SessionDep

router = APIRouter()


@router.get("/", response_model=list[dict[Literal['id','name','coord','matches'],str|UUID|int]])
def list_universities(request : Request,response : Response,session: SessionDep):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        universities = UniversityController.list_universities(token, session)
        return universities
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

@router.get("/count")
def get_count(request: Request, response : Response, session : SessionDep):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        count = UniversityController.get_count(token, session)
        return count
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    
@router.get("/{id_universidade_instituicao}", response_model=UniversityResponse)
def get_university(id_universidade_instituicao: int, session: SessionDep):
    return UniversityController.get_university(id_universidade_instituicao, session)


@router.post("/", response_model=UniversityResponse)
def create_university(data: UniversityCreate, session: SessionDep):
    return UniversityController.create_university(data, session)


@router.put("/{id_universidade_instituicao}", response_model=UniversityResponse)
def update_university(id_universidade_instituicao: int, data: UniversityUpdate, session: SessionDep):
    return UniversityController.update_university(id_universidade_instituicao, data, session)


@router.delete("/{id_universidade_instituicao}")
def delete_university(id_universidade_instituicao: int, session: SessionDep):
    return UniversityController.delete_university(id_universidade_instituicao, session)
