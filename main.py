from fastapi import FastAPI
import models
from database import engine
from routers.admin.v1 import api as admin
from routers.app.v1 import api

# creates the db
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="IT short",description="API for It short")
app.include_router(admin.router)