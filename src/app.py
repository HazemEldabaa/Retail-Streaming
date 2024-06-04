from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaConsumer, KafkaProducer
import uvicorn
import asyncio
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from threading import Thread
from dotenv import load_dotenv
import os
import sys
import logging  
from src.consumer import process
from src.orm import migrate_data
from src.cloud import ingest_azure
from threading import Thread
import socket
import time

load_dotenv()

app = FastAPI()
print('server is running...')

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Item(BaseModel):
    id : str
    store : str
    date : str
    products : list[Product]

def create_kafka_producer():
    while True:
        # Check if Kafka brokers are available
        try:
            socket.create_connection(('kafka', 29092), timeout=1)
            producer = KafkaProducer(bootstrap_servers='kafka:29092')
            return producer
        except ConnectionRefusedError:
            print("Error: No Kafka brokers available. Retrying in 5 seconds...")
            time.sleep(5)


producer = KafkaProducer(bootstrap_servers="kafka:29092")
logger.info("Kafka producer created successfully.")

try:
    pg_engine = create_engine('postgresql://hazem:admin@retail-streaming-postgres-1/Delhaize_Sales')
    Base = declarative_base()
    Base.metadata.create_all(pg_engine)
    logger.info("PostgreSQL connection established and tables created if not exist.")
except Exception as e:
    logger.error(f"Failed to connect to PostgreSQL: {e}")


class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    date = Column(String)
    total_price = Column(Integer)
    store = relationship("Store", back_populates="sales")
    products = relationship("SaleProduct", back_populates="sale")


class SaleProduct(Base):
    __tablename__ = 'sale_products'
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Integer)
    sale = relationship("Sale", back_populates="products")
    product = relationship("Product", back_populates="sales")

sql_engine = create_engine(sql_connection_string)
Base.metadata.create_all(sql_engine)
Base.metadata.create_all(engine)
print('created producer')

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(consume_raw_data())
    loop.create_task(consume_processed_data())

async def consume_raw_data():
    while True:
        msg = raw.poll(1.0)
        if msg is None:
            await asyncio.sleep(1)
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Consumer error: {msg.error()}")
                continue
        print(f"Received raw message: {msg.value().decode('utf-8')}")
        processing(msg)

async def consume_processed_data():
    while True:
        msg = processed.poll(1.0)
        if msg is None:
            await asyncio.sleep(1)
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Consumer error: {msg.error()}")
                continue
        print(f"Received processed message: {msg.value().decode('utf-8')}")
        migrate_data(engine, Base, msg)
        await ingest_azure()
@app.get("/")
async def read_root():
    return {"status": "ok"}

@app.post("/data")
def data(user_data: ItemModel):
    logger.info(f"Received user data: {user_data}")
    try:
        print('Try catch')
        consumer_thread = Thread(target=consume_messages)
        consumer_thread.start()

        logger.info("Consumer thread started successfully.")
        serialized_data = user_data.json()
        producer.send('raw_data', serialized_data.encode('utf-8'))
        producer.flush()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error in data endpoint: {e}")
        return {"status": "error", "message": str(e)}
    

def consume_messages():
    try:
        logger.info('Launching consumer...')
        consumer = KafkaConsumer(
            'raw_data',
            bootstrap_servers='kafka:29092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='my-group'
        )
        logger.info('Consumer started, waiting for messages...')
        for message in consumer:
            logger.info(f"Received message: {message.value.decode('utf-8')}")
            logger.info(f'message value {message.value}')
            process(message.value)
            consumer.close()
    except Exception as e:
        logger.error(f"Error in consumer: {e}")

if __name__ == "__main__":
    try:
        uvicorn.run("app:app", port=8080, host="0.0.0.0", reload=True)
    except Exception as e:
        logger.error(f"Failed to start FastAPI server: {e}")
