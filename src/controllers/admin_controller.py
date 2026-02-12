from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Session, col, select
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from src.models.login import get_current_user
from src.schemas.tables import Administrador, Mentora, Mentorada, Usuario


class UpdateApproval(BaseModel):
    mentor_id : str
    approved : bool

class UpdateApprovalMentee(BaseModel):
    mentee_id : str
    approved : bool

class AdminController:
    @staticmethod
    def get_approvals(token : str, session : Session) -> list[dict[str,any]]:
        user = get_current_user(token, session)
        try:
            if user is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            statement = select(Administrador).where(Administrador.id_usuario == user.id_usuario)
            admin = session.exec(statement).one_or_none()
            if admin is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            mentors = session.exec(
                select(
                    col(Mentora.id_mentora).label("id"),
                    col(Usuario.nome_completo).label("nome"),
                    col(Mentora.cargo_atual).label("cargo"),
                    col(Mentora.formacao).label("formacao"),
                    col(Mentora.linkedin).label("linkedin"),
                    col(Mentora.competencias).label("skills"),
                    col(Mentora.foto_perfil).label("foto"),
                )\
                .where(Mentora.conta_ativa == False)\
                .join(Usuario)
            ).mappings().all()
            return mentors
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    @staticmethod
    def update_approval(data : UpdateApproval,token : str, session : Session):
        user = get_current_user(token, session)
        try:
            if user is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            statement = select(Administrador).where(Administrador.id_usuario == user.id_usuario)
            admin = session.exec(statement).one_or_none()
            if admin is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            mentor = session.exec(
                select(Mentora)\
                .where(Mentora.id_mentora == data.mentor_id)
            ).one_or_none()
            if mentor is None:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST)
            mentor.conta_ativa = data.approved
            session.commit()
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
        
    @staticmethod
    def get_approvals_mentee(token : str, session : Session) -> list[dict[str,any]]:
        user = get_current_user(token, session)
        try:
            if user is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            statement = select(Administrador).where(Administrador.id_usuario == user.id_usuario)
            admin = session.exec(statement).one_or_none()
            if admin is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            mentees = session.exec(
                select(
                    col(Mentorada.id_mentorada).label("id"),
                    col(Usuario.nome_completo).label("nome"),
                    col(Mentorada.curso).label("curso"),
                    col(Mentorada.competencias_interesse).label("skills"),
                    col(Mentorada.linkedin).label("linkedin"),
                    col(Mentorada.foto_perfil).label("foto")
                )\
                .where(Mentorada.conta_ativa == False)\
                .join(Usuario)\
            ).mappings().all()
            return mentees
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    @staticmethod
    def update_approval_mentee(data : UpdateApprovalMentee,token : str, session : Session):
        user = get_current_user(token, session)
        try:
            if user is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            statement = select(Administrador).where(Administrador.id_usuario == user.id_usuario)
            admin = session.exec(statement).one_or_none()
            if admin is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            mentee = session.exec(
                select(Mentorada)\
                .where(Mentorada.id_mentorada == data.mentee_id)
            ).one_or_none()
            if mentee is None:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST)
            mentee.conta_ativa = data.approved
            session.commit()
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
