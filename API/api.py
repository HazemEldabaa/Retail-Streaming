from fastapi import FastAPI
from pydantic import BaseModel
from confluent_kafka import Producer
from kafka import KafkaProducer
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

producer_conf = {
    'bootstrap.servers': 'http://localhost:29092/', 
}

producer = KafkaProducer(bootstrap_servers='localhost:29092')

@app.post("/data")
async def data(user_data: Item):
    try:
        # Convert the user_data to a dictionary and serialize it to JSON
        #serialized_data = user_data.model_dump_json()
        serialized_data = user_data
        # Produce the serialized data to the Kafka topic
        producer.send('raw_data', serialized_data.encode('utf-8'))
        # Wait up to 1 second for events. Callbacks will be invoked during
        # this method call if the message is acknowledged.
        producer.flush(1)

        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

