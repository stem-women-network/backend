from fastapi import APIRouter, HTTPException, status
from sqlmodel import Session, select
from src.schemas.tables import Certificado, Mentorada
from src.database import SessionDep
from pydantic import BaseModel

router = APIRouter()

class CertificadoResponse(BaseModel):
    id_certificado: int
    ano_certificado: int
    id_mentorada: int

class CertificadoCreate(BaseModel):
    ano_certificado: int
    id_mentorada: int

@router.get("/", response_model=list[CertificadoResponse])
def list_certificates(session: SessionDep):
    """List all certificates"""
    certificados = session.exec(select(Certificado)).all()
    return certificados

@router.get("/{id_certificado}", response_model=CertificadoResponse)
def get_certificate(id_certificado: int, session: SessionDep):
    """Get a specific certificate by ID"""
    certificado = session.get(Certificado, id_certificado)
    if not certificado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    return certificado

@router.post("/", response_model=CertificadoResponse)
def create_certificate(data: CertificadoCreate, session: SessionDep):
    """Create a new certificate"""
    # Verify mentorada exists
    mentorada = session.get(Mentorada, data.id_mentorada)
    if not mentorada:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentorada not found")
    
    certificado = Certificado(**data.dict())
    session.add(certificado)
    session.commit()
    session.refresh(certificado)
    return certificado

@router.delete("/{id_certificado}")
def delete_certificate(id_certificado: int, session: SessionDep):
    """Delete a certificate"""
    certificado = session.get(Certificado, id_certificado)
    if not certificado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")
    
    session.delete(certificado)
    session.commit()
    return {"message": "Certificate deleted successfully"}

@router.get("/mentorada/{id_mentorada}")
def get_mentorada_certificates(id_mentorada: int, session: SessionDep):
    """Get all certificates for a specific mentorada"""
    statement = select(Certificado).where(Certificado.id_mentorada == id_mentorada)
    certificados = session.exec(statement).all()
    return certificados
