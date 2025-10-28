from typing import Annotated, List
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from db import get_db, engine, Base
import routers.edition_router as e_router
import routers.magic_item_router as mi_router
import routers.level_router as l_router
import routers.villain_sensei_router as vs_router
import routers.sensei_router as s_router
import routers.skylanders_router as sk_router
import routers.giant_router as g_router
import routers.swapper_router as sw_router
import routers.trap_master_router as tm_router
import routers.trap_router as t_router
import routers.vehicle_router as v_router
import routers.creation_crystal_router as cc_router

app = FastAPI()
app.include_router(e_router.router)
app.include_router(mi_router.router)
app.include_router(l_router.router)
app.include_router(vs_router.router)
app.include_router(s_router.router)
app.include_router(sk_router.router)
app.include_router(g_router.router)
app.include_router(sw_router.router)
app.include_router(tm_router.router)
app.include_router(t_router.router)
app.include_router(v_router.router)
app.include_router(cc_router.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)
db_dep = Annotated[Session, Depends(get_db)]

#* FastAPI endpoints
@app.get("/{item_id}")
def root(item_id:int):
    return {"var":item_id}
