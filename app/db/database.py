import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

# Define your DATABASE_URL. For MySQL (Aurora), you might use:
# "mysql+pymysql://user:password@aurora-endpoint:3306/dbname"
# For local testing, you can use SQLite:
DATABASE_URL = os.getenv("DATABASE_URL")

print(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    # Import all models so that they are registered with SQLModel metadata
    from app.models import user, machine, image, runner, role, user_role, script, runner_history
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    role.populate_roles()


    
def get_session():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        yield session