from typing import Literal
from uuid import UUID
from sqlmodel import Session, desc, select
from src.database import engine
from src.models.login import get_current_user
from src.schemas.tables import Mentora, Mentoria 


class MentorModel:
    @classmethod
    def get_current_mentee_info(cls, token : str) -> dict[Literal["name","course","semester","progress", "status", "id"],str | int | UUID] | None:
        session = Session(engine)
        user = get_current_user(token, session)
        try:
            if user is None:
                return None
            statement = select(Mentora).where(Mentora.id_usuario == user.id_usuario)
            mentor = session.exec(statement).one_or_none()
            if mentor is None:
                return None

            statement = select(Mentoria)\
                .where(Mentoria.mentora == mentor)\
                .order_by(desc(Mentoria.comeco_mentoria))\
                .limit(1)
            
            mentoring = session.exec(statement).one_or_none()
            if mentoring is None:
                return None

            mentee = mentoring.mentorada
            id_mentee = mentee.id_mentorada
            mentee_user = mentee.usuario
            response : dict[Literal["name","course","semester","progress", "status", "id"],str | int | UUID] = {
                "id" : id_mentee,
                "name" : mentee_user.nome_completo,
                "course" : mentee.curso,
                "semester" : mentee.semestre,
                "progress" : mentoring.progresso_mentorada,
                "status" : mentoring.estado_mentoria
            }
            session.close()
            return response
        except Exception as e:
            print(e)
            session.close()
            return None
        
    @classmethod
    def get_all_mentee_info(cls, token : str) -> list[dict[Literal["name", "course", "status", "period", "meetings", "id"], str | int | UUID]] | None:
        session = Session(engine)
        user = get_current_user(token, session)
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
            
            mentees : list[dict[Literal["name", "course", "status", "period", "meetings","id"], str | int | UUID]] = []
            for mentoring in mentorings:
                mentee = mentoring.mentorada
                id_mentee = mentee.id_mentorada
                name = mentee.usuario.nome_completo
                course = mentee.curso
                status = mentoring.estado_mentoria
                count_meetings = len(mentoring.encontros)
                
                start = mentoring.comeco_mentoria
                end = mentoring.fim_mentoria
                
                if end is None:
                    end = "Presente"
                else:
                    end = end.strftime("%b %Y")
                mentees.append({
                    "id" : id_mentee,
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
