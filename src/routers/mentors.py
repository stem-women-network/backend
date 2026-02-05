from typing import List, Literal
from fastapi import APIRouter, HTTPException, Request, Response, status
from sqlalchemy.engine import create
from sqlmodel import Session, select
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from src.models.login import get_current_user, get_tipo_usuario
from src.models.mentor import MentorModel
from src.schemas.tables import Mentora, Usuario, UniversidadeInstituicao
from src.database import SessionDep
from pydantic import BaseModel, create_model
from src.controllers.mentor_controller import (
    MentorController,
    MentorResponse,
    MentorCreate,
    MentorUpdate,
)
from src.database import SessionDep

router = APIRouter()


@router.get("/", response_model=list[MentorResponse])
def list_mentors(session: SessionDep):
    return MentorController.list_mentors(session)


@router.get("/get-current-mentee", responses={
    HTTP_200_OK : {"model" : create_model("NewMentee",**{
        "id" : str,
        "name" : str,
        "course" : str,
        "semester" : int,
        "status" : str,
        "progress" : int
    })},
    HTTP_401_UNAUTHORIZED : {"model" : None}
})
def get_mentee(request : Request, response : Response):
    """Get current mentee by mentor token"""
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        mentee = MentorModel.get_current_mentee_info(
            token
        )
        if mentee is None:
            response.status_code = HTTP_404_NOT_FOUND
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)
        return mentee
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

@router.get("/get-all-mentee", responses={
    HTTP_200_OK : {
        "model" : List[create_model("AllMentee", **{
            "id" : str,
            "name" : str,
            "course" : str,
            "status" : str,
            "period" : str,
            "meetings" : int
        })]
    },
    HTTP_401_UNAUTHORIZED : {
        "model" : None
    }
    
})
def get_all_mentee(request: Request, response: Response):
    """Get all mentee by mentor token"""
    print(request)
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        mentees = MentorModel.get_all_mentee_info(
            token
        )
        if mentees is None:
            response.status_code = HTTP_401_UNAUTHORIZED
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)
        return mentees
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


@router.get("/{id_mentora}", response_model=MentorResponse)
def get_mentor(id_mentora: int, session: SessionDep):
    return MentorController.get_mentor(id_mentora, session)


@router.post("/", response_model=MentorResponse)
def create_mentor(data: MentorCreate, session: SessionDep):
    return MentorController.create_mentor(data, session)


@router.put("/{id_mentora}", response_model=MentorResponse)
def update_mentor(id_mentora: int, data: MentorUpdate, session: SessionDep):
    return MentorController.update_mentor(id_mentora, data, session)


@router.delete("/{id_mentora}")
def delete_mentor(id_mentora: int, session: SessionDep):
    return MentorController.delete_mentor(id_mentora, session)


@router.get("/{id_mentora}/disponibilidade")
def get_mentor_availability(id_mentora: int, session: SessionDep):
    mentora = MentorController.get_mentor(id_mentora, session)
    return {
        "id_mentora": mentora.id_mentora,
        "disponibilidade": mentora.disponibilidade,
        "conta_ativa": mentora.conta_ativa,
    }


@router.put("/{id_mentora}/disponibilidade")
def update_mentor_availability(
    id_mentora: int, disponibilidade: int, session: SessionDep
):
    data = MentorUpdate(disponibilidade=disponibilidade)
    mentora = MentorController.update_mentor(id_mentora, data, session)
    return {
        "message": "Availability updated",
        "disponibilidade": mentora.disponibilidade,
    }
