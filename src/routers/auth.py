from fastapi import APIRouter, HTTPException, Response
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_405_METHOD_NOT_ALLOWED, HTTP_409_CONFLICT

from src.models.login import Cadastro, CadastroMentora, CadastroMentorada, CadastroModel, Login, LoginModel

router = APIRouter()

@router.post("/login")
def login(credentials: LoginModel, response : Response):
    token, user = Login.fazer_login(credentials)
    if token is not None and user is not None:
        response.status_code = HTTP_200_OK
        return {
            "token" : token,
            "user" : {
                "nome_completo" : user["nome_completo"],
                "tipo_usuario" : user["tipo_usuario"]
            }
        }
    else:
        response.status_code = HTTP_401_UNAUTHORIZED
        return HTTPException(status_code=HTTP_401_UNAUTHORIZED)

@router.post("/signup-mentee")
def signup_mentorar(credentials: CadastroMentora, response:Response):
    signup = Cadastro.fazer_cadastro_mentora(credentials)
    if signup is None:
        response.status_code = HTTP_409_CONFLICT
        return HTTPException(status_code=HTTP_409_CONFLICT,detail="Houve um erro ao fazer o cadastro")
    return {"message" : "Cadastro feito com sucesso"}

@router.post("/signup-mentor")
def signup_mentorada(credentials: CadastroMentorada, response:Response):
    signup = Cadastro.fazer_cadastro_mentorada(credentials)
    if signup is None:
        response.status_code = HTTP_409_CONFLICT
        return HTTPException(status_code=HTTP_409_CONFLICT,detail="Houve um erro ao fazer o cadastro")
    return {"message" : "Cadastro feito com sucesso"}
