from fastapi import APIRouter
from src.controllers.user_controller import (
    UserController,
    UsuarioResponse,
    UsuarioCreate,
    UsuarioUpdate,
)
from src.database import SessionDep

router = APIRouter()


@router.get("/", response_model=list[UsuarioResponse])
def list_users(session: SessionDep):
    """Listar todos os usuários"""
    return UserController.list_users(session)


@router.get("/{id_usuario}", response_model=UsuarioResponse)
def get_user(id_usuario: int, session: SessionDep):
    """Obter um usuário específico por ID"""
    return UserController.get_user(id_usuario, session)


@router.post("/", response_model=UsuarioResponse)
def create_user(data: UsuarioCreate, session: SessionDep):
    """Criar um novo usuário"""
    return UserController.create_user(data, session)


@router.put("/{id_usuario}", response_model=UsuarioResponse)
def update_user(id_usuario: int, data: UsuarioUpdate, session: SessionDep):
    """Atualizar um usuário"""
    return UserController.update_user(id_usuario, data, session)


@router.delete("/{id_usuario}")
def delete_user(id_usuario: int, session: SessionDep):
    """Deletar um usuário"""
    return UserController.delete_user(id_usuario, session)
