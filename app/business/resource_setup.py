# app/business/resource_setup.py
from dataclasses import dataclass
from sqlmodel import Session, select
from app.db.database import engine
from app.models import User, Machine, Image

@dataclass
class Resources:
    system_user_email: str
    db_machine: Machine
    db_image: Image

def setup_resources():
    """Fetch or create default User, Machine, and Image.
       Returns a dictionary with the created/fetched objects.
    """
    with Session(engine) as session:
        # 1) Fetch or create a user
        stmt_user = select(User).where(User.email == "ashoka.shringla@revature.com")
        system_user = session.exec(stmt_user).first()
        if not system_user:
            system_user = User(
                first_name="Ashoka",
                last_name="Shringla",
                email="ashoka.shringla@revature.com",
                created_by="system",
                modified_by="system"
            )
            session.add(system_user)
            session.commit()
            session.refresh(system_user)
        
        # 2) Fetch or create default Machine
        stmt_machine = select(Machine).where(Machine.identifier == "default-machine")
        db_machine = session.exec(stmt_machine).first()
        if not db_machine:
            db_machine = Machine(
                name="t2.medium",
                identifier="t2.medium",
                cpu_count=2,
                memory_size=4096,
                storage_size=20,
                created_by="system",
                modified_by="system"
            )
            session.add(db_machine)
            session.commit()
            session.refresh(db_machine)
        
        # 3) Fetch or create default Image
        stmt_image = select(Image).where(Image.identifier == "ami-07f9ff58e9ab20148")
        db_image = session.exec(stmt_image).first()
        if not db_image:
            db_image = Image(
                name="sample-id-image",
                description="An AMI for testing",
                identifier="ami-07f9ff58e9ab20148",
                runner_pool_size=2,  # Example pool size
                machine_id=db_machine.id,
                created_by="system",
                modified_by="system"
            )
            session.add(db_image)
            session.commit()
            session.refresh(db_image)
        
        return Resources(
            system_user_email=system_user.email,
            db_machine=db_machine,
            db_image=db_image
        )