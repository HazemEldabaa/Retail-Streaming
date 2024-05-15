from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from orm import migrate_data
from consumer import processing
# from celery import Celery
print("start")

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

# celery_app = Celery('tasks', broker='redis://localhost:6379/0')

producer = KafkaProducer(bootstrap_servers='localhost:29092')
# @celery_app.task
#engine = create_engine('postgresql://hazem:admin@localhost:5432/Delhaize_Sales')
engine = create_engine('sqlite:///retail.db')
Base = declarative_base()  
print('created producer')
@app.get("/")
async def read_root():
    return {"status": "ok"}

@app.post("/data")
async def data(user_data: Item):
    try:
        # Convert the user_data to a dictionary and serialize it to JSON
        serialized_data = user_data.model_dump_json()
        #serialized_data = user_data
        # Produce the serialized data to the Kafka topic
        producer.send('raw_data', serialized_data.encode('utf-8'))
        # Wait up to 1 second for events. Callbacks will be invoked during
        # this method call if the message is acknowledged.
        producer.flush(1)
         
        processing()
        migrate_data(engine, Base)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
print('parsed')
if __name__ == "__main__":
    uvicorn.run("api:app", port=8080, host="0.0.0.0", reload=True)