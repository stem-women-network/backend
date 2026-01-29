from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import Usuario
from pydantic import BaseModel, EmailStr


class UsuarioResponse(BaseModel):
    id_usuario: int
    nome_completo: str
    cpf: str
    email: EmailStr


class UsuarioCreate(BaseModel):
    nome_completo: str
    cpf: str
    email: EmailStr
    senha: str


class UsuarioUpdate(BaseModel):
    nome_completo: str | None = None
    email: EmailStr | None = None


class UserController:
    """Controller for user management"""

    @staticmethod
    def list_users(session: Session) -> list[Usuario]:
        """List all users"""
        usuarios = session.exec(select(Usuario)).all()
        return usuarios

    @staticmethod
    def get_user(id_usuario: int, session: Session) -> Usuario:
        """Get a specific user by ID"""
        usuario = session.get(Usuario, id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )
        return usuario

    @staticmethod
    def create_user(data: UsuarioCreate, session: Session) -> Usuario:
        statement = select(Usuario).where(Usuario.email == data.email)
        existing = session.exec(statement).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email já existe"
            )

        usuario = Usuario(**data.dict())
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario

    @staticmethod
    def update_user(id_usuario: int, data: UsuarioUpdate, session: Session) -> Usuario:
        usuario = session.get(Usuario, id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(usuario, key, value)

        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return usuario

    @staticmethod
    def delete_user(id_usuario: int, session: Session) -> dict:
        usuario = session.get(Usuario, id_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )

        session.delete(usuario)
        session.commit()
        return {"message": "Usuário deletado com sucesso"}
