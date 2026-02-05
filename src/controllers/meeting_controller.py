from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import ProximoEncontro, Encontro
from pydantic import BaseModel
from datetime import datetime


class MeetingResponse(BaseModel):
    id_encontro: int
    data_encontro: datetime
    local: str
    id_mentoria: int


class MeetingCreate(BaseModel):
    data_encontro: datetime
    local: str
    id_mentoria: int


class MeetingUpdate(BaseModel):
    data_encontro: datetime | None = None
    local: str | None = None


class UpcomingMeetingResponse(BaseModel):
    id_proximo_encontro: int
    data_proximo_encontro: datetime
    local: str
    id_mentora: int
    id_mentorada: int


class UpcomingMeetingCreate(BaseModel):
    data_proximo_encontro: datetime
    local: str
    id_mentora: int
    id_mentorada: int


class UpcomingMeetingUpdate(BaseModel):
    data_proximo_encontro: datetime | None = None
    local: str | None = None


class MeetingController:
    """Controller for meeting management"""

    # Encontro (Past meetings)
    @staticmethod
    def list_meetings(session: Session) -> list[Encontro]:
        """List all past meetings"""
        encontros = session.exec(select(Encontro)).all()
        return encontros

    @staticmethod
    def get_meeting(id_encontro: int, session: Session) -> Encontro:
        """Get a specific past meeting by ID"""
        encontro = session.get(Encontro, id_encontro)
        if not encontro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Encontro não encontrado"
            )
        return encontro

    @staticmethod
    def create_meeting(data: MeetingCreate, session: Session) -> Encontro:
        encontro = Encontro(**data.dict())
        session.add(encontro)
        session.commit()
        session.refresh(encontro)
        return encontro

    @staticmethod
    def update_meeting(id_encontro: int, data: MeetingUpdate, session: Session) -> Encontro:
        encontro = session.get(Encontro, id_encontro)
        if not encontro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Encontro não encontrado"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(encontro, key, value)

        session.add(encontro)
        session.commit()
        session.refresh(encontro)
        return encontro

    @staticmethod
    def delete_meeting(id_encontro: int, session: Session) -> dict:
        encontro = session.get(Encontro, id_encontro)
        if not encontro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Encontro não encontrado"
            )

        session.delete(encontro)
        session.commit()
        return {"message": "Encontro deletado com sucesso"}

    # ProximoEncontro (Upcoming meetings)
    @staticmethod
    def list_upcoming_meetings(session: Session) -> list[ProximoEncontro]:
        """List all upcoming meetings"""
        proximos = session.exec(select(ProximoEncontro)).all()
        return proximos

    @staticmethod
    def get_upcoming_meeting(
        id_proximo_encontro: int, session: Session
    ) -> ProximoEncontro:
        """Get a specific upcoming meeting by ID"""
        proximo = session.get(ProximoEncontro, id_proximo_encontro)
        if not proximo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Próximo encontro não encontrado",
            )
        return proximo

    @staticmethod
    def create_upcoming_meeting(
        data: UpcomingMeetingCreate, session: Session
    ) -> ProximoEncontro:
        proximo = ProximoEncontro(**data.dict())
        session.add(proximo)
        session.commit()
        session.refresh(proximo)
        return proximo

    @staticmethod
    def update_upcoming_meeting(
        id_proximo_encontro: int, data: UpcomingMeetingUpdate, session: Session
    ) -> ProximoEncontro:
        proximo = session.get(ProximoEncontro, id_proximo_encontro)
        if not proximo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Próximo encontro não encontrado",
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(proximo, key, value)

        session.add(proximo)
        session.commit()
        session.refresh(proximo)
        return proximo

    @staticmethod
    def delete_upcoming_meeting(id_proximo_encontro: int, session: Session) -> dict:
        proximo = session.get(ProximoEncontro, id_proximo_encontro)
        if not proximo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Próximo encontro não encontrado",
            )

        session.delete(proximo)
        session.commit()
        return {"message": "Próximo encontro deletado com sucesso"}
