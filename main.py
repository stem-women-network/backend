from fastapi import FastAPI
from src.routers import mentors, users, match, auth, universities, mentoring
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="STEM Women Backend")
app.add_middleware(CORSMiddleware,
                   allow_origins="*",
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )

app.include_router(mentors.router, prefix="/mentors", tags=["Mentors"])
app.include_router(match.router, prefix="/match", tags=["Match"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(universities.router, prefix="/university", tags=["University"])
app.include_router(mentoring.router, prefix="/mentoring", tags=["Mentoring"])

@app.get("/")
def root():
    return {"message": "STEM Women API rodando com sucesso!"}
