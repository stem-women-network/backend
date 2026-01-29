from fastapi import APIRouter
from src.controllers.match_controller import (
    MatchController,
    PedidoMentoriaResponse,
    PedidoMentoriaCreate,
    MatchRequest,
    MatchResponse,
)
from src.database import SessionDep

router = APIRouter()


@router.post("/", response_model=MatchResponse)
def create_match(request: MatchRequest, session: SessionDep):
    return MatchController.create_match(request, session)


@router.post("/pedidos", response_model=PedidoMentoriaResponse)
def create_mentorship_request(data: PedidoMentoriaCreate, session: SessionDep):
    return MatchController.create_mentorship_request(data, session)


@router.get("/pedidos/{id_pedidos_mentoria}", response_model=PedidoMentoriaResponse)
def get_mentorship_request(id_pedidos_mentoria: int, session: SessionDep):
    return MatchController.get_mentorship_request(id_pedidos_mentoria, session)


@router.get("/pedidos/")
def list_mentorship_requests(session: SessionDep):
    return MatchController.list_mentorship_requests(session)


@router.put("/pedidos/{id_pedidos_mentoria}")
def update_mentorship_request(id_pedidos_mentoria: int, estado_pedido: str, session: SessionDep):
    return MatchController.update_mentorship_request(id_pedidos_mentoria, estado_pedido, session)


@router.delete("/pedidos/{id_pedidos_mentoria}")
def delete_mentorship_request(id_pedidos_mentoria: int, session: SessionDep):
    return MatchController.delete_mentorship_request(id_pedidos_mentoria, session)
