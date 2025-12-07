from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def create_match():
    return {"status": "matching gerado"}
