from kafka import KafkaConsumer, KafkaProducer
import json
# Pseudocode example using an ORM library like SQLAlchemy

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Define the database connection
engine = create_engine('sqlite:///retail.db')
Base = declarative_base()

# Define the Store model
class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True)
    name = Column(String)

# Define the Product model
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)

# Define the Sale model
class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey('stores.id'))
    date = Column(String)
    total_price = Column(Integer)
    store = relationship("Store", back_populates="sales")

# Define the SaleProduct model
class SaleProduct(Base):
    __tablename__ = 'sale_products'
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Integer)
    sale = relationship("Sale", back_populates="products")
    product = relationship("Product", back_populates="sales")

categories = {
    "Fruit": "apple, banana, orange, pear, kiwi",
    "Bakery": "bread, croissant, baguette, cake",
    "Drink": "water, soda, beer, wine"
}

def get_category(product_name):
    for category, products in categories.items():
        if product_name in products:
            return category
    return "Unknown"
# Create Kafka consumer instance
consumer = KafkaConsumer('delhaize_shop', bootstrap_servers='localhost:29092', auto_offset_reset='earliest', enable_auto_commit=True)

# Iterate over messages in the Kafka topic
for message in consumer:
    raw = message.value.decode('utf-8')
    # Create a reverse mapping of product names to categories
    #products_json = raw['products']

# Deserialize JSON string into a Python list
    data = json.loads(raw)
    # Calculate total price
    total_price = sum(product['price'] for product in data['products'])

    # Add total price to data dictionary
    data['total_price'] = total_price

    formatted_data = {
    "id": data["id"],
    "store": data["store"],
    "date": data["date"],
    "total_price": data["total_price"],
    "products": data["products"]
}

    # Add category to each product
    for product in formatted_data['products']:
        for category, products in categories.items():
            if product['name'] in products:
                product['category'] = category
                break
        else:
            product['category'] = "Unknown"

    # Serialize dictionary back into JSON string
    formatted_data_str = json.dumps(formatted_data, indent=4)
    producer = KafkaProducer(bootstrap_servers='localhost:29092')
    producer.send('processed_data', formatted_data_str.encode('utf-8'))
    # Print formatted data
    print("Succesfully sent data to Kafka topic: processed_data")
    