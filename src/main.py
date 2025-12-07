from fastapi import FastAPI
from routers import mentors, mentees, match, auth

app = FastAPI(title="STEM Women Backend")

app.include_router(mentors.router, prefix="/mentors", tags=["Mentores"])
app.include_router(mentees.router, prefix="/mentees", tags=["Mentoradas"])
app.include_router(match.router, prefix="/match", tags=["Match"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "STEM Women API rodando com sucesso!"}
