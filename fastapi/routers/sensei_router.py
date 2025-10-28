from fastapi import APIRouter, Depends, HTTPException
from models.sensei_model import Sensei
from base_models import SenseiBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/senseis", tags=["senseis"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_sensei():
    return {}