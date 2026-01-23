import enum
from typing import Literal, Optional, Tuple
from pydantic import BaseModel
from sqlmodel import Date, Session, select
import bcrypt
import jwt
from datetime import date, timedelta, timezone, datetime
import dotenv
import os

from src.database import engine
from src.schemas.tables import Mentora, Mentorada, Usuario

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 14 # 14 days

class TipoUsuario(enum.StrEnum):
    ADMIN       = enum.auto()
    COORDENADOR = enum.auto()
    MENTORA     = enum.auto()
    MENTORADA   = enum.auto()

class ComoFicouSabendo(enum.StrEnum):
    INSTAGRAM  = enum.auto()
    AMIGOS     = enum.auto()
    PROFESSORA = enum.auto()
    EVENTO     = enum.auto()
    LINKEDIN   = enum.auto()
    OUTROS     = enum.auto()

class Genero(enum.StrEnum):
    FEMININO          = enum.auto()
    MASCULINO         = enum.auto()
    NAO_BINARIO       = enum.auto()
    PREFIRO_NAO_DIZER = enum.auto()
    OUTRO             = enum.auto()

class Etnia(enum.StrEnum):
    AMARELA           = enum.auto()
    BRANCA            = enum.auto()
    INDIGENA          = enum.auto()
    PARDA             = enum.auto()
    PRETA             = enum.auto()
    PREFIRO_NAO_DIZER = enum.auto()
    
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginModel(BaseModel):
    email : str
    senha : str

class CadastroModel(BaseModel):
    email : str
    senha: str
    nome_completo : str
    cpf : str
    celular : str
    data_nascimento : Date
    linkedin : str | None

class CadastroMentorada(CadastroModel):
    curso : str
    ano_curso : int
    semestre : int
    genero: Genero
    etnia : Etnia
    expectativas : str
    compartilhar_experiencias : str
    desenvolver_competencias : str
    foi_mentorada : bool
    hobbies_interesses : str
    comentarios: str

class CadastroMentora(CadastroModel):
    formacao : str
    cargo_atual : str
    areas_atuacao : str
    como_ficou_sabendo : ComoFicouSabendo
    
    
class Cadastro:
    @classmethod
    def fazer_cadastro_mentorada(cls, cadastro: CadastroMentorada):
        session = Session(engine)
        try:
            usuario = Usuario(
                nome_completo= cadastro.nome_completo,
                email=cadastro.email,
                senha=get_password_hash(cadastro.senha),
                cpf=cadastro.cpf
            )
            session.add(usuario)
            mentorada = Mentorada(
                id_usuario = usuario.id_usuario,
                ano_curso = cadastro.ano_curso,
                semestre = cadastro.semestre,
                curso_area_stem = cadastro.curso,
                disponibilidade = None,
                objetivo_mentoria = cadastro.desenvolver_competencias,
                expectativas=cadastro.expectativas,
                genero = cadastro.genero,
                etnia = cadastro.etnia,
                linkedin = None,
                id_universidade_instituicao=None,
            )
            session.add(mentorada)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(e)
            return None
        finally:
            session.close()
            
    @classmethod
    def fazer_cadastro_mentora(cls, cadastro: CadastroMentora):
        session = Session(engine)
        try:
            usuario = Usuario(
                nome_completo=cadastro.nome_completo,
                email=cadastro.email,
                senha=get_password_hash(cadastro.senha),
                cpf=cadastro.cpf
            )
            session.add(usuario)
            mentora = Mentora(
                cargo_atual=cadastro.cargo_atual,
                areas_atuacao=int(cadastro.areas_atuacao),
                linkedin=cadastro.linkedin,
                formacao=cadastro.formacao,
                id_usuario=usuario.id_usuario,
                id_universidade_instituicao=None,
                disponibilidade=None,
                como_ficou_sabendo=cadastro.como_ficou_sabendo
            )
            session.add(mentora)
            session.commit()
            session.close()
            return True
        except Exception as e:
            print(e)
            return None
        finally:
            session.close()
        
class Login:
    @classmethod
    def fazer_login(cls, login : LoginModel) -> Tuple[str | None, dict[str, str] | None]:
        session = Session(engine)
        try:
            statement = select(Usuario).where(Usuario.email == login.email)
            usuario = session.exec(statement).one()
            session.close()
            if verify_password(login.senha, usuario.senha):
                return (create_access_token(data={
                    "nome" : usuario.nome_completo,
                    "email" : usuario.email,
                }, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)),
                        {"nome_completo" : usuario.nome_completo,
                         "tipo_usuario" : get_tipo_usuario(usuario).value}
                        )
        except Exception as e:
            print(e)
            return (None, None)
        finally:
            session.close()
        return (None, None)


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )

def get_password_hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str):
    session = Session(engine)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("email")
    if email is None:
        return None
    user = session.exec(select(Usuario).where(Usuario.email == email)).one()
    session.close()
    if user is None:
        return None
    return user

def get_tipo_usuario(usuario : Usuario) -> TipoUsuario:
    if len(usuario.administradores) > 0:
        return TipoUsuario.ADMIN
    if len(usuario.coordenadores) > 0:
        return TipoUsuario.COORDENADOR
    if len(usuario.mentoras) > 0:
        return TipoUsuario.MENTORA
    if len(usuario.mentoradas) > 0:
        return TipoUsuario.MENTORADA
    else:
        raise Exception("O usuário não foi cadastrado corretamente") 
