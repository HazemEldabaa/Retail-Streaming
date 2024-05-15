from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from src.orm import migrate_data
from src.consumer import processing
from threading import Thread
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

@app.post('/data')
def read_receipt(receipt: Item):
    print(receipt)
    process_data(receipt)

producer = KafkaProducer(bootstrap_servers='kafka:29092')
engine = create_engine('postgresql://hazem:admin@retail-streaming-postgres-1/Delhaize_Sales')


Base = declarative_base()  
@app.get("/")
async def read_root():
    return {"status": "ok"}


def process_data(user_data: Item):
    print(user_data)
    try:
        # Convert the user_data to a dictionary and serialize it to JSON
        # Produce the serialized data to the Kafka topic
        producer.send('raw_data', user_data.encode('utf-8'))
        # Wait up to 1 second for events. Callbacks will be invoked during
        # this method call if the message is acknowledged.
        producer.flush(1)
         
        processing_thread = Thread(target=processing)
        migration_thread = Thread(target=migrate_data, args=(engine, Base))

        processing_thread.start()
        migration_thread.start()

        processing_thread.join()
        migration_thread.join()

        return {"status": "okitos"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    


if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, host="0.0.0.0", reload=True)