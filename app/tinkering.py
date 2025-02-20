import os
from dotenv import load_dotenv
from models import machine, image, runner, role, user_role, script, runner_history
from models.user import User, create_user, get_user
from sqlmodel import Field, Session, SQLModel, create_engine, select
from app.db.database import get_session




# user_update = User(first_name="newname")

# with next(get_session()) as session:
#     user_from_db = session.get(User, 1)
    
    






# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")
# engine = create_engine(DATABASE_URL, echo=True)

# print(next(get_session()))

# with next(get_session()) as session:
#     statement = select(User).where(User.id == 1)
#     user = session.exec(statement).first()
#     print(user)


# user_1 = User(first_name="asdasdas", last_name="asdasd", email="asdasd.asdasd@revature.com")

# create_user(user_1)

# print(get_session())

# with Session(engine) as session:
#     session.add(user_1)
#     session.commit()