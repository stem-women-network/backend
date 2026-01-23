from typing import Annotated
import os
from dotenv import dotenv_values, load_dotenv
from fastapi import Depends
from sqlmodel import Session, create_engine
from schemas.tables import *

config = dotenv_values(".env")
DATABASE_URL = config["DATABASE_URL"]
assert DATABASE_URL != None

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

if __name__ == "__main__":
    create_db_and_tables()
