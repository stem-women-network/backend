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
    id_pedidos_mentoria: str
    estado_pedido: str
    ano_pedido: int
    id_mentora: str
    id_mentorada: str


class PedidoMentoriaCreate(BaseModel):
    id_mentora: str
    id_mentorada: str
    ano_pedido: int


class MatchRequest(BaseModel):
    id_mentorada: int
    top_k: int | None = 3  # number of top mentor suggestions to create pedidos for
    min_score: int | None = 1  # minimum score required to consider a match


class MatchItem(BaseModel):
    id_mentora: str
    id_pedido: str | None = None
    score: int
    objetivo_mentoria: str
    curso_mentorada: str


class MentorSuggestion(BaseModel):
    id_mentorada: str
    score: int
    objetivo_mentoria: str
    curso_mentorada: str
    shared_competencias: list[str] = []
    shared_hobbies: list[str] = []


class MatchResponse(BaseModel):
    pedidos_criados: list[str]
    matches: list[MatchItem]
    mensagem: str


class MatchController:

    @staticmethod
    def _normalize_text(text: str) -> str:
        return (text or "").lower()

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        import re

        text = MatchController._normalize_text(text)
        tokens = re.split(r"\W+", text)
        return set(t for t in tokens if t)

    @staticmethod
    def _score_by_text(areas: list[str], text: str) -> int:
        """Score overlap between mentor areas and a text field (course or objective)"""
        text_str = MatchController._normalize_text(text)
        text_tokens = MatchController._tokenize(text)

        score = 0
        for area in areas or []:
            area_norm = MatchController._normalize_text(area)
            if not area_norm:
                continue
            if area_norm in text_str:
                score += 3
                continue
            area_tokens = MatchController._tokenize(area_norm)
            common = area_tokens.intersection(text_tokens)
            score += len(common)
        return score

    @staticmethod
    def _score_match(areas: list[str], curso: str, objetivo: str) -> int:
        """Combine course (higher weight) and objective into final score"""
        course_score = MatchController._score_by_text(areas, curso)
        objetivo_score = MatchController._score_by_text(areas, objetivo)
        return course_score * 2 + objetivo_score

    @staticmethod
    def create_match(request: MatchRequest, session: Session) -> MatchResponse:
        """Create pending mentorship requests (pedidos) for mentors to accept.

        Rules:
        - Do not create requests if mentee or mentor already has an active mentorship or pending pedido.
        - Only create PedidosMentoria (estado_pedido='pendente') so mentors can accept (mentor-only action).
        """
        from datetime import datetime

        # Get mentorada
        mentorada = session.get(Mentorada, request.id_mentorada)
        if not mentorada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada not found"
            )

        # Prevent mentee from having more than one match
        existing_active = session.exec(
            select(Mentoria).where(
                Mentoria.id_mentorada == mentorada.id_mentorada,
                Mentoria.estado_mentoria == "ativa",
            )
        ).first()
        existing_pending = session.exec(
            select(PedidosMentoria).where(
                PedidosMentoria.id_mentorada == mentorada.id_mentorada,
                PedidosMentoria.estado_pedido == "pendente",
            )
        ).first()

        if existing_active or existing_pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mentorada already has an active or pending mentorship",
            )

        statement = select(Mentora).where(
            Mentora.conta_ativa == True,
        )
        mentoras_disponiveis = session.exec(statement).all()

        available_mentors = []
        for mentora in mentoras_disponiveis:
            mentor_active = session.exec(
                select(Mentoria).where(
                    Mentoria.id_mentora == mentora.id_mentora,
                    Mentoria.estado_mentoria == "ativa",
                )
            ).first()
            mentor_pending = session.exec(
                select(PedidosMentoria).where(
                    PedidosMentoria.id_mentora == mentora.id_mentora,
                    PedidosMentoria.estado_pedido == "pendente",
                )
            ).first()
            if mentor_active or mentor_pending:
                continue
            available_mentors.append(mentora)

        if not available_mentors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available mentors found",
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

        # Ensure neither mentor nor mentee already has an active or pending match
        mentor_active = session.exec(
            select(Mentoria).where(
                Mentoria.id_mentora == mentora.id_mentora,
                Mentoria.estado_mentoria == "ativa",
            )
        ).first()
        mentor_pending = session.exec(
            select(PedidosMentoria).where(
                PedidosMentoria.id_mentora == mentora.id_mentora,
                PedidosMentoria.estado_pedido == "pendente",
            )
        ).first()
        mentee_active = session.exec(
            select(Mentoria).where(
                Mentoria.id_mentorada == mentorada.id_mentorada,
                Mentoria.estado_mentoria == "ativa",
            )
        ).first()
        mentee_pending = session.exec(
            select(PedidosMentoria).where(
                PedidosMentoria.id_mentorada == mentorada.id_mentorada,
                PedidosMentoria.estado_pedido == "pendente",
            )
        ).first()

        if mentor_active or mentor_pending or mentee_active or mentee_pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mentor or mentored already has an active or pending mentorship",
            )

        import uuid

        pedido = PedidosMentoria(
            estado_pedido="pendente",
            ano_pedido=data.ano_pedido,
            id_mentora=uuid.UUID(data.id_mentora),
            id_mentorada=uuid.UUID(data.id_mentorada),
        )
        session.add(pedido)
        session.commit()
        session.refresh(pedido)
        return pedido

    @staticmethod
    def get_suggested_mentees_for_mentor(
        id_mentora: int,
        session: Session,
        top_k: int | None = 5,
        min_score: int | None = 1,
    ) -> list["MentorSuggestion"]:
        """Return mentees compatible with a mentor so the mentor can accept/ask for mentorships."""
        mentor = session.get(Mentora, id_mentora)
        if not mentor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentora not found"
            )

        # Do not show suggestions if mentor already has active or pending match
        mentor_active = session.exec(
            select(Mentoria).where(
                Mentoria.id_mentora == mentor.id_mentora,
                Mentoria.estado_mentoria == "ativa",
            )
        ).first()
        mentor_pending = session.exec(
            select(PedidosMentoria).where(
                PedidosMentoria.id_mentora == mentor.id_mentora,
                PedidosMentoria.estado_pedido == "pendente",
            )
        ).first()
        if mentor_active or mentor_pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mentora already has an active or pending mentorship",
            )

        # Find active mentees (no university restriction)
        statement = select(Mentorada).where(
            Mentorada.conta_ativa == True,
        )
        possible_mentees = session.exec(statement).all()

        # Filter out mentees who already have active/pending
        filtered = []
        for m in possible_mentees:
            mentee_active = session.exec(
                select(Mentoria).where(
                    Mentoria.id_mentorada == m.id_mentorada,
                    Mentoria.estado_mentoria == "ativa",
                )
            ).first()
            mentee_pending = session.exec(
                select(PedidosMentoria).where(
                    PedidosMentoria.id_mentorada == m.id_mentorada,
                    PedidosMentoria.estado_pedido == "pendente",
                )
            ).first()
            if mentee_active or mentee_pending:
                continue
            filtered.append(m)

        if not filtered:
            return []

        # Score each mentee
        scored: list[tuple[int, Mentorada]] = []
        for m in filtered:
            score = 0
            # expertise (areas_atuacao) vs mentee competencias_interesse -> strong
            for exp in mentor.areas_atuacao or []:
                if not exp:
                    continue
                if exp in (m.competencias_interesse or []):
                    score += 3
                # partial token overlap
                exp_tokens = MatchController._tokenize(exp)
                comp_tokens = MatchController._tokenize(" ".join(m.competencias_interesse or []))
                score += len(exp_tokens.intersection(comp_tokens))
                # course match
                if exp.lower() in (m.curso_area_stem or "").lower():
                    score += 2
            # hobbies overlap
            hobby_overlap = set(mentor.hobbies or []).intersection(set(m.hobbies or []))
            score += len(hobby_overlap)
            scored.append((score, m))

        scored.sort(key=lambda x: x[0], reverse=True)

        min_score = min_score if min_score is not None else 1
        top_k = top_k if top_k is not None else 5
        selected = [(s, mm) for s, mm in scored if s >= min_score]
        if not selected and scored:
            selected = [scored[0]]
        selected = selected[:top_k]

        results: list[MentorSuggestion] = []
        for score, mm in selected:
            shared_comp = []
            shared_hob = []
            # compute shared lists
            if mm.competencias_interesse:
                shared_comp = [c for c in (mm.competencias_interesse or []) if c in (mentor.areas_atuacao or [])]
            if mm.hobbies:
                shared_hob = [h for h in (mm.hobbies or []) if h in (mentor.hobbies or [])]

            results.append(
                MentorSuggestion(
                    id_mentorada=str(mm.id_mentorada),
                    score=score,
                    objetivo_mentoria=mm.objetivo_mentoria or "",
                    curso_mentorada=mm.curso_area_stem or "",
                    shared_competencias=shared_comp,
                    shared_hobbies=shared_hob,
                )
            )
        return results

    @staticmethod
    def mentor_create_request(
        id_mentora: int, id_mentorada: int, session: Session
    ) -> PedidosMentoria:
        """Allow mentor to create a pending request to a mentee (accept suggestion)."""
        mentora = session.get(Mentora, id_mentora)
        mentorada = session.get(Mentorada, id_mentorada)
        if not mentora or not mentorada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentora or Mentorada not found"
            )

        # Ensure neither has active/pending
        mentor_active = session.exec(
            select(Mentoria).where(
                Mentoria.id_mentora == mentora.id_mentora,
                Mentoria.estado_mentoria == "ativa",
            )
        ).first()
        mentor_pending = session.exec(
            select(PedidosMentoria).where(
                PedidosMentoria.id_mentora == mentora.id_mentora,
                PedidosMentoria.estado_pedido == "pendente",
            )
        ).first()
        mentee_active = session.exec(
            select(Mentoria).where(
                Mentoria.id_mentorada == mentorada.id_mentorada,
                Mentoria.estado_mentoria == "ativa",
            )
        ).first()
        mentee_pending = session.exec(
            select(PedidosMentoria).where(
                PedidosMentoria.id_mentorada == mentorada.id_mentorada,
                PedidosMentoria.estado_pedido == "pendente",
            )
        ).first()

        if mentor_active or mentor_pending or mentee_active or mentee_pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mentor or mentored already has an active or pending mentorship",
            )

        from datetime import datetime

        pedido = PedidosMentoria(
            estado_pedido="pendente",
            ano_pedido=datetime.now().year,
            id_mentora=mentora.id_mentora,
            id_mentorada=mentorada.id_mentorada,
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
        pedidos = list(session.exec(select(PedidosMentoria)).all())
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

        # If the mentor accepts the pedido, create an active Mentoria and clear other pending requests
        if estado_pedido.lower() in ("aceita", "aceito", "aprovado", "accepted"):
            # Ensure neither mentor nor mentee already have active mentorships
            mentor_active = session.exec(
                select(Mentoria).where(
                    Mentoria.id_mentora == pedido.id_mentora,
                    Mentoria.estado_mentoria == "ativa",
                )
            ).first()
            mentee_active = session.exec(
                select(Mentoria).where(
                    Mentoria.id_mentorada == pedido.id_mentorada,
                    Mentoria.estado_mentoria == "ativa",
                )
            ).first()
            if mentor_active or mentee_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mentor or mentored already has an active mentorship",
                )

            # Create active mentorship
            mentoria = Mentoria(
                estado_mentoria="ativa",
                avaliacao_mentora=None,
                avaliacao_mentorada=None,
                nota_mentora=None,
                nota_mentorada=None,
                id_mentora=pedido.id_mentora,
                id_mentorada=pedido.id_mentorada,
            )
            session.add(mentoria)

            # Mark this pedido as accepted
            pedido.estado_pedido = estado_pedido
            session.add(pedido)

            # Remove other pending pedidos involving these users
            other_pedidos = session.exec(
                select(PedidosMentoria).where(
                    (PedidosMentoria.id_mentora == pedido.id_mentora)
                    | (PedidosMentoria.id_mentorada == pedido.id_mentorada),
                    PedidosMentoria.estado_pedido == "pendente",
                )
            ).all()
            for op in other_pedidos:
                if op.id_pedidos_mentoria == pedido.id_pedidos_mentoria:
                    continue
                session.delete(op)

            session.commit()
            session.refresh(pedido)
            return pedido

        # Otherwise just update the pedido state (e.g., 'rejeitado')
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
