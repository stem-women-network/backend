from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from src.schemas.tables import (
    PedidosMentoria, Mentorada, Mentora, Mentoria
)
from src.database import SessionDep
from pydantic import BaseModel

router = APIRouter()

class PedidoMentoriaResponse(BaseModel):
    id_pedidos_mentoria: int
    estado_pedido: str
    ano_pedido: int
    id_mentora: int
    id_mentorada: int

class PedidoMentoriaCreate(BaseModel):
    id_mentora: int
    id_mentorada: int
    ano_pedido: int

class MatchRequest(BaseModel):
    id_mentorada: int

class MatchResponse(BaseModel):
    mentorias_criadas: list[int]
    mensagem: str

@router.post("/", response_model=MatchResponse)
def create_match(request: MatchRequest, session: SessionDep):
    """Create matching between mentee and available mentors"""
    # Get mentorada
    mentorada = session.get(Mentorada, request.id_mentorada)
    if not mentorada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada not found")
    
    # Find available mentors with same university
    statement = select(Mentora).where(
        Mentora.id_universidade_instituicao == mentorada.id_universidade_instituicao,
        Mentora.conta_ativa == True
    )
    mentoras_disponiveis = session.exec(statement).all()
    
    if not mentoras_disponiveis:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No available mentors found")
    
    # Create mentoria for each available mentor
    mentorias_criadas = []
    for mentora in mentoras_disponiveis:
        mentoria = Mentoria(
            estado_mentoria="ativa",
            id_mentora=mentora.id_mentora,
            id_mentorada=mentorada.id_mentorada
        )
        session.add(mentoria)
        mentorias_criadas.append(mentoria.id_mentoria)
    
    session.commit()
    
    return MatchResponse(
        mentorias_criadas=mentorias_criadas,
        mensagem=f"Matching created with {len(mentoras_disponiveis)} mentors"
    )

@router.post("/pedidos", response_model=PedidoMentoriaResponse)
def create_mentorship_request(data: PedidoMentoriaCreate, session: SessionDep):
    """Create a mentorship request"""
    mentora = session.get(Mentora, data.id_mentora)
    mentorada = session.get(Mentorada, data.id_mentorada)
    
    if not mentora:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    if not mentorada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada not found")
    
    pedido = PedidosMentoria(
        estado_pedido="pendente",
        ano_pedido=data.ano_pedido,
        id_mentora=data.id_mentora,
        id_mentorada=data.id_mentorada
    )
    session.add(pedido)
    session.commit()
    session.refresh(pedido)
    return pedido

@router.get("/pedidos/{id_pedidos_mentoria}", response_model=PedidoMentoriaResponse)
def get_mentorship_request(id_pedidos_mentoria: int, session: SessionDep):
    """Get a mentorship request"""
    pedido = session.get(PedidosMentoria, id_pedidos_mentoria)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return pedido

@router.get("/pedidos/")
def list_mentorship_requests(session: SessionDep):
    """List all mentorship requests"""
    pedidos = session.exec(select(PedidosMentoria)).all()
    return pedidos

@router.put("/pedidos/{id_pedidos_mentoria}")
def update_mentorship_request(id_pedidos_mentoria: int, estado_pedido: str, session: SessionDep):
    """Update mentorship request status"""
    pedido = session.get(PedidosMentoria, id_pedidos_mentoria)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    pedido.estado_pedido = estado_pedido
    session.add(pedido)
    session.commit()
    session.refresh(pedido)
    return pedido

@router.delete("/pedidos/{id_pedidos_mentoria}")
def delete_mentorship_request(id_pedidos_mentoria: int, session: SessionDep):
    """Delete a mentorship request"""
    pedido = session.get(PedidosMentoria, id_pedidos_mentoria)
    if not pedido:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    session.delete(pedido)
    session.commit()
    return {"message": "Request deleted successfully"}
