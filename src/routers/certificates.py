from fastapi import APIRouter
from src.controllers.certificate_controller import (
    CertificateController,
    CertificadoResponse,
    CertificadoCreate,
)
from src.database import SessionDep

router = APIRouter()


@router.get("/", response_model=list[CertificadoResponse])
def list_certificates(session: SessionDep):
    return CertificateController.list_certificates(session)


@router.get("/{id_certificado}", response_model=CertificadoResponse)
def get_certificate(id_certificado: int, session: SessionDep):
    return CertificateController.get_certificate(id_certificado, session)


@router.post("/", response_model=CertificadoResponse)
def create_certificate(data: CertificadoCreate, session: SessionDep):
    return CertificateController.create_certificate(data, session)


@router.delete("/{id_certificado}")
def delete_certificate(id_certificado: int, session: SessionDep):
    return CertificateController.delete_certificate(id_certificado, session)


@router.get("/mentorada/{id_mentorada}", response_model=list[CertificadoResponse])
def get_mentorada_certificates(id_mentorada: int, session: SessionDep):
    return CertificateController.get_mentorada_certificates(id_mentorada, session)
