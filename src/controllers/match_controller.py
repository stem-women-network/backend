from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import (
    PedidosMentoria,
    Mentorada,
    Mentora,
    Mentoria,
)
from pydantic import BaseModel


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


class MatchController:
    """Controller for mentorship matching"""

    @staticmethod
    def create_match(request: MatchRequest, session: Session) -> MatchResponse:
        """Create matching between mentee and available mentors"""
        # Get mentorada
        mentorada = session.get(Mentorada, request.id_mentorada)
        if not mentorada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada not found"
            )

        # Find available mentors with same university
        statement = select(Mentora).where(
            Mentora.id_universidade_instituicao
            == mentorada.id_universidade_instituicao,
            Mentora.conta_ativa == True,
        )
        mentoras_disponiveis = session.exec(statement).all()

        if not mentoras_disponiveis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available mentors found",
            )

        # Create mentoria for each available mentor
        mentorias_criadas = []
        for mentora in mentoras_disponiveis:
            mentoria = Mentoria(
                estado_mentoria="ativa",
                id_mentora=mentora.id_mentora,
                id_mentorada=mentorada.id_mentorada,
            )
            session.add(mentoria)
            mentorias_criadas.append(mentoria.id_mentoria)

        session.commit()

        return MatchResponse(
            mentorias_criadas=mentorias_criadas,
            mensagem=f"Matching created with {len(mentoras_disponiveis)} mentors",
        )

    @staticmethod
    def create_mentorship_request(
        data: PedidoMentoriaCreate, session: Session
    ) -> PedidosMentoria:
        """Create a mentorship request"""
        mentora = session.get(Mentora, data.id_mentora)
        mentorada = session.get(Mentorada, data.id_mentorada)

        if not mentora:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found"
            )
        if not mentorada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada not found"
            )

        pedido = PedidosMentoria(
            estado_pedido="pendente",
            ano_pedido=data.ano_pedido,
            id_mentora=data.id_mentora,
            id_mentorada=data.id_mentorada,
        )
        session.add(pedido)
        session.commit()
        session.refresh(pedido)
        return pedido

    @staticmethod
    def get_mentorship_request(
        id_pedidos_mentoria: int, session: Session
    ) -> PedidosMentoria:
        pedido = session.get(PedidosMentoria, id_pedidos_mentoria)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado"
            )
        return pedido

    @staticmethod
    def list_mentorship_requests(session: Session) -> list[PedidosMentoria]:
        pedidos = session.exec(select(PedidosMentoria)).all()
        return pedidos

    @staticmethod
    def update_mentorship_request(
        id_pedidos_mentoria: int, estado_pedido: str, session: Session
    ) -> PedidosMentoria:
        pedido = session.get(PedidosMentoria, id_pedidos_mentoria)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado"
            )

        pedido.estado_pedido = estado_pedido
        session.add(pedido)
        session.commit()
        session.refresh(pedido)
        return pedido

    @staticmethod
    def delete_mentorship_request(
        id_pedidos_mentoria: int, session: Session
    ) -> dict:
        pedido = session.get(PedidosMentoria, id_pedidos_mentoria)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado"
            )

        session.delete(pedido)
        session.commit()
        return {"message": "Pedido deletado com sucesso"}
