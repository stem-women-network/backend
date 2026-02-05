from fastapi import APIRouter
from src.controllers.auth_controller import AuthController
from src.models.login import LoginModel, CadastroMentora, CadastroMentorada

router = APIRouter()


@router.post("/login")
def login(credentials: LoginModel):
    return AuthController.login(credentials)


@router.post("/signup-mentor")
def signup_mentora(credentials: CadastroMentora):
    return AuthController.signup_mentor(credentials)


@router.post("/signup-mentee")
def signup_mentorada(credentials: CadastroMentorada):
    return AuthController.signup_mentee(credentials)
