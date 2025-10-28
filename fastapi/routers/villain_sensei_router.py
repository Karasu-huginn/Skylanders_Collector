from fastapi import APIRouter, Depends, HTTPException
from models.villain_sensei_model import VillainSensei
from base_models import VillainSenseiBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/villain_senseis", tags=["villain_senseis"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_villain_sensei():
    return {}