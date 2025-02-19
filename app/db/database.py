import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

# Define your DATABASE_URL. For MySQL (Aurora), you might use:
# "mysql+pymysql://user:password@aurora-endpoint:3306/dbname"
# For local testing, you can use SQLite:
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    # Import all models so that they are registered with SQLModel metadata
    from app.models import user, machine, image, runner
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session