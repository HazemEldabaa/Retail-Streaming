import asyncio
from fastapi import FastAPI
from pydantic import BaseModel
from confluent_kafka import Producer
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from threading import Thread
import urllib
from dotenv import load_dotenv
import os
from src.orm import migrate_data
from src.consumer import processing
from src.cloud import ingest_azure

load_dotenv()

app = FastAPI()

class ProductModel(BaseModel):
    id: str
    name: str
    price: float

class ItemModel(BaseModel):
    id: str
    store: str
    date: str
    products: list[ProductModel]

# Kafka producer setup
producer = Producer({'bootstrap.servers': 'kafka:29092'})

# PostgreSQL connection
pg_engine = create_engine('postgresql://hazem:admin@retail-streaming-postgres-1/Delhaize_Sales')
Base = declarative_base()

# Create tables if they do not exist
Base.metadata.create_all(pg_engine)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/data")
async def data(user_data: ItemModel):
    print('user_data', user_data)
    try:
        serialized_data = user_data.json()

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, producer.produce, 'raw_data', serialized_data.encode('utf-8'))
        await loop.run_in_executor(None, producer.flush, 1)

        # Run processing and migration in separate threads
        processing_thread = Thread(target=processing)
        migration_thread = Thread(target=migrate_data, args=(pg_engine, Base))
        
        processing_thread.start()
        migration_thread.start()
        
        # Run ingest_azure asynchronously within an executor
        await loop.run_in_executor(None, ingest_azure)

        processing_thread.join()
        migration_thread.join()

        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, host="0.0.0.0", reload=True)
