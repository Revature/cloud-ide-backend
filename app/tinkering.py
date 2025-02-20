import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True)