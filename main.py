from fastapi import FastAPI
from src.routers import (
    mentors,
    users,
    match,
    auth,
    certificates,
    universities,
    mentoradas,
    mentoring,
    meetings,
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="STEM Women Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mentors.router, prefix="/mentors", tags=["Mentores"])
app.include_router(users.router, prefix="/users", tags=["Usuários"])
app.include_router(match.router, prefix="/match", tags=["Match"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(certificates.router, prefix="/certificates", tags=["Certificados"])
app.include_router(
    universities.router, prefix="/universities", tags=["Universidades"]
)
app.include_router(mentoradas.router, prefix="/mentoradas", tags=["Mentoradas"])
app.include_router(mentoring.router, prefix="/mentoring", tags=["Mentoring"])
app.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])

@app.get("/")
def root():
    return {"message": "STEM Women API rodando com sucesso!"}
