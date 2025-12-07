from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_mentors():
    return {"mentores": []}

@router.post("/")
def create_mentor(data: dict):
    return {"status": "mentor criado", "data": data}
