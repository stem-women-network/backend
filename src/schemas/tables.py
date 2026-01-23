from datetime import date, datetime
from pydantic import EmailStr
from sqlalchemy.orm import RelationshipDirection, declared_attr
from sqlalchemy.orm.relationships import _RelationshipDeclared
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, table
import uuid

class Usuario(SQLModel, table=True):
    id_usuario : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nome_completo : str = Field(max_length=100)
    cpf : str = Field(min_length=11,max_length=11)
    email : EmailStr = Field()
    senha : str = Field(min_length=60, max_length=60)
    data_nascimento : date = Field()

    administradores : list["Administrador"] = Relationship(back_populates="usuario")
    coordenadores : list["Coordenador"] = Relationship(back_populates="usuario")
    mentoradas : list["Mentorada"] = Relationship(back_populates="usuario")
    mentoras : list["Mentora"] = Relationship(back_populates="usuario")

    
class UniversidadeInstituicao(SQLModel, table=True):
    __tablename__ : str = "universidade_instituicao"
    id_universidade_instituicao : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nome_instituicao : str = Field(max_length=100)

    coordenadores : list["Coordenador"] = Relationship(back_populates="universidade_instituicao")
    mentoradas : list["Mentorada"] = Relationship(back_populates="universidade_instituicao")
    mentoras : list["Mentora"] = Relationship(back_populates="universidade_instituicao")

    
class Administrador(SQLModel, table=True):
    id_administrador : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    id_usuario : uuid.UUID = Field(foreign_key="usuario.id_usuario")
    
    usuario : Usuario = Relationship(back_populates="administradores")
    
    
class Coordenador(SQLModel, table=True):
    id_coordenador : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    id_usuario : uuid.UUID = Field(foreign_key="usuario.id_usuario")
    id_universidade_instituicao : uuid.UUID = Field(foreign_key="universidade_instituicao.id_universidade_instituicao")
    
    usuario : Usuario = Relationship(back_populates="coordenadores")
    universidade_instituicao : UniversidadeInstituicao = Relationship(back_populates="coordenadores")

    
class Mentorada(SQLModel, table=True):
    id_mentorada : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    linkedin : str | None = Field(max_length=100)
    curso_area_stem : str = Field(max_length=100)
    ano_curso : int = Field(max_digits=4)
    semestre : int = Field(max_digits=2)
    objetivo_mentoria : str = Field(max_length=200)
    disponibilidade : int | None = Field(max_digits=3)
    etnia : str = Field()
    genero : str = Field()
    expectativas : str = Field(max_length=300)
    
    conta_ativa : bool = Field(default = True)

    id_usuario : uuid.UUID = Field(foreign_key="usuario.id_usuario")
    id_universidade_instituicao : uuid.UUID | None = Field(foreign_key="universidade_instituicao.id_universidade_instituicao")
    
    usuario : Usuario = Relationship(back_populates="mentoradas")
    universidade_instituicao : UniversidadeInstituicao = Relationship(back_populates="mentoradas")
    
    pedidos : list["PedidosMentoria"] = Relationship(back_populates="mentorada")
    mentorias : list["Mentoria"] = Relationship(back_populates="mentorada")
    proximos_encontros : list["Mentoria"] = Relationship(back_populates="mentorada")
    certificados : list["Certificado"] = Relationship(back_populates="mentorada")
    encontros : list["Encontro"] = Relationship(back_populates="mentorada")
    

class Mentora(SQLModel, table=True):
    id_mentora : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    linkedin : str | None = Field(max_length=100)
    formacao : str = Field(max_length=100)
    cargo_atual : str = Field(max_length=100)
    areas_atuacao : int = Field(max_digits=9)
    disponibilidade : int | None = Field(max_digits=3)
    como_ficou_sabendo : str = Field()
    conta_ativa : bool = Field(default=True)

    id_usuario : uuid.UUID = Field(foreign_key="usuario.id_usuario")
    id_universidade_instituicao : uuid.UUID | None = Field(foreign_key="universidade_instituicao.id_universidade_instituicao")
    usuario : Usuario = Relationship(back_populates="mentoras")
    universidade_instituicao : UniversidadeInstituicao = Relationship(back_populates="mentoras")

    pedidos : list["PedidosMentoria"] = Relationship(back_populates="mentora")
    mentorias : list["Mentoria"] = Relationship(back_populates="mentora")
    proximos_encontros : list["ProximoEncontro"] = Relationship(back_populates="mentora")
    encontros : list["Encontro"] = Relationship(back_populates="mentora")
    

class PedidosMentoria(SQLModel, table=True):
    __tablename__ : str = "pedidos_mentoria"
    id_pedidos_mentoria : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    estado_pedido : str = Field(max_length=10)
    ano_pedido : int = Field(max_digits=4)
    
    id_mentora : uuid.UUID = Field(foreign_key="mentora.id_mentora")
    id_mentorada : uuid.UUID = Field(foreign_key="mentorada.id_mentorada")
    mentora : Mentora = Relationship(back_populates="pedidos")
    mentorada : Mentorada = Relationship(back_populates="pedidos")

    
class Mentoria(SQLModel, table=True):
    id_mentoria : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    estado_mentoria : str = Field(max_length=20)
    avaliacao_mentora : str | None = Field(max_length=500)
    avaliacao_mentorada : str | None = Field(max_length=500)
    nota_mentora : int | None = Field(max_digits=2)
    nota_mentorada : int | None = Field(max_digits=2)
    
    id_mentora : uuid.UUID = Field(foreign_key="mentora.id_mentora")
    id_mentorada : uuid.UUID = Field(foreign_key="mentorada.id_mentorada")
    
    mentora : Mentora = Relationship(back_populates="mentorias")
    mentorada : Mentorada = Relationship(back_populates="mentorias")

    
class ProximoEncontro(SQLModel, table=True):
    __tablename__ : str = "proximo_encontro"
    id_proximo_encontro :  uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    data_sugerida : datetime = Field()
    topico_sugerido : str = Field(max_length=100)
    
    id_mentora : uuid.UUID = Field(foreign_key="mentora.id_mentora")
    id_mentorada : uuid.UUID = Field(foreign_key="mentorada.id_mentorada")
    
    mentora : Mentora = Relationship(back_populates="proximos_encontros")
    mentorada : Mentorada = Relationship(back_populates="proximos_encontros")

    
class Encontro(SQLModel, table=True):
    id_encontro : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    data_encontro : datetime = Field()
    duracao_min : int = Field()
    tema : str = Field(max_length=100)
    topicos_discutidos : str = Field(max_length=300)
    progresso_mentorada : int = Field(gt=1, le=5)
    observacoes : str = Field(max_length=200)

    id_mentora : uuid.UUID = Field(foreign_key="mentora.id_mentora")
    id_mentorada : uuid.UUID = Field(foreign_key="mentorada.id_mentorada")
    
    mentora : Mentora = Relationship(back_populates="encontros")
    mentorada : Mentorada = Relationship(back_populates="encontros")

    
class Certificado(SQLModel, table=True):
    id_certificado : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ano_certificado : int = Field(max_digits=4)
    
    id_mentorada : uuid.UUID = Field(foreign_key="mentorada.id_mentorada")
    
    mentorada : Mentorada = Relationship(back_populates="certificados")
    
    
