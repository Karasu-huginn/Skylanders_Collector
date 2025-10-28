from fastapi import APIRouter, Depends, HTTPException
from models.vehicle_model import Vehicle
from base_models import VehicleBase
from sqlalchemy.orm import Session
from starlette import status
from db import get_db
from typing import Annotated

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

db_dep = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vehicle():
    return {}