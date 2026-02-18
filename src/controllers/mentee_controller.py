from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import label
from sqlmodel import Session, col, desc, literal, select
from starlette.status import HTTP_404_NOT_FOUND
from src.models.login import get_current_user
from src.schemas.tables import Mentorada, Mentoria, Usuario
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

    @staticmethod
    def get_card_info(token : str, session: Session) -> dict:
        user = get_current_user(token, session)
        try:
            if user is None:
                raise Exception()
            
            statement = select(Mentoria.estado_mentoria)\
                .join(Mentorada, Mentoria.id_mentorada == Mentoria.id_mentorada)\
                .where(Mentorada.id_usuario == user.id_usuario)\
                .where(Mentoria.ano_mentoria == datetime.now().year)\
                .order_by(desc(Mentoria.comeco_mentoria))\
                .limit(1)
            
            mentoring_status = session.exec(statement).one_or_none()
            if mentoring_status is None:
                mentoring_status = "pendente"
            print(mentoring_status)
            statement = select(
                col(Usuario.nome_completo).label("name"),
                col(Mentorada.curso).label("course"),
                col(Mentorada.semestre).label("semester"),
                col(Mentorada.disponibilidade).label("availability"),
                literal(mentoring_status).label("status")
            )\
            .where(Mentorada.id_usuario == user.id_usuario)\
            .join(Usuario)
            mentee = session.exec(statement)\
                .mappings().one_or_none()
            if mentee is None:
                raise Exception()
            return mentee
        except Exception as e:
            print(e)
            raise HTTPException(
                HTTP_404_NOT_FOUND,
                "Mentorada não encontrada"
            )
        
