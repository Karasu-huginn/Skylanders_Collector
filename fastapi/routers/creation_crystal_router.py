from fastapi import APIRouter, Depends, HTTPException
from models.creation_crystal_model import CreationCrystal
from base_models import CreationCrystalBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/creation_crystals", tags=["creation_crystals"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_creation_crystal():
    return {}