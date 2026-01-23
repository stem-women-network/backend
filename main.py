from fastapi import FastAPI
from src.routers import mentors, users, match, auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="STEM Women Backend")
app.add_middleware(CORSMiddleware,
                   allow_origins="*",
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )

app.include_router(mentors.router, prefix="/mentors", tags=["Mentores"])
app.include_router(match.router, prefix="/match", tags=["Match"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "STEM Women API rodando com sucesso!"}
