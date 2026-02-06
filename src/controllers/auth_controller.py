from fastapi import HTTPException, status
from pydantic import BaseModel
from src.models.login import Login, LoginModel, Cadastro, CadastroMentora, CadastroMentorada


class LoginResponse(BaseModel):
    token: str
    user: dict


class SignupResponse(BaseModel):
    message: str


class AuthController:
    @staticmethod
    def login(credentials: LoginModel) -> dict:
        token, user = Login.fazer_login(credentials)
        if token is not None and user is not None:
            return {
                "token": token,
                "user": {
                    "nome_completo": user["nome_completo"],
                    "tipo_usuario": user["tipo_usuario"],
                },
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas"
            )

    @staticmethod
    def signup_mentor(credentials: CadastroMentora) -> dict:
        signup = Cadastro.fazer_cadastro_mentora(credentials)
        if signup is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Erro ao registrar mentora",
            )
        return {"message": "Mentora registrada com sucesso"}

    @staticmethod
    def signup_mentee(credentials: CadastroMentorada) -> dict:
        signup = Cadastro.fazer_cadastro_mentorada(credentials)
        if signup is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Erro ao registrar mentorada",
            )
        return {"message": "Mentorada registrada com sucesso"}
