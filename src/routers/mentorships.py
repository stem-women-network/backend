from fastapi import APIRouter
from src.controllers.mentorship_controller import (
    MentorshipController,
    MentorshipResponse,
    MentorshipCreate,
    MentorshipUpdate,
)
from src.database import SessionDep

router = APIRouter()


@router.get("/", response_model=list[MentorshipResponse])
def list_mentorships(session: SessionDep):
    return MentorshipController.list_mentorships(session)


@router.get("/{id_mentoria}", response_model=MentorshipResponse)
def get_mentorship(id_mentoria: int, session: SessionDep):
    return MentorshipController.get_mentorship(id_mentoria, session)


@router.post("/", response_model=MentorshipResponse)
def create_mentorship(data: MentorshipCreate, session: SessionDep):
    return MentorshipController.create_mentorship(data, session)


@router.put("/{id_mentoria}", response_model=MentorshipResponse)
def update_mentorship(id_mentoria: int, data: MentorshipUpdate, session: SessionDep):
    return MentorshipController.update_mentorship(id_mentoria, data, session)


@router.delete("/{id_mentoria}")
def delete_mentorship(id_mentoria: int, session: SessionDep):
    return MentorshipController.delete_mentorship(id_mentoria, session)


@router.get("/mentor/{id_mentora}")
def get_mentor_mentorships(id_mentora: int, session: SessionDep):
    return MentorshipController.get_mentor_mentorships(id_mentora, session)


@router.get("/mentee/{id_mentorada}")
def get_mentee_mentorships(id_mentorada: int, session: SessionDep):
    return MentorshipController.get_mentee_mentorships(id_mentorada, session)