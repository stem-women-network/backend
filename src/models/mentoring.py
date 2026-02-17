import enum
from typing import Sequence

from sqlmodel import select, Session, func

from src.models.login import TipoUsuario, get_current_user, get_tipo_usuario
from src.schemas.tables import MaterialMentoria, MensagemMentoria, Mentora, Mentorada, Mentoria
from src.database import engine
import base64

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

    @classmethod
    def send_file(cls, file : bytes, title: str, file_type : str, token: str, mentee_id: str):
        session = Session(engine)
        try:
            user = get_current_user(token, session)
            if user is None:
                return None
            mentor = user.mentoras[0]
            mentoring_id = session.exec(
                select(Mentoria.id_mentoria)\
                .where(Mentoria.id_mentora==mentor.id_mentora)\
                .where(Mentoria.id_mentorada==mentee_id)
            ).one()
            material = MaterialMentoria(
                id_mentoria= mentoring_id,
                tipo_material= file_type,
                titulo_material= title,
                arquivo=file
            )
            session.add(material)
            session.commit()
        except Exception as e:
            print(e)
        finally:
            session.close()

    @classmethod
    def get_files(cls, token: str, mentee_id: str):
        session = Session(engine)
        try:
            user = get_current_user(token, session)
            if user is None:
                return None
            mentor = user.mentoras[0]
            mentoring_id = session.exec(
                select(Mentoria.id_mentoria)\
                .where(Mentoria.id_mentora==mentor.id_mentora)\
                .where(Mentoria.id_mentorada==mentee_id)
            ).one_or_none()
            if mentoring_id is None:
                return None
            files = session.exec(
                select(
                       MaterialMentoria.id_arquivo_mentoria,
                       MaterialMentoria.titulo_material,
                       MaterialMentoria.tipo_material,
                       func.length(MaterialMentoria.arquivo),
                       )\
                .where(MaterialMentoria.id_mentoria == mentoring_id)
            ).all()
            return files
        except Exception as e:
            print(e)
        finally:
            session.close()

    @classmethod
    def download_file(cls, token: str, file_id: str) -> tuple[bytes | None, str | None]:
        session = Session(engine)
        try:
            user = get_current_user(token, session)
            if user is None:
                return None, None
            user_type = get_tipo_usuario(user)
            result = ""
            if user_type == TipoUsuario.MENTORA:
                mentor = user.mentoras[0]
                result = session.exec(
                    select(
                        MaterialMentoria.arquivo,
                        MaterialMentoria.tipo_material
                    )\
                    .where(
                        MaterialMentoria.id_arquivo_mentoria == file_id
                    )\
                    .join(Mentoria)\
                    .join(Mentora)\
                    .where(
                        Mentora.id_mentora == mentor.id_mentora
                    )
                ).one_or_none()
            elif user_type == TipoUsuario.MENTORADA:
                mentee = user.mentoradas[0]
                result = session.exec(
                    select(
                        MaterialMentoria.arquivo,
                        MaterialMentoria.tipo_material
                    )\
                    .where(
                        MaterialMentoria.id_arquivo_mentoria == file_id
                    )\
                    .join(Mentoria)\
                    .join(Mentorada)\
                    .where(
                        Mentorada.id_mentorada == mentee.id_mentorada
                    )
                ).one_or_none()
            if result is None or result == '':
                return (None, None)
            return result
        except Exception as e:
            print(e)
        finally:
            session.close()
        return None, None

    @classmethod
    def delete_file(cls,token: str, file_id: str):
        session = Session(engine)
        try:
            user = get_current_user(token, session)
            if user is None:
                return None
            user_type = get_tipo_usuario(user)
            result = ""
            if user_type == TipoUsuario.MENTORA:
                mentor = user.mentoras[0]
                result = session.exec(
                    select(
                        MaterialMentoria
                    )\
                    .where(
                        MaterialMentoria.id_arquivo_mentoria == file_id
                    )\
                    .join(Mentoria)\
                    .join(Mentora)\
                    .where(
                        Mentora.id_mentora == mentor.id_mentora
                    )
                ).one_or_none()
                if result is None:
                    return None
                session.delete(result)
                session.commit()
            session.close()
            return None
        except Exception as e:
            print(e)
        finally:
            session.close()
