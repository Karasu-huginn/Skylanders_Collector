from fastapi import APIRouter, Depends, HTTPException
from models.level_model import Level
from base_models import LevelBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/levels", tags=["levels"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_level():
    return {}