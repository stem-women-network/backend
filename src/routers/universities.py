from fastapi import APIRouter, HTTPException, Response
from starlette.status import HTTP_409_CONFLICT

from src.models.university import University, UniversityModel

router = APIRouter()

@router.post("/")
def create_university(university : UniversityModel, response : Response):
    data = University.create_university(university)
    if data == None:
        response.status_code = HTTP_409_CONFLICT
        return HTTPException(status_code=HTTP_409_CONFLICT, detail="Houve um erro ao registrar a instituição")
    return {"message" : "A instituição foi cadastrada com sucesso"}
