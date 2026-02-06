from datetime import date, datetime
from typing import Literal
from pydantic import EmailStr
from sqlmodel import ARRAY, Column, Field, Relationship, SQLModel, String, JSON
import uuid

class Usuario(SQLModel, table=True):
    id_usuario : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nome_completo : str = Field(max_length=100)
    cpf : str = Field(min_length=14,max_length=14)
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
    foto_perfil : bytes | None = Field()
    linkedin : str | None = Field(max_length=100)
    genero : str = Field()
    etnia : str = Field()
    area_stem : str = Field()
    curso : str = Field()
    ano_curso : int = Field(max_digits=4)
    semestre : int = Field(max_digits=2)
    situacao_atual : str = Field()
    foco_mentoria : str = Field()
    idiomas : list[str] = Field(sa_column=Column(ARRAY(String)))
    disponibilidade : str = Field()
    termo_assinado : bytes | None = Field()
    conta_ativa : bool = Field(default = False)

    # New fields for matching selections (list of strings)
    hobbies : list[str] | None = Field(sa_column=Column(ARRAY(String)))
    competencias_interesse : list[str] | None = Field(sa_column=Column(ARRAY(String)))

    id_usuario : uuid.UUID = Field(foreign_key="usuario.id_usuario")
    id_universidade_instituicao : uuid.UUID | None = Field(foreign_key="universidade_instituicao.id_universidade_instituicao")
    
    usuario : Usuario = Relationship(back_populates="mentoradas")
    universidade_instituicao : UniversidadeInstituicao = Relationship(back_populates="mentoradas")
    
    pedidos : list["PedidosMentoria"] = Relationship(back_populates="mentorada")
    mentorias : list["Mentoria"] = Relationship(back_populates="mentorada")
    certificados : list["Certificado"] = Relationship(back_populates="mentorada")
    

class Mentora(SQLModel, table=True):
    id_mentora : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    foto_perfil : bytes | None = Field()
    linkedin : str | None = Field(max_length=100)
    formacao : str = Field(max_length=100)
    cargo_atual : str = Field(max_length=100)
    area_atuacao : str = Field()
    cidade : str = Field()
    estado : str = Field()
    etnia : str = Field()
    genero : str = Field()
    foi_mentora : bool = Field()
    foi_mentorada : bool = Field()
    perfil_interesse : str = Field()
    foco_mentoria : list[str] = Field(sa_column=Column(ARRAY(String)))
    idiomas : list[str] = Field(sa_column=Column(ARRAY(String)))
    competencias : list[str] = Field(sa_column=Column(ARRAY(String)))
    ajuda : str = Field()
    bio : str | None = Field()
    termo_assinado : bytes | None = Field()
    conta_ativa : bool = Field(default=False)
    disponibilidade : str = Field()

    # New hobby field to match with mentees
    hobbies : list[str] | None = Field(sa_column=Column(ARRAY(String)))
    
    id_usuario : uuid.UUID = Field(foreign_key="usuario.id_usuario")
    id_universidade_instituicao : uuid.UUID | None = Field(foreign_key="universidade_instituicao.id_universidade_instituicao")
    usuario : Usuario = Relationship(back_populates="mentoras")
    universidade_instituicao : UniversidadeInstituicao = Relationship(back_populates="mentoras")

    pedidos : list["PedidosMentoria"] = Relationship(back_populates="mentora")
    mentorias : list["Mentoria"] = Relationship(back_populates="mentora")

class PedidosMentoria(SQLModel, table=True):
    id_pedidos_mentoria : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    estado_pedido : str = Field(max_length=10)
    data_pedido : datetime = Field(default_factory=datetime.now)
    
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
    progresso_mentorada : int = Field(default=0)
    ano_mentoria : int = Field()
    
    comeco_mentoria : date = Field()
    fim_mentoria : date | None = Field()
    
    id_mentora : uuid.UUID = Field(foreign_key="mentora.id_mentora")
    id_mentorada : uuid.UUID = Field(foreign_key="mentorada.id_mentorada")
    
    mentora : Mentora = Relationship(back_populates="mentorias")
    mentorada : Mentorada = Relationship(back_populates="mentorias")
    encontros : list["Encontro"] = Relationship(back_populates="mentoria")
    proximos_encontros : list["ProximoEncontro"] = Relationship(back_populates="mentoria")
    materiais : list["MaterialMentoria"] = Relationship(back_populates="mentoria")
    mensagens : list["MensagemMentoria"] = Relationship(back_populates="mentoria")
    
class ProximoEncontro(SQLModel, table=True):
    id_proximo_encontro :  uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    data_sugerida : datetime = Field()
    topico_sugerido : str = Field(max_length=100)
    
    id_mentoria : uuid.UUID = Field(foreign_key="mentoria.id_mentoria")
    mentoria : Mentoria = Relationship(back_populates="proximos_encontros")
    
class Encontro(SQLModel, table=True):
    id_encontro : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    data_encontro : datetime = Field()
    duracao_min : int = Field()
    tema : str = Field(max_length=100)
    topicos_discutidos : str = Field(max_length=300)
    progresso_mentorada : int = Field(gt=1, le=5)
    observacoes : str = Field(max_length=200)
    
    id_mentoria : uuid.UUID = Field(foreign_key="mentoria.id_mentoria")
    mentoria : Mentoria = Relationship(back_populates="encontros")

    
class Certificado(SQLModel, table=True):
    id_certificado : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ano_certificado : int = Field(max_digits=4)
    
    id_mentorada : uuid.UUID = Field(foreign_key="mentorada.id_mentorada")
    
    mentorada : Mentorada = Relationship(back_populates="certificados")
    
class MaterialMentoria(SQLModel, table=True):
    __tablename__ : str = "material_mentoria"
    id_arquivo_mentoria : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tipo_material : str = Field()
    titulo_material : str = Field()
    arquivo : bytes = Field()
    id_mentoria : uuid.UUID = Field(foreign_key="mentoria.id_mentoria")
    mentoria : Mentoria = Relationship(back_populates="materiais")

class ArquivoTreinamento(SQLModel, table=True):
    __tablename__ : str = "arquivo_treinamento"
    id_arquivo_treinamento : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    categoria: str = Field()
    titulo_arquivo : str = Field()
    arquivo : bytes = Field()
    
class MensagemMentoria(SQLModel, table=True):
    __tablename__ : str = "mensagem_mentoria" 
    id_mensagem : uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    mensagens : list[dict[Literal["actor","datetime","message"],str]] = Field(sa_column=Column(ARRAY(JSON)))
    id_mentoria : uuid.UUID = Field(foreign_key="mentoria.id_mentoria")
    mentoria : Mentoria = Relationship(back_populates="mensagens")    
