from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_users():
    return {"usuarios": []}

@router.post("/")
def create_user(data: dict):
    return {"status": "usuario criado", "data": data}
