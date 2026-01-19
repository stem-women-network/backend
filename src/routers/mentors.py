from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import Mentora, Usuario, UniversidadeInstituicao
from src.database import SessionDep
from pydantic import BaseModel

router = APIRouter()

class MentorResponse(BaseModel):
    id_mentora: int
    linkedin: str | None
    formacao: str
    cargo_atual: str
    area_atuacao: int
    disponibilidade: int
    conta_ativa: bool

class MentorCreate(BaseModel):
    linkedin: str | None = None
    formacao: str
    cargo_atual: str
    area_atuacao: int
    disponibilidade: int
    id_usuario: int
    id_universidade_instituicao: int

class MentorUpdate(BaseModel):
    linkedin: str | None = None
    formacao: str | None = None
    cargo_atual: str | None = None
    area_atuacao: int | None = None
    disponibilidade: int | None = None
    conta_ativa: bool | None = None

@router.get("/", response_model=list[MentorResponse])
def list_mentors(session: SessionDep):
    """List all mentors"""
    mentoras = session.exec(select(Mentora)).all()
    return mentoras

@router.get("/{id_mentora}", response_model=MentorResponse)
def get_mentor(id_mentora: int, session: SessionDep):
    """Get a specific mentor by ID"""
    mentora = session.get(Mentora, id_mentora)
    if not mentora:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    return mentora

@router.post("/", response_model=MentorResponse)
def create_mentor(data: MentorCreate, session: SessionDep):
    """Create a new mentor"""
    usuario = session.get(Usuario, data.id_usuario)
    universidade = session.get(UniversidadeInstituicao, data.id_universidade_instituicao)
    
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not universidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="University not found")
    
    mentora = Mentora(**data.dict())
    session.add(mentora)
    session.commit()
    session.refresh(mentora)
    return mentora

@router.put("/{id_mentora}", response_model=MentorResponse)
def update_mentor(id_mentora: int, data: MentorUpdate, session: SessionDep):
    """Update a mentor"""
    mentora = session.get(Mentora, id_mentora)
    if not mentora:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(mentora, key, value)
    
    session.add(mentora)
    session.commit()
    session.refresh(mentora)
    return mentora

@router.delete("/{id_mentora}")
def delete_mentor(id_mentora: int, session: SessionDep):
    """Delete a mentor"""
    mentora = session.get(Mentora, id_mentora)
    if not mentora:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    
    session.delete(mentora)
    session.commit()
    return {"message": "Mentor deleted successfully"}

@router.get("/{id_mentora}/disponibilidade")
def get_mentor_availability(id_mentora: int, session: SessionDep):
    """Get mentor availability"""
    mentora = session.get(Mentora, id_mentora)
    if not mentora:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    
    return {
        "id_mentora": mentora.id_mentora,
        "disponibilidade": mentora.disponibilidade,
        "conta_ativa": mentora.conta_ativa
    }

@router.put("/{id_mentora}/disponibilidade")
def update_mentor_availability(id_mentora: int, disponibilidade: int, session: SessionDep):
    """Update mentor availability"""
    mentora = session.get(Mentora, id_mentora)
    if not mentora:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    
    mentora.disponibilidade = disponibilidade
    session.add(mentora)
    session.commit()
    session.refresh(mentora)
    return {"message": "Availability updated", "disponibilidade": mentora.disponibilidade}
