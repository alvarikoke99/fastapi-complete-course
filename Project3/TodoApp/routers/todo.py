from starlette import status
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.orm import Session
from typing import Annotated
from database import SessionLocal
from models import Todo

router = APIRouter()

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    completed: bool

@router.get("/")
async def read_all(db: db_dependency, status_code=status.HTTP_200_OK):
    return db.query(Todo).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todo(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()

@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()

    if not todo_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()

    if not todo_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")

    db.delete(todo_model)
    db.commit()