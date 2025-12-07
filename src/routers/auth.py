from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
def login(credentials: dict):
    return {"token": "fake-jwt-token"}
