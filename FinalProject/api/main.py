import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .routers import index as indexRoute
from .models import model_loader
from .dependencies.config import conf
from .schemas import sandwiches as schemas
from .controllers import sandwiches
from .dependencies.database import get_db

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_loader.index()
indexRoute.load_routes(app)

@app.post("/sandwiches/", response_model=schemas.Sandwich, tags=["Sandwiches"])
def create_sandwich(sandwich: schemas.SandwichCreate, db: Session = Depends(get_db)):
    return sandwiches.create(db=db, sandwich=sandwich)


@app.get("/sandwiches/", response_model=list[schemas.Sandwich], tags=["Sandwiches"])
def read_sandwiches(db: Session = Depends(get_db)):
    return sandwiches.read_all(db)


@app.get("/sandwiches/{sandwich_id}", response_model=schemas.Sandwich, tags=["Sandwiches"])
def read_one_sandwich(sandwich_id: int, db: Session = Depends(get_db)):
    sandwich = sandwiches.read_one(db, sandwich_id=sandwich_id)

    if sandwich is None:
        raise HTTPException(status_code=404, detail="Sandwich not found")

    return sandwich


@app.put("/sandwiches/{sandwich_id}", response_model=schemas.Sandwich, tags=["Sandwiches"])
def update_one_sandwich(
    sandwich_id: int,
    sandwich: schemas.SandwichUpdate,
    db: Session = Depends(get_db)
):
    sandwich_db = sandwiches.read_one(db, sandwich_id=sandwich_id)

    if sandwich_db is None:
        raise HTTPException(status_code=404, detail="Sandwich not found")

    return sandwiches.update(db=db, sandwich=sandwich, sandwich_id=sandwich_id)


@app.delete("/sandwiches/{sandwich_id}", tags=["Sandwiches"])
def delete_one_sandwich(sandwich_id: int, db: Session = Depends(get_db)):
    sandwich = sandwiches.read_one(db, sandwich_id=sandwich_id)

    if sandwich is None:
        raise HTTPException(status_code=404, detail="Sandwich not found")

    return sandwiches.delete(db=db, sandwich_id=sandwich_id)


if __name__ == "__main__":
    uvicorn.run(app, host=conf.app_host, port=conf.app_port)