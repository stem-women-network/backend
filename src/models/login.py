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
    data_nascimento : str
    linkedin : str | None

class CadastroMentorada(CadastroModel):
    genero: str
    etnia : str
    universidade_instituicao : str
    area_stem : str
    curso : str
    ano_curso : int
    semestre : int
    situacao_atual : str
    foco_mentoria : str
    idiomas : list[str]
    desenvolver_competencias : list[str]
    hobbies_interesses : list[str]
    disponibilidade : str

class CadastroMentora(CadastroModel):
    formacao : str
    cargo_atual : str
    areas_atuacao : list[str]
    como_ficou_sabendo : str
    
    
class Cadastro:
    @classmethod
    def fazer_cadastro_mentorada(cls, cadastro: CadastroMentorada):
        session = Session(engine)
        try:
            usuario = Usuario(
                nome_completo= cadastro.nome_completo,
                email=cadastro.email,
                senha=get_password_hash(cadastro.senha),
                cpf=cadastro.cpf,
                data_nascimento = date(
                    int(cadastro.data_nascimento.split("/")[2]),
                    int(cadastro.data_nascimento.split("/")[1]),
                    int(cadastro.data_nascimento.split("/")[0])
                )
            )
            session.add(usuario)
            mentorada = Mentorada(
                foto_perfil = None,
                linkedin = cadastro.linkedin if cadastro.linkedin is not None else None,
                genero = Genero(cadastro.genero.lower()),
                etnia = Etnia(cadastro.etnia.lower()),
                area_stem = cadastro.area_stem,
                curso = cadastro.curso,
                ano_curso = cadastro.ano_curso,
                semestre = cadastro.semestre,
                situacao_atual = cadastro.situacao_atual,
                foco_mentoria = cadastro.foco_mentoria,
                idiomas = cadastro.idiomas,
                competencias_interesse = cadastro.desenvolver_competencias,
                hobbies = cadastro.hobbies_interesses,
                disponibilidade = cadastro.disponibilidade,
                id_usuario = usuario.id_usuario,
                id_universidade_instituicao=None,
                termo_assinado = None
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
                cpf=cadastro.cpf,
                data_nascimento = date(
                    int(cadastro.data_nascimento.split("/")[2]),
                    int(cadastro.data_nascimento.split("/")[1]),
                    int(cadastro.data_nascimento.split("/")[0])
                )
            )
            session.add(usuario)
            mentora = Mentora(
                foto_perfil=None,
                cargo_atual=cadastro.cargo_atual,
                areas_atuacao=cadastro.areas_atuacao,
                linkedin=cadastro.linkedin,
                formacao=cadastro.formacao,
                id_usuario=usuario.id_usuario,
                id_universidade_instituicao=None,
                disponibilidade=None,
                como_ficou_sabendo=cadastro.como_ficou_sabendo.lower(),
                termo_assinado=None
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
            if verify_password(login.senha, usuario.senha):
                return (create_access_token(data={
                    "nome" : usuario.nome_completo,
                    "email" : usuario.email,
                }, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)),
                        {"nome_completo" : usuario.nome_completo,
                         "tipo_usuario" : get_tipo_usuario(usuario).value}
                        )
            session.close()
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

def get_current_user(token: str, session : Session):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("email")
    if email is None:
        return None
    user = session.exec(select(Usuario).where(Usuario.email == email)).one()
    if user is None:
        return None
    return user

def get_tipo_usuario(usuario : Usuario) -> TipoUsuario:
    if usuario.administradores is not None and len(usuario.administradores) > 0:
        return TipoUsuario.ADMIN
    if usuario.coordenadores is not None and len(usuario.coordenadores) > 0:
        return TipoUsuario.COORDENADOR
    if usuario.mentoras is not None and len(usuario.mentoras) > 0:
        return TipoUsuario.MENTORA
    if usuario.mentoradas is not None and len(usuario.mentoradas) > 0:
        return TipoUsuario.MENTORADA
    else:
        raise Exception("O usuário não foi cadastrado corretamente") 
