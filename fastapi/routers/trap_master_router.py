from fastapi import APIRouter, Depends, HTTPException
from models.trap_master_model import TrapMaster
from base_models import TrapMasterBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/trap_masters", tags=["trap_masters"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_trap_master():
    return {}