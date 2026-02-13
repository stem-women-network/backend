from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, col, func, select
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR
from src.models.login import get_current_user
from src.schemas.tables import Administrador, Coordenador, Mentora, Mentoria, UniversidadeInstituicao, Usuario
from pydantic import BaseModel

class UniversityResponse(BaseModel):
    id: UUID
    name: str
    coord: str

class UniversityCreate(BaseModel):
    nome_instituicao: str


class UniversityUpdate(BaseModel):
    nome_instituicao: str | None = None


class UniversityController:
    @staticmethod
    def list_universities(token : str, session: Session) -> list[dict]:
        user = get_current_user(token, session)
        try:
            if user is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            statement = select(Administrador).where(Administrador.id_usuario == user.id_usuario)
            admin = session.exec(statement).one_or_none()
            if admin is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            universidades = session.exec(
                    select(col(UniversidadeInstituicao.id_universidade_instituicao).label("id"),
                           col(UniversidadeInstituicao.nome_instituicao).label("name"),
                           col(Usuario.nome_completo).label("coord"),
                           func.count().label("matches")
                           )\
                    .join(UniversidadeInstituicao.coordenadores)
                    .join(Usuario, Usuario.id_usuario == Coordenador.id_usuario)\
                    .join(Mentora, Mentora.id_universidade_instituicao == UniversidadeInstituicao.id_universidade_instituicao)\
                    .where(Mentora.conta_ativa)\
                    .join(Mentoria)\
                    .group_by(UniversidadeInstituicao.id_universidade_instituicao,
                              UniversidadeInstituicao.nome_instituicao,
                              Usuario.nome_completo,
                              Mentoria.estado_mentoria
                              )\
                    .where(Mentoria.estado_mentoria == "ativa")\
                ).mappings().all()
            print(universidades)
            return universidades
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    @staticmethod
    def get_universities_names(session : Session):
        try:
            universidades = session.exec(
                    select(
                        col(UniversidadeInstituicao.id_universidade_instituicao).label("id"),
                        col(UniversidadeInstituicao.nome_instituicao).label("name"),
                    )
            ).mappings().all()
            return universidades
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR)
        
    @staticmethod
    def get_count(token: str, session: Session) -> dict[str,int]:
        user = get_current_user(token, session)
        try:
            if user is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            statement = select(Administrador).where(Administrador.id_usuario == user.id_usuario)
            admin = session.exec(statement).one_or_none()
            if admin is None:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
            count = session.exec(select(func.count()).select_from(UniversidadeInstituicao)).one()
            return {"count" : count}
        except Exception as e:
            print(e)
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    @staticmethod
    def get_university(
        id_universidade_instituicao: UUID, session: Session
    ) -> UniversidadeInstituicao:
        universidade = session.get(UniversidadeInstituicao, id_universidade_instituicao)
        if not universidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Universidade não encontrada",
            )
        return universidade

    @staticmethod
    def create_university(
        data: UniversityCreate, session: Session
    ) -> UniversidadeInstituicao:
        if not data.nome_instituicao or not data.nome_instituicao.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nome da universidade não pode estar vazio",
            )
        
        existing = session.exec(
            select(UniversidadeInstituicao).where(
                UniversidadeInstituicao.nome_instituicao == data.nome_instituicao
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Universidade já existe",
            )
        
        universidade = UniversidadeInstituicao(
            nome_instituicao=data.nome_instituicao.strip()
        )
        session.add(universidade)
        session.commit()
        session.refresh(universidade)
        return universidade

    @staticmethod
    def update_university(
        id_universidade_instituicao: UUID, data: UniversityUpdate, session: Session
    ) -> UniversidadeInstituicao:
        universidade = session.get(UniversidadeInstituicao, id_universidade_instituicao)
        if not universidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Universidade não encontrada",
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
        id_universidade_instituicao: UUID, session: Session
    ) -> dict:
        universidade = session.get(UniversidadeInstituicao, id_universidade_instituicao)
        if not universidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Universidade não encontrada",
            )

        session.delete(universidade)
        session.commit()
        return {"message": "Universidade deletada com sucesso"}
