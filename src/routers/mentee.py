from fastapi import APIRouter, Request, Response
from src.controllers.mentee_controller import (
    MenteeController,
    MenteeResponse,
    MenteeCreate,
    MenteeUpdate,
)
from src.database import SessionDep

router = APIRouter()

@router.get("/get-card-info")
def get_card_info(request : Request, response : Response, session : SessionDep):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        mentee = MenteeController.get_card_info(
            token, session
        )
        return mentee

@router.get("/", response_model=list[MenteeResponse])
def list_mentees(session: SessionDep):
    return MenteeController.list_mentees(session)


@router.get("/{id_mentorada}", response_model=MenteeResponse)
def get_mentee(id_mentorada: int, session: SessionDep):
    return MenteeController.get_mentee(id_mentorada, session)


@router.post("/", response_model=MenteeResponse)
def create_mentee(data: MenteeCreate, session: SessionDep):
    return MenteeController.create_mentee(data, session)


@router.put("/{id_mentorada}", response_model=MenteeResponse)
def update_mentee(id_mentorada: int, data: MenteeUpdate, session: SessionDep):
    return MenteeController.update_mentee(id_mentorada, data, session)


@router.delete("/{id_mentorada}")
def delete_mentee(id_mentorada: int, session: SessionDep):
    return MenteeController.delete_mentee(id_mentorada, session)
