from fastapi import HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import Certificado, Mentorada
from pydantic import BaseModel


class CertificadoResponse(BaseModel):
    id_certificado: int
    ano_certificado: int
    id_mentorada: int


class CertificadoCreate(BaseModel):
    ano_certificado: int
    id_mentorada: int


class CertificateController:
    """Controller for certificate management"""

    @staticmethod
    def list_certificates(session: Session) -> list[Certificado]:
        """List all certificates"""
        certificados = session.exec(select(Certificado)).all()
        return certificados

    @staticmethod
    def get_certificate(id_certificado: int, session: Session) -> Certificado:
        """Get a specific certificate by ID"""
        certificado = session.get(Certificado, id_certificado)
        if not certificado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Certificado não encontrado"
            )
        return certificado

    @staticmethod
    def create_certificate(data: CertificadoCreate, session: Session) -> Certificado:
        """Create a new certificate"""
        mentorada = session.get(Mentorada, data.id_mentorada)
        if not mentorada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada não encontrada"
            )

        certificado = Certificado(**data.dict())
        session.add(certificado)
        session.commit()
        session.refresh(certificado)
        return certificado

    @staticmethod
    def delete_certificate(id_certificado: int, session: Session) -> dict:
        """Delete a certificate"""
        certificado = session.get(Certificado, id_certificado)
        if not certificado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Certificado não encontrado"
            )

        session.delete(certificado)
        session.commit()
        return {"message": "Certificado deletado com sucesso"}

    @staticmethod
    def get_mentorada_certificates(id_mentorada: int, session: Session) -> list[Certificado]:
        """Get all certificates for a specific mentorada"""
        statement = select(Certificado).where(Certificado.id_mentorada == id_mentorada)
        certificados = session.exec(statement).all()
        return certificados
