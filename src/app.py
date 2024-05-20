from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from src.orm import migrate_data
from src.consumer import processing
from src.cloud import ingest_azure
from threading import Thread
import urllib
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
        print('ingestion starting')
        ingest_thread.start()

        processing_thread.join()
        migration_thread.join()
        print('igestion joining')
        ingest_thread.join()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
if __name__ == "__main__":
    uvicorn.run("app:app", port=8080, host="0.0.0.0", reload=True)