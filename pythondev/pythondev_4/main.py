import multiprocessing
import time
import random
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import asyncio
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProcessStatus(Base):
    __tablename__ = "process_status"
    id = Column(Integer, primary_key=True, index=True)
    process_id = Column(String, index=True)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)


app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the app!"}

def task_process(process_id):
  
    
    time.sleep(random.uniform(1, 5)) 
    return f"Process {process_id} completed."

async def run_processes():
   
    pool = []
    for i in range(1000):
        p = multiprocessing.Process(target=execute_task, args=(str(i),))
        pool.append(p)
        p.start()

  
    for p in pool:
        p.join()

def execute_task(process_id):
   
    status = "Started"
    db = SessionLocal()


    db.add(ProcessStatus(process_id=process_id, status=status))
    db.commit()

    try:
        task_result = task_process(process_id)
        status = "Completed"
    except Exception as e:
        task_result = str(e)
        status = "Failed"
    finally:
       
        db.add(ProcessStatus(process_id=process_id, status=status))
        db.commit()


@app.post("/start_processes/")
async def start_processes():
   
    await run_processes()
    return JSONResponse(status_code=200, content={"message": "Processes started"})


@app.get("/status/{process_id}")
async def get_process_status(process_id: str):
   
    db = SessionLocal()
    status = db.query(ProcessStatus).filter(ProcessStatus.process_id == process_id).all()
    if status:
        return {"process_id": process_id, "status": status[-1].status, "timestamp": status[-1].timestamp}
    else:
        return {"error": "Process not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
