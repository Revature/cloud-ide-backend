# app/business/key_management.py

from datetime import date, datetime
from sqlmodel import Session, select
from app.db.database import engine
from app.models.key import Key
from app.business.aws import Create_New_Keypair
from app.business.encryption import encrypt_text

async def get_daily_key() -> Key:
    """
    Checks if a key already exists for today's date.
    If it exists, returns the key record.
    If not, generates a new key using Create_New_Keypair, encrypts the key material,
    saves it to the database, and returns the new key record.
    """
    today = date.today()
    with Session(engine) as session:
        stmt = select(Key).where(Key.key_date == today)
        key_record = session.exec(stmt).first()
        if key_record:
            return key_record

        # Generate a new keypair asynchronously using AWS.
        new_keypair = await Create_New_Keypair()
        if not isinstance(new_keypair, dict):
            raise Exception(f"Failed to create new key pair: {new_keypair}")

        # Encrypt the private key material using a master encryption key.
        # Assumes ENCRYPTION_KEY is set in the environment.
        encrypted_material = encrypt_text(new_keypair['PrimaryKey'], key_env="ENCRYPTION_KEY")

        key_record = Key(
            key_date=today,
            key_name="Keypair-" + datetime.datetime.now().strftime("%Y-%m-%d"),
            key_pair_id=new_keypair['KeyPairId'],
            encrypted_key=encrypted_material,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(key_record)
        session.commit()
        session.refresh(key_record)
        return key_record