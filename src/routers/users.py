from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import Usuario, Mentorada, Mentora
from src.database import SessionDep
from pydantic import BaseModel, EmailStr

router = APIRouter()

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

@router.get("/", response_model=list[UsuarioResponse])
def list_users(session: SessionDep):
    """List all users"""
    usuarios = session.exec(select(Usuario)).all()
    return usuarios

@router.get("/{id_usuario}", response_model=UsuarioResponse)
def get_user(id_usuario: int, session: SessionDep):
    """Get a specific user by ID"""
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return usuario

@router.post("/", response_model=UsuarioResponse)
def create_user(data: UsuarioCreate, session: SessionDep):
    """Create a new user"""
    # Check if email already exists
    statement = select(Usuario).where(Usuario.email == data.email)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    
    usuario = Usuario(**data.dict())
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

@router.put("/{id_usuario}", response_model=UsuarioResponse)
def update_user(id_usuario: int, data: UsuarioUpdate, session: SessionDep):
    """Update a user"""
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usuario, key, value)
    
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

@router.delete("/{id_usuario}")
def delete_user(id_usuario: int, session: SessionDep):
    """Delete a user"""
    usuario = session.get(Usuario, id_usuario)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    session.delete(usuario)
    session.commit()
    return {"message": "User deleted successfully"}
