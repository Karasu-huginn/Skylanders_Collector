from fastapi import APIRouter, Depends, HTTPException
from models.skylander_model import Skylander
from base_models import SkylanderBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/skylanders", tags=["skylanders"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_skylander():
    return {}