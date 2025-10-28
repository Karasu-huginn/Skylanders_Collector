from fastapi import APIRouter, Depends, HTTPException
from models.edition_model import Editions
from base_models import EditionBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/editions", tags=["editions"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_edition():
    return {}