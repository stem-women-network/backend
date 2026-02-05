from fastapi import APIRouter
from src.controllers.match_controller import (
    MatchController,
    PedidoMentoriaResponse,
    PedidoMentoriaCreate,
    MatchRequest,
    MatchResponse,
    MentorSuggestion,
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


@router.get("/pedidos/", response_model=list[PedidoMentoriaResponse])
def list_mentorship_requests(session: SessionDep):
    return MatchController.list_mentorship_requests(session)


@router.put("/pedidos/{id_pedidos_mentoria}")
def update_mentorship_request(id_pedidos_mentoria: int, estado_pedido: str, session: SessionDep):
    return MatchController.update_mentorship_request(id_pedidos_mentoria, estado_pedido, session)


@router.delete("/pedidos/{id_pedidos_mentoria}")
def delete_mentorship_request(id_pedidos_mentoria: int, session: SessionDep):
    return MatchController.delete_mentorship_request(id_pedidos_mentoria, session)


@router.get("/suggestions/mentor/{id_mentora}", response_model=list[MentorSuggestion])
def get_suggested_mentees(id_mentora: int, session: SessionDep, top_k: int | None = 5, min_score: int | None = 1, same_university: bool | None = False):
    return MatchController.get_suggested_mentees_for_mentor(id_mentora, session, top_k=top_k, min_score=min_score, same_university=same_university)


@router.post("/suggestions/mentor/{id_mentora}/{id_mentorada}", response_model=PedidoMentoriaResponse)
def mentor_create_request(id_mentora: int, id_mentorada: int, session: SessionDep):
    return MatchController.mentor_create_request(id_mentora, id_mentorada, session)
