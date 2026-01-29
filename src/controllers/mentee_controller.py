from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import Mentorada
from pydantic import BaseModel


class MenteeResponse(BaseModel):
    id_mentorada: int
    linkedin: str | None
    curso_area_stem: str
    ano_curso: int
    semestre: int
    objetivo_mentoria: str
    disponibilidade: int | None
    conta_ativa: bool


class MenteeCreate(BaseModel):
    linkedin: str | None = None
    curso_area_stem: str
    ano_curso: int
    semestre: int
    objetivo_mentoria: str
    disponibilidade: int | None = None
    id_usuario: int
    id_universidade_instituicao: int


class MenteeUpdate(BaseModel):
    linkedin: str | None = None
    curso_area_stem: str | None = None
    ano_curso: int | None = None
    semestre: int | None = None
    objetivo_mentoria: str | None = None
    disponibilidade: int | None = None
    conta_ativa: bool | None = None


class MenteeController:
    """Controller for mentee (mentorada) management"""

    @staticmethod
    def list_mentees(session: Session) -> list[Mentorada]:
        """List all mentees"""
        mentoradas = session.exec(select(Mentorada)).all()
        return mentoradas

    @staticmethod
    def get_mentee(id_mentorada: int, session: Session) -> Mentorada:
        """Get a specific mentee by ID"""
        mentorada = session.get(Mentorada, id_mentorada)
        if not mentorada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada não encontrada"
            )
        return mentorada

    @staticmethod
    def create_mentee(data: MenteeCreate, session: Session) -> Mentorada:
        mentorada = Mentorada(**data.dict())
        session.add(mentorada)
        session.commit()
        session.refresh(mentorada)
        return mentorada

    @staticmethod
    def update_mentee(id_mentorada: int, data: MenteeUpdate, session: Session) -> Mentorada:
        mentorada = session.get(Mentorada, id_mentorada)
        if not mentorada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada não encontrada"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(mentorada, key, value)

        session.add(mentorada)
        session.commit()
        session.refresh(mentorada)
        return mentorada

    @staticmethod
    def delete_mentee(id_mentorada: int, session: Session) -> dict:
        mentorada = session.get(Mentorada, id_mentorada)
        if not mentorada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada não encontrada"
            )

        session.delete(mentorada)
        session.commit()
        return {"message": "Mentorada deletada com sucesso"}
