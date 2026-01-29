from fastapi import APIRouter
from src.controllers.university_controller import (
    UniversityController,
    UniversityResponse,
    UniversityCreate,
    UniversityUpdate,
)
from src.database import SessionDep

router = APIRouter()


@router.get("/", response_model=list[UniversityResponse])
def list_universities(session: SessionDep):
    return UniversityController.list_universities(session)


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
