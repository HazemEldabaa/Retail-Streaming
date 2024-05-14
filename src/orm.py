import json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from kafka import KafkaConsumer

# Define the database connection
engine = create_engine('sqlite:///retail.db')
Base = declarative_base()

# Define the Store model
class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    sales = relationship("Sale", back_populates="store")

# Define the Product model
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
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

# Create tables in the database
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)

# Create a Kafka consumer
consumer = KafkaConsumer('processed_data', bootstrap_servers='localhost:29092', auto_offset_reset='earliest', enable_auto_commit=True)

# Process messages from Kafka
for message in consumer:
    data = message.value.decode('utf-8')
    data = json.loads(data)
    
    # Open a session
    session = Session()

    # Insert data into the database
    store = Store(name=data['store'])
    session.add(store)

    sale = Sale(store=store, date=data['date'], total_price=data['total_price'])
    session.add(sale)

    for product_data in data['products']:
        product = Product(name=product_data['name'], category=product_data['category'])
        session.add(product)
        
        sale_product = SaleProduct(sale=sale, product=product, price=product_data['price'])
        session.add(sale_product)

    # Commit changes and close session
    session.commit()
    session.close()

# Close the Kafka consumer
consumer.close()
