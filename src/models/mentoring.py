import enum
from typing import Sequence

from sqlmodel import select, Session

from src.models.login import TipoUsuario, get_current_user, get_tipo_usuario
from src.schemas.tables import MensagemMentoria, Mentora, Mentorada, Mentoria, Usuario
from src.database import engine

class MentoringStatus(enum.StrEnum):
    ATIVA = enum.auto()
    CONCLUIDA = enum.auto()
    CANCELADA = enum.auto()

class MentoringModel:
    @classmethod
    def get_messages(cls, token : str, otherId : str) -> Sequence[any] | None:
        messages = None
        session = Session(engine)
        try:
            user = get_current_user(token, session)
            if user is None:
                return None
            user_type = get_tipo_usuario(user)
            condition = False
            if(user_type == TipoUsuario.MENTORA):
                mentor = user.mentoras[0]
                mentor_id = mentor.id_mentora
                mentee_id = otherId
                
            elif user_type == TipoUsuario.MENTORADA:
                mentee = user.mentoradas[0]
                mentor_id = otherId
                mentee_id = mentee.id_mentorada
            else:
                return None
            statement = select(Mentoria)\
                .where(Mentoria.id_mentora == mentor_id) \
                .where(Mentoria.id_mentorada == mentee_id)
            mentoring = session.exec(statement).one_or_none()
            if mentoring is None:
                return None
            statement = select(MensagemMentoria.mensagens)\
                .where(MensagemMentoria.id_mentoria == mentoring.id_mentoria)
            messages = session.exec(statement).all()
            if messages is None:
                return None
            session.close()
            return messages[0]
        except Exception as e:
            print(e)
            return None
