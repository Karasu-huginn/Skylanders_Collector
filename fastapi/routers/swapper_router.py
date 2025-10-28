from fastapi import APIRouter, Depends, HTTPException
from models.swapper_model import Swapper
from base_models import SwapperBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/swappers", tags=["swappers"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_swapper():
    return {}