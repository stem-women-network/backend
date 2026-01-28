from typing import Literal
from sqlmodel import Session, desc, select
from src.database import engine
from src.models.login import TipoUsuario, get_current_user, get_tipo_usuario
from src.schemas.tables import Mentora, Mentorada, Mentoria 


class MentorModel:
    @classmethod
    def get_current_mentee_info(cls, token : str) -> dict[Literal["name","course","semester","progress"],str | int] | None:
        user = get_current_user(token)
        session = Session(engine)
        try:
            if user is None:
                return None
            statement = select(Mentora).where(Mentora.id_usuario == user.id_usuario)
            mentor = session.exec(statement).one_or_none()
            if mentor is None:
                return None

            statement = select(Mentoria)\
                .where(Mentoria.mentora == mentor)\
                .order_by(desc(Mentoria.ano_mentoria))\

            mentoring = session.exec(statement).one_or_none()
            if mentoring is None:
                return None

            mentee = mentoring.mentorada
            mentee_user = mentee.usuario
            response : dict[Literal["name","course","semester","progress"],str | int] = {
                "name" : mentee_user.nome_completo,
                "course" : mentee.curso_area_stem,
                "semester" : mentee.semestre,
                "progress" : mentoring.progresso_mentorada
            }
            session.close()
            return response
        except Exception as e:
            print(e)
            session.close()
            return None
        
    @classmethod
    def get_all_mentee_info(cls, token : str) -> list[dict[Literal["name", "course", "status", "period", "meetings"], str | int]] | None:
        user = get_current_user(token)
        session = Session(engine)
        try:
            if user is None:
                return None
            statement = select(Mentora).where(Mentora.id_usuario == user.id_usuario)
            mentor = session.exec(statement).one_or_none()
            if mentor is None:
                return None

            statement = select(Mentoria)\
                .where(Mentoria.mentora == mentor)\
                .order_by(desc(Mentoria.ano_mentoria))\

            mentorings = session.exec(statement).all()
            if mentorings is None:
                return None
            
            mentees : list[dict[Literal["name", "course", "status", "period", "meetings"], str | int]] = []
            for mentoring in mentorings:
                mentee = mentoring.mentorada
                name = mentee.usuario.nome_completo
                course = mentee.curso_area_stem
                status = mentoring.estado_mentoria
                count_meetings = len(mentoring.encontros)
                
                start = mentoring.comeco_mentoria
                end = mentoring.fim_mentoria
                
                if end is None:
                    end = "Presente"
                else:
                    end = end.strftime("%b %Y")
                mentees.append({
                    "name" : name,
                    "course" : course,
                    "status" : status,
                    "period" : f'{start.strftime("%b %Y")} - {end}',
                    "meetings" : count_meetings
                })
            session.close()
            return mentees
        except Exception as e:
            print(e)
            session.close()
            return None
