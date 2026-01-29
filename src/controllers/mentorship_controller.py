from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import Mentoria
from pydantic import BaseModel


class MentorshipResponse(BaseModel):
    id_mentoria: int
    estado_mentoria: str
    id_mentora: int
    id_mentorada: int


class MentorshipCreate(BaseModel):
    estado_mentoria: str = "ativa"
    id_mentora: int
    id_mentorada: int


class MentorshipUpdate(BaseModel):
    estado_mentoria: str | None = None


class MentorshipController:
    """Controller for mentorship management"""

    @staticmethod
    def list_mentorships(session: Session) -> list[Mentoria]:
        """List all mentorships"""
        mentorias = session.exec(select(Mentoria)).all()
        return mentorias

    @staticmethod
    def get_mentorship(id_mentoria: int, session: Session) -> Mentoria:
        """Get a specific mentorship by ID"""
        mentoria = session.get(Mentoria, id_mentoria)
        if not mentoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentoria não encontrada"
            )
        return mentoria

    @staticmethod
    def create_mentorship(data: MentorshipCreate, session: Session) -> Mentoria:
        mentoria = Mentoria(**data.dict())
        session.add(mentoria)
        session.commit()
        session.refresh(mentoria)
        return mentoria

    @staticmethod
    def update_mentorship(
        id_mentoria: int, data: MentorshipUpdate, session: Session
    ) -> Mentoria:
        mentoria = session.get(Mentoria, id_mentoria)
        if not mentoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentoria não encontrada"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(mentoria, key, value)

        session.add(mentoria)
        session.commit()
        session.refresh(mentoria)
        return mentoria

    @staticmethod
    def delete_mentorship(id_mentoria: int, session: Session) -> dict:
        mentoria = session.get(Mentoria, id_mentoria)
        if not mentoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentoria não encontrada"
            )

        session.delete(mentoria)
        session.commit()
        return {"message": "Mentoria deletada com sucesso"}

    @staticmethod
    def get_mentor_mentorships(id_mentora: int, session: Session) -> list[Mentoria]:
        """Get all mentorships for a specific mentor"""
        statement = select(Mentoria).where(Mentoria.id_mentora == id_mentora)
        mentorias = session.exec(statement).all()
        return mentorias

    @staticmethod
    def get_mentee_mentorships(id_mentorada: int, session: Session) -> list[Mentoria]:
        """Get all mentorships for a specific mentee"""
        statement = select(Mentoria).where(Mentoria.id_mentorada == id_mentorada)
        mentorias = session.exec(statement).all()
        return mentorias
