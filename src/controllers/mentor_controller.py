from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import Mentora, Usuario, UniversidadeInstituicao
from pydantic import BaseModel


class MentorResponse(BaseModel):
    id_mentora: int
    linkedin: str | None
    formacao: str
    cargo_atual: str
    area_atuacao: list[str]
    disponibilidade: int
    conta_ativa: bool


class MentorCreate(BaseModel):
    linkedin: str | None = None
    formacao: str
    cargo_atual: str
    areas_atuacao: list[str]
    disponibilidade: int
    id_usuario: int
    id_universidade_instituicao: int


class MentorUpdate(BaseModel):
    linkedin: str | None = None
    formacao: str | None = None
    cargo_atual: str | None = None
    areas_atuacao: list[str] | None = None
    disponibilidade: int | None = None
    conta_ativa: bool | None = None


class MentorController:
    """Controller for mentor management"""

    @staticmethod
    def list_mentors(session: Session) -> list[Mentora]:
        """List all mentors"""
        mentoras = session.exec(select(Mentora)).all()
        return mentoras

    @staticmethod
    def get_mentor(id_mentora: int, session: Session) -> Mentora:
        """Get a specific mentor by ID"""
        mentora = session.get(Mentora, id_mentora)
        if not mentora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentora não encontrada"
            )
        return mentora

    @staticmethod
    def create_mentor(data: MentorCreate, session: Session) -> Mentora:
        usuario = session.get(Usuario, data.id_usuario)
        universidade = session.get(
            UniversidadeInstituicao, data.id_universidade_instituicao
        )

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )
        if not universidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Universidade não encontrada"
            )

        mentora = Mentora(**data.dict())
        session.add(mentora)
        session.commit()
        session.refresh(mentora)
        return mentora

    @staticmethod
    def update_mentor(id_mentora: int, data: MentorUpdate, session: Session) -> Mentora:
        mentora = session.get(Mentora, id_mentora)
        if not mentora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentora não encontrada"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(mentora, key, value)

        session.add(mentora)
        session.commit()
        session.refresh(mentora)
        return mentora

    @staticmethod
    def delete_mentor(id_mentora: int, session: Session) -> dict:
        mentora = session.get(Mentora, id_mentora)
        if not mentora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentora não encontrada"
            )

        session.delete(mentora)
        session.commit()
        return {"message": "Mentora deletada com sucesso"}
