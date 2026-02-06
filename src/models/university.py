from pydantic import BaseModel
from sqlmodel import Session
from src.database import engine
from src.schemas.tables import UniversidadeInstituicao


class UniversityModel(BaseModel):
    nome_instituicao : str


class University:
    @classmethod
    def create_university(cls, universityModel : UniversityModel):
        session = Session(engine)
        try:
            university = UniversidadeInstituicao(
                nome_instituicao=universityModel.nome_instituicao
            )
            session.add(university)
            session.commit()
            session.close()
        except Exception as e:
            print(e)
            return (None, None)
        finally:
            session.close()
        return (None, None)
