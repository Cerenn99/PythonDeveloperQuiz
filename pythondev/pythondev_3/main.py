from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import time


DATABASE_URL = "sqlite:///./test.db"  


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    age = Column(Integer)
    created_at = Column(String)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    total_amount = Column(Integer)
    created_at = Column(String)
    user_id = Column(Integer)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    created_at: str

class OrderCreate(BaseModel):
    order_number: str
    total_amount: int
    created_at: str
    user_id: int


app = FastAPI()


Base.metadata.create_all(bind=engine)


@app.post("/users/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email, age=user.age, created_at=user.created_at)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/orders/")
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(order_number=order.order_number, total_amount=order.total_amount, created_at=order.created_at, user_id=order.user_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.put("/users/{user_id}/")
async def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
    db_user.age = user.age
    db_user.created_at = user.created_at
    db.commit()
    db.refresh(db_user)
    return db_user


@app.delete("/users/{user_id}/")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}


@app.post("/insert_bulk/")
async def insert_bulk_data(db: Session = Depends(get_db)):
    start_time = time.time()

   
    for i in range(100000):
        user = User(name=f"User_{i}", email=f"user_{i}@example.com", age=20 + (i % 50), created_at="2024-11-06")
        db.add(user)
        if i % 1000 == 0:  
            db.commit()

    db.commit()
    end_time = time.time()
    elapsed_time = end_time - start_time
    return {"message": f"100,000 users inserted in {elapsed_time:.2f} seconds"}
