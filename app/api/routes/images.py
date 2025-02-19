from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.image import Image

router = APIRouter()

@router.post("/", response_model=Image, status_code=status.HTTP_201_CREATED)
def create_image(image: Image, session: Session = Depends(get_session)):
    """
    Create a new Image record.
    """
    session.add(image)
    session.commit()
    session.refresh(image)
    return image

@router.get("/", response_model=List[Image])
def read_images(session: Session = Depends(get_session)):
    """
    Retrieve a list of all Images.
    """
    images = session.exec(select(Image)).all()
    return images

@router.get("/{image_id}", response_model=Image)
def read_image(image_id: int, session: Session = Depends(get_session)):
    """
    Retrieve a single Image by ID.
    """
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.put("/{image_id}", response_model=Image)
def update_image(image_id: int, updated_image: Image, session: Session = Depends(get_session)):
    """
    Update an existing Image record.
    """
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Update fields; typically, you might want to limit which fields can be updated.
    image.name = updated_image.name
    image.description = updated_image.description
    image.identifier = updated_image.identifier
    image.modified_by = updated_image.modified_by
    # Optionally, you might update the modified_on automatically in your model's onupdate configuration.
    
    session.add(image)
    session.commit()
    session.refresh(image)
    return image

@router.delete("/{image_id}", status_code=status.HTTP_200)
def delete_image(image_id: int, session: Session = Depends(get_session)):
    """
    Delete an Image record.
    """
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    session.delete(image)
    session.commit()
    return None