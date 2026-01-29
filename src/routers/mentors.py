from fastapi import APIRouter
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
