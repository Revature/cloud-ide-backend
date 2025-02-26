# app/business/key_management.py
from datetime import date, datetime
from sqlmodel import Session, select
from app.db.database import engine
from app.models.key import Key
from app.business.aws import Create_New_Keypair
from app.business.encryption import encrypt_text, decrypt_text

async def get_daily_key() -> Key:
    """
    Checks if a key already exists for today's date.
    If it exists, returns the key record.
    If not, generates a new keypair via AWS, encrypts the private key material,
    saves the key record to the database, and returns it.
    """
    today = date.today()
    
    # Check if today's key exists in the database.
    with Session(engine) as session:
        stmt = select(Key).where(Key.key_date == today)
        key_record = session.exec(stmt).first()
        if key_record:
            return key_record

    # Define the key name (e.g., "Keypair-YYYY-MM-DD")
    key_name = f"Keypair-{today.strftime('%Y-%m-%d')}-testing-key"
    
    try:
        # Attempt to create a new keypair with the key_name.
        new_keypair = await Create_New_Keypair(KeyName=key_name)
    except Exception as e:
        # If the error indicates a duplicate, re-check the database.
        if "Duplicate" in str(e):
            with Session(engine) as session:
                stmt = select(Key).where(Key.key_date == today)
                key_record = session.exec(stmt).first()
                if key_record:
                    return key_record
            raise Exception(f"Key pair already exists in AWS but no record found in DB: {e}")
        else:
            raise Exception(f"Failed to create new key pair: {e}")

    if not isinstance(new_keypair, dict):
        raise Exception(f"Failed to create new key pair: {new_keypair}")

    # Encrypt the private key material using a master encryption key.
    encrypted_material = encrypt_text(new_keypair['PrimaryKey'])

    # Save the new key record to the database.
    with Session(engine) as session:
        key_record = Key(
            key_date=today,
            key_pair_id=new_keypair['KeyPairId'],
            key_name=key_name,
            encrypted_key=encrypted_material,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(key_record)
        session.commit()
        session.refresh(key_record)
        return key_record