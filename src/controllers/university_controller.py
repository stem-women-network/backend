from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import UniversidadeInstituicao
from pydantic import BaseModel


class UniversityResponse(BaseModel):
    id_universidade_instituicao: int
    nome_instituicao: str


class UniversityCreate(BaseModel):
    nome_instituicao: str


class UniversityUpdate(BaseModel):
    nome_instituicao: str | None = None


class UniversityController:
    """Controller for university/institution management"""

    @staticmethod
    def list_universities(session: Session) -> list[UniversidadeInstituicao]:
        """List all universities/institutions"""
        universidades = session.exec(select(UniversidadeInstituicao)).all()
        return universidades

    @staticmethod
    def get_university(
        id_universidade_instituicao: int, session: Session
    ) -> UniversidadeInstituicao:
        """Get a specific university/institution by ID"""
        universidade = session.get(UniversidadeInstituicao, id_universidade_instituicao)
        if not universidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Universidade/Instituição não encontrada",
            )
        return universidade

    @staticmethod
    def create_university(
        data: UniversityCreate, session: Session
    ) -> UniversidadeInstituicao:
        """Create a new university/institution"""
        universidade = UniversidadeInstituicao(**data.dict())
        session.add(universidade)
        session.commit()
        session.refresh(universidade)
        return universidade

    @staticmethod
    def update_university(
        id_universidade_instituicao: int, data: UniversityUpdate, session: Session
    ) -> UniversidadeInstituicao:
        """Update a university/institution"""
        universidade = session.get(UniversidadeInstituicao, id_universidade_instituicao)
        if not universidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Universidade/Instituição não encontrada",
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(universidade, key, value)

        session.add(universidade)
        session.commit()
        session.refresh(universidade)
        return universidade

    @staticmethod
    def delete_university(
        id_universidade_instituicao: int, session: Session
    ) -> dict:
        """Delete a university/institution"""
        universidade = session.get(UniversidadeInstituicao, id_universidade_instituicao)
        if not universidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Universidade/Instituição não encontrada",
            )

        session.delete(universidade)
        session.commit()
        return {"message": "Universidade/Instituição deletada com sucesso"}
