from typing import Literal
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.models.login import TipoUsuario, get_current_user, get_tipo_usuario
from src.schemas.tables import (
    PedidosMentoria,
    Mentorada,
    Mentora,
    Mentoria,
    Usuario,
)
from pydantic import BaseModel


from datetime import datetime

class MatchSugerido(BaseModel):
    class MentoraOptional(BaseModel):
        nome : str
        cargo : str
        skills : list[str]
        foto : bytes | None

    class MentoradaOptional(BaseModel):
        nome : str
        curso : str
        objetivo : str
        foto : bytes | None
        
    id : UUID
    score : int
    motivo : str
    mentora: MentoraOptional
    mentorada : MentoradaOptional

class PedidoMentoriaResponse(BaseModel):
    id_pedidos_mentoria: str
    estado_pedido: str
    data_pedido: datetime
    id_mentora: str
    id_mentorada: str
    objetivo_mentoria: str


class PedidoMentoriaCreate(BaseModel):
    id_mentora: str
    id_mentorada: str
    data_pedido: datetime | None = None


class MatchRequest(BaseModel):
    top_k: int | None = 3
    min_score: int | None = 1
    id_universidade : str | None = None
    same_university: bool | None = False

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
    def _score_match(
        mentor_competencias: list[str],
        mentor_hobbies: list[str],
        mentee_competencias: list[str],
        mentee_hobbies: list[str],
        mentee_curso: str,
    ) -> tuple[int, list[str], list[str]]:
        """
        - mesmas competencias => 5 points cada -- máx 20
        - mesmo curso => 3 points -- máx 3
        - mesmos hobbies => 1 point cada -- max 22
        - máximo de points é igual a 45
        """
        # TODO mudar pontuação
        shared_comp = [c for c in mentee_competencias if c in mentor_competencias]
        shared_hob = [h for h in mentee_hobbies if h in mentor_hobbies]

        score = 0
        score += 5 * len(shared_comp)
        score += 1 * len(shared_hob)
        if mentee_curso in mentor_competencias:
            score += 3
        return score, shared_comp, shared_hob

    @staticmethod
    def create_match(token: str,request : MatchRequest, session: Session) -> str | None:
        user = get_current_user(token, session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )
        user_type = get_tipo_usuario(user)
        if user_type == TipoUsuario.ADMIN:
            mentoradas = session.exec(select(Mentorada)\
                                      .where(Mentorada.conta_ativa)
                                      ).all()
            for mentorada in mentoradas:
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
                    continue

                # TODO precisa ser da mesma faculdade?
                if request.same_university:
                    statement = select(Mentora).where(
                        Mentora.id_universidade_instituicao
                        == mentorada.id_universidade_instituicao,
                        Mentora.conta_ativa == True,
                    )
                else:
                    statement = select(Mentora).where(
                        Mentora.conta_ativa == True,
                    )
                mentoras_disponiveis = session.exec(statement).all()

                available_mentors : list[Mentora] = []
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

                # TODO atualmente as areas de atuacao da mentora e
                # competencias de interesse da mentorada devem ser exatamente iguais
                scored: list[tuple[int, Mentora, list[str], list[str]]] = []
                for mentora in available_mentors:
                    score, shared_comp, shared_hob = MatchController._score_match(
                        mentora.competencias,
                        mentora.hobbies,
                        mentorada.competencias_interesse,
                        mentorada.hobbies,
                        mentorada.curso,
                    )
                    scored.append((score, mentora, shared_comp, shared_hob))

                # x[0] é o score
                scored.sort(key=lambda x: x[0], reverse=True)

                min_score = request.min_score if request.min_score is not None else 1
                top_k = request.top_k if request.top_k is not None else 3

                # score, mentora, shared_comp, shared_hob
                selected = [ (s, m, sc, sh) for s, m, sc, sh in scored if s >= min_score ]

                # TODO fazer ter pelo menos um match?
                if not selected and scored:
                    selected = [scored[0]]
                    
                selected = selected[:top_k]
                current_time = datetime.now()
                MAX_POINTS = 45
                for score, mentora, shared_comp, shared_hob in selected:
                    pedido = PedidosMentoria(
                        estado_pedido="pendente",
                        pontuacao = round((score / MAX_POINTS) * 100),
                        motivo = (shared_comp + shared_hob),
                        data_pedido=current_time,
                        id_mentora=mentora.id_mentora,
                        id_mentorada=mentorada.id_mentorada,
                    )
                    session.add(pedido)
                    session.commit()
                    break
            return "Os matches foram criados"
        else:
            raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Houve um erro ao criar os matches",
                    )

    # @staticmethod
    # def create_mentorship_request(
    #     data: PedidoMentoriaCreate, session: Session
    # ) -> PedidosMentoria:
    #     mentora = session.get(Mentora, data.id_mentora)
    #     mentorada = session.get(Mentorada, data.id_mentorada)

    #     if not mentora:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Mentora não encontrada"
    #         )
    #     if not mentorada:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada não encontrada"
    #         )

    #     # Ensure neither mentor nor mentee already has an active or pending match
    #     mentor_active = session.exec(
    #         select(Mentoria).where(
    #             Mentoria.id_mentora == mentora.id_mentora,
    #             Mentoria.estado_mentoria == "ativa",
    #         )
    #     ).first()
    #     mentor_pending = session.exec(
    #         select(PedidosMentoria).where(
    #             PedidosMentoria.id_mentora == mentora.id_mentora,
    #             PedidosMentoria.estado_pedido == "pendente",
    #         )
    #     ).first()
    #     mentee_active = session.exec(
    #         select(Mentoria).where(
    #             Mentoria.id_mentorada == mentorada.id_mentorada,
    #             Mentoria.estado_mentoria == "ativa",
    #         )
    #     ).first()
    #     mentee_pending = session.exec(
    #         select(PedidosMentoria).where(
    #             PedidosMentoria.id_mentorada == mentorada.id_mentorada,
    #             PedidosMentoria.estado_pedido == "pendente",
    #         )
    #     ).first()

    #     if mentor_active or mentor_pending or mentee_active or mentee_pending:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Mentora ou mentorada já tem um match ativo",
    #         )

    #     import uuid

    #     pedido = PedidosMentoria(
    #         estado_pedido="pendente",
    #         data_pedido=data.data_pedido or datetime.now(),
    #         id_mentora=uuid.UUID(data.id_mentora),
    #         id_mentorada=uuid.UUID(data.id_mentorada),
    #     )
    #     session.add(pedido)
    #     session.commit()
    #     session.refresh(pedido)
    #     return pedido

    # @staticmethod
    # def get_suggested_mentees_for_mentor(
    #     id_mentora: int,
    #     session: Session,
    #     top_k: int | None = 5,
    #     min_score: int | None = 1,
    #     same_university: bool | None = False,
    # ) -> list["MentorSuggestion"]:
    #     """
    #     Retorna mentoradas compatíveis com uma mentora para que a mentora possa aceitar/solicitar mentorias.
    #     """
    #     mentor = session.get(Mentora, id_mentora)
    #     if not mentor:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Mentora não encontrada"
    #         )

    #     # Não sugere mentoradas para mentoras que já tenham um match ativo ou pendente
    #     mentor_active = session.exec(
    #         select(Mentoria).where(
    #             Mentoria.id_mentora == mentor.id_mentora,
    #             Mentoria.estado_mentoria == "ativa",
    #         )
    #     ).first()
    #     mentor_pending = session.exec(
    #         select(PedidosMentoria).where(
    #             PedidosMentoria.id_mentora == mentor.id_mentora,
    #             PedidosMentoria.estado_pedido == "pendente",
    #         )
    #     ).first()
    #     if mentor_active or mentor_pending:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Mentora já tem um match ativo ou pendente",
    #         )

    #     if same_university:
    #         statement = select(Mentorada).where(
    #             Mentorada.id_universidade_instituicao == mentor.id_universidade_instituicao,
    #             Mentorada.conta_ativa == True,
    #         )
    #     else:
    #         statement = select(Mentorada).where(
    #             Mentorada.conta_ativa == True,
    #         )
    #     possible_mentees = session.exec(statement).all()

    #     filtered : list[Mentorada] = []
    #     for m in possible_mentees:
    #         mentee_active = session.exec(
    #             select(Mentoria).where(
    #                 Mentoria.id_mentorada == m.id_mentorada,
    #                 Mentoria.estado_mentoria == "ativa",
    #             )
    #         ).first()
    #         mentee_pending = session.exec(
    #             select(PedidosMentoria).where(
    #                 PedidosMentoria.id_mentorada == m.id_mentorada,
    #                 PedidosMentoria.estado_pedido == "pendente",
    #             )
    #         ).first()
    #         if mentee_active or mentee_pending:
    #             continue
    #         filtered.append(m)

    #     if not filtered:
    #         return []

    #     # Sistema de pontuação
    #     scored: list[tuple[int, Mentorada, list[str], list[str]]] = []
    #     for m in filtered:
    #         score, shared_comp, shared_hob = MatchController._score_match(
    #             mentor.area_atuacao or "",
    #             mentor.hobbies or [],
    #             m.competencias_interesse or [],
    #             m.hobbies or [],
    #             m.curso or "",
    #         )
    #         scored.append((score, m, shared_comp, shared_hob))

    #     scored.sort(key=lambda x: x[0], reverse=True)

    #     min_score = min_score if min_score is not None else 1
    #     top_k = top_k if top_k is not None else 5
    #     selected = [(s, mm, sc, sh) for s, mm, sc, sh in scored if s >= min_score]
    #     if not selected and scored:
    #         selected = [scored[0]]
    #     selected = selected[:top_k]

    #     results: list[MentorSuggestion] = []
    #     for score, mm, shared_comp, shared_hob in selected:
    #         results.append(
    #             MentorSuggestion(
    #                 id_mentorada=str(mm.id_mentorada),
    #                 score=score,
    #                 objetivo_mentoria=mm.foco_mentoria,
    #                 curso_mentorada=mm.curso or "",
    #                 shared_competencias=shared_comp,
    #                 shared_hobbies=shared_hob,
    #             )
    #         )
    #     return results

    # @staticmethod
    # def mentor_create_request(
    #     id_mentora: int, id_mentorada: int, session: Session
    # ) -> PedidosMentoria:
    #     """Allow mentor to create a pending request to a mentee (accept suggestion)."""
    #     mentora = session.get(Mentora, id_mentora)
    #     mentorada = session.get(Mentorada, id_mentorada)
    #     if not mentora or not mentorada:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Mentora ou Mentorada não encontrada"
    #         )

    #     # Ensure neither has active/pending
    #     mentor_active = session.exec(
    #         select(Mentoria).where(
    #             Mentoria.id_mentora == mentora.id_mentora,
    #             Mentoria.estado_mentoria == "ativa",
    #         )
    #     ).first()
    #     mentor_pending = session.exec(
    #         select(PedidosMentoria).where(
    #             PedidosMentoria.id_mentora == mentora.id_mentora,
    #             PedidosMentoria.estado_pedido == "pendente",
    #         )
    #     ).first()
    #     mentee_active = session.exec(
    #         select(Mentoria).where(
    #             Mentoria.id_mentorada == mentorada.id_mentorada,
    #             Mentoria.estado_mentoria == "ativa",
    #         )
    #     ).first()
    #     mentee_pending = session.exec(
    #         select(PedidosMentoria).where(
    #             PedidosMentoria.id_mentorada == mentorada.id_mentorada,
    #             PedidosMentoria.estado_pedido == "pendente",
    #         )
    #     ).first()

    #     if mentor_active or mentor_pending or mentee_active or mentee_pending:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Mentor or mentored already has an active or pending mentorship",
    #         )

    #     pedido = PedidosMentoria(
    #         estado_pedido="pendente",
    #         data_pedido=datetime.now(),
    #         id_mentora=mentora.id_mentora,
    #         id_mentorada=mentorada.id_mentorada,
    #     )
    #     session.add(pedido)
    #     session.commit()
    #     session.refresh(pedido)
    #     return pedido

    @staticmethod
    def get_mentorship_request(
        id_pedidos_mentoria: int, session: Session
    ) -> PedidoMentoriaResponse:
        pedido = session.get(PedidosMentoria, id_pedidos_mentoria)
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado"
            )
        mentorada = session.get(Mentorada, pedido.id_mentorada)
        objetivo = mentorada.foco_mentoria if mentorada else ""
        return PedidoMentoriaResponse(
            id_pedidos_mentoria=str(pedido.id_pedidos_mentoria),
            estado_pedido=pedido.estado_pedido,
            data_pedido=pedido.data_pedido,
            id_mentora=str(pedido.id_mentora),
            id_mentorada=str(pedido.id_mentorada),
            objetivo_mentoria=objetivo,
        )

    @staticmethod
    def list_mentorship_requests(token: str, session: Session) -> list[MatchSugerido] | None:
        user = get_current_user(token, session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )
        user_type = get_tipo_usuario(user)
        if user_type == TipoUsuario.ADMIN:
            pedidos = list(session.exec(select(PedidosMentoria)\
                                        .where(
                                            PedidosMentoria.estado_pedido == "pendente"
                                        )).all())
            results: list[MatchSugerido] = []
            for pedido in pedidos:
                mentorada = session.get(Mentorada, pedido.id_mentorada)
                mentora = session.get(Mentora, pedido.id_mentora)
                if mentorada is None or mentora is None:
                    return []
                usuario_mentora = session.exec(select(Usuario).where(
                    Usuario.id_usuario == mentora.id_usuario
                )).one()
                usuario_mentorada = session.exec(select(Usuario).where(
                    Usuario.id_usuario == mentorada.id_usuario
                )).one()
                objetivo = mentorada.foco_mentoria if mentorada else ""
                results.append(
                    MatchSugerido(
                        id = pedido.id_pedidos_mentoria,
                        score = pedido.pontuacao,
                        motivo = "\n".join(pedido.motivo),
                        mentora = MatchSugerido.MentoraOptional(
                            nome = usuario_mentora.nome_completo,
                            cargo= mentora.cargo_atual,
                            skills= mentora.competencias,
                            foto = mentora.foto_perfil
                        ),
                        mentorada = MatchSugerido.MentoradaOptional(
                            nome = usuario_mentorada.nome_completo,
                            curso = mentorada.curso,
                            objetivo = mentorada.foco_mentoria,
                            foto = mentorada.foto_perfil
                        )
                    )
                )
            return results
        else:
            return None

    @staticmethod
    def update_mentorship_request(
            token: str, id_pedidos_mentoria: str, estado_pedido: str, session: Session
    ) -> PedidosMentoria | None:
        user = get_current_user(token, session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )
        user_type = get_tipo_usuario(user)
        if user_type == TipoUsuario.ADMIN:
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
                    ano_mentoria = datetime.now().year,
                    comeco_mentoria = datetime.now(),
                    fim_mentoria = None,
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
            token: str, id_pedidos_mentoria: int, session: Session
    ) -> dict:
        user = get_current_user(token, session)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
            )
        user_type = get_tipo_usuario(user)
        if user_type == TipoUsuario.ADMIN:
            pedido = session.get(PedidosMentoria, id_pedidos_mentoria)
            if not pedido:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Pedido não encontrado"
                )

            session.delete(pedido)
            session.commit()
            return {"message": "Pedido deletado com sucesso"}
        else:
            return {"message": "O usuário não é um administrador"}
