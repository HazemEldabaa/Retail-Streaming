from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from confluent_kafka import Producer, Consumer, KafkaError, KafkaException
from confluent_kafka.admin import AdminClient
import uvicorn
import asyncio
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.orm import migrate_data
from src.consumer import processing
from src.cloud import ingest_azure
from threading import Thread
import urllib
import socket
import time
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

def create_kafka_producer():
    while True:
        try:
            # Check if Kafka brokers are available
            socket.create_connection(('kafka', 29092), timeout=1)
            # If reachable, create Kafka producer
            producer = KafkaProducer(bootstrap_servers='kafka:29092')
            return producer
        except ConnectionRefusedError:
            print("Error: No Kafka brokers available. Retrying in 5 seconds...")
            time.sleep(5)
# def create_kafka_topics():
#     admin_client = KafkaAdminClient(bootstrap_servers='kafka:29092')
#     topics = [NewTopic(name='raw_data', num_partitions=1, replication_factor=1),
#               NewTopic(name='processed_data', num_partitions=1, replication_factor=1)]
#     admin_client.create_topics(topics)
# create_kafka_topics()
# #producer = KafkaProducer(bootstrap_servers='kafka:29092')
# producer = create_kafka_producer()
# raw = KafkaConsumer(bootstrap_servers='kafka:29092')
# processed = KafkaConsumer(bootstrap_servers='kafka:29092')
# producer_conf = {
#     'bootstrap.servers': 'kafka:29092',
# }


def check_and_create_topic(admin_client, topic_name, num_partitions, replication_factor):
    """Check if a topic exists, and create it if it does not."""
    topic_metadata = admin_client.list_topics(timeout=10)
    if topic_name in topic_metadata.topics:
        print(f"Topic '{topic_name}' already exists.")
        return
    else:
        print(f"Creating topic '{topic_name}'...")
        new_topic = NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
        fs = admin_client.create_topics([new_topic])
        try:
            fs[topic_name].result()  # Wait for operation to finish
            print(f"Topic '{topic_name}' created successfully.")
        except KafkaException as e:
            print(f"Failed to create topic '{topic_name}': {e}")
            raise


# Kafka bootstrap servers
bootstrap_servers = 'kafka:29092'

# Wait for the broker to be available
producer = create_kafka_producer()
# Create an AdminClient
admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})

# Topics to check and create if not exist
topics = [
    {"name": "raw_data", "num_partitions": 1, "replication_factor": 1},
    {"name": "processed_data", "num_partitions": 1, "replication_factor": 1}
]

# Check and create topics
for topic in topics:
    check_and_create_topic(admin_client, topic["name"], topic["num_partitions"], topic["replication_factor"])
consumer_conf = {
    'bootstrap.servers': 'kafka:29092',
    'group.id': 'my_consumer_group',
    'auto.offset.reset': 'earliest',
}

raw = Consumer(consumer_conf)
processed = Consumer(consumer_conf)
raw.subscribe(['raw_data'])
processed.subscribe(['processed_data'])
engine = create_engine('postgresql://hazem:admin@retail-streaming-postgres-1/Delhaize_Sales')
print("db created")
Base = declarative_base()
server = 'retail-salessqlserver.database.windows.net'
database = 'retail-salesdb'
username = 'hazem'
password = 'h@z3m6969!' 
driver= '{ODBC Driver 17 for SQL Server}'
params = urllib.parse.quote_plus(
    f"DRIVER={driver};"
    f"SERVER={server},1433;"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password}"
)
sql_connection_string = f"mssql+pyodbc:///?odbc_connect={params}"  
# Define the Store model
class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    sales = relationship("Sale", back_populates="store")

# Define the Product model
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    category = Column(String)
    sales = relationship("SaleProduct", back_populates="product")

# Define the Sale model
class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    date = Column(String)
    total_price = Column(Integer)
    store = relationship("Store", back_populates="sales")
    products = relationship("SaleProduct", back_populates="sale")

# Define the SaleProduct model
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
    # Create tables in the database
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
async def data(user_data: Item):
    print('user_data', user_data)
    try:
        # Convert the user_data to a dictionary and serialize it to JSON
        serialized_data = user_data.model_dump_json()
        print(serialized_data)
        # Produce the serialized data to the Kafka topic
        producer.send('raw_data', serialized_data.encode('utf-8'))
        # Wait up to 1 second for events..
        producer.flush(2)
        print("Processing, please wait....")

        return {"status": "okitos"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    


if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, host="0.0.0.0", reload=True)