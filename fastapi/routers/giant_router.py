from fastapi import APIRouter, Depends, HTTPException
from models.giant_model import Giant
from base_models import GiantBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/giants", tags=["giants"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_giant():
    return {}