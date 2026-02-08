from fastapi import APIRouter, HTTPException, Request, Response
from starlette.status import HTTP_401_UNAUTHORIZED
from src.controllers.match_controller import (
    MatchController,
    MatchSugerido,
    PedidoMentoriaResponse,
    PedidoMentoriaCreate,
    MatchRequest,
    MatchResponse,
    MentorSuggestion,
)
from src.database import SessionDep

router = APIRouter()


@router.post("/")
def create_match(matchRequest: MatchRequest, request: Request ,response: Response, session: SessionDep):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        return MatchController.create_match(token, matchRequest, session)
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


# @router.post("/pedidos", response_model=PedidoMentoriaResponse)
# def create_mentorship_request(data: PedidoMentoriaCreate, session: SessionDep):
#     return MatchController.create_mentorship_request(data, session)


@router.get("/pedidos/{id_pedidos_mentoria}", response_model=PedidoMentoriaResponse)
def get_mentorship_request(id_pedidos_mentoria: int, session: SessionDep):
    return MatchController.get_mentorship_request(id_pedidos_mentoria, session)


@router.get("/pedidos/", response_model=list[MatchSugerido])
def list_mentorship_requests(request : Request, response: Response, session: SessionDep):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        return MatchController.list_mentorship_requests(token, session)
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


@router.put("/pedidos/{id_pedidos_mentoria}")
def update_mentorship_request(id_pedidos_mentoria: str, estado_match: str, request : Request, response: Response ,session: SessionDep):
    authorization = request.headers.get("authorization")
    if authorization is not None:
        token = authorization.split(" ")[1]
        return MatchController.update_mentorship_request(token, id_pedidos_mentoria, estado_match, session)
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

@router.delete("/pedidos/{id_pedidos_mentoria}")
def delete_mentorship_request(id_pedidos_mentoria: int, request : Request, response: Response ,session: SessionDep):
    authorization = request.headers.get("authorization")
    print("teste")
    if authorization is not None:
        token = authorization.split(" ")[1]
        return MatchController.delete_mentorship_request(token, id_pedidos_mentoria, session)
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


# @router.get("/suggestions/mentor/{id_mentora}", response_model=list[MentorSuggestion])
# def get_suggested_mentees(id_mentora: int, session: SessionDep, top_k: int | None = 5, min_score: int | None = 1, same_university: bool | None = False):
#     return MatchController.get_suggested_mentees_for_mentor(id_mentora, session, top_k=top_k, min_score=min_score, same_university=same_university)


# @router.post("/suggestions/mentor/{id_mentora}/{id_mentorada}", response_model=PedidoMentoriaResponse)
# def mentor_create_request(id_mentora: int, id_mentorada: int, session: SessionDep):
#     return MatchController.mentor_create_request(id_mentora, id_mentorada, session)
