from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from src.orm import migrate_data
from src.consumer import processing
from src.cloud import ingest_azure
from threading import Thread
# from celery import Celery
print("testing ci/cd")



app = FastAPI()
class Product(BaseModel):
    id : str
    name : str
    price : float

class Item(BaseModel):
    id : str
    store : str
    date : str
    products : list[Product]


producer = KafkaProducer(bootstrap_servers='kafka:29092')
# @celery_app.task
engine = create_engine('postgresql://hazem:admin@retail-streaming-postgres-1/Delhaize_Sales')
print("db created")
Base = declarative_base()  
print('created producer')
@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/data")
def data(user_data: Item):
    print('user_data', user_data)
    try:
        # Convert the user_data to a dictionary and serialize it to JSON
        serialized_data = user_data.model_dump_json()
        #serialized_data = user_data
        # Produce the serialized data to the Kafka topic
        producer.send('raw_data', serialized_data.encode('utf-8'))
        # Wait up to 1 second for events. Callbacks will be invoked during
        # this method call if the message is acknowledged.
        producer.flush(1)
         
        processing_thread = Thread(target=processing)
        migration_thread = Thread(target=migrate_data, args=(engine, Base))
        ingest_thread = Thread(target=ingest_azure)

        processing_thread.start()
        migration_thread.start()
        ingest_thread.start()

        processing_thread.join()
        migration_thread.join()
        ingest_thread.join()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, host="0.0.0.0", reload=True)