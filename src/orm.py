import json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from kafka import KafkaConsumer
import logging
from src.models import Store, Product, Sale, SaleProduct

try:
    pg_engine = create_engine('postgresql://hazem:admin@retail-streaming-postgres-1/Delhaize_Sales')
    Base = declarative_base()
    Base.metadata.create_all(pg_engine)
    session = sessionmaker(bind=pg_engine)
    logging.info("PostgreSQL connection established and tables created if not exist.")
except Exception as e:
    logging.error(f"Failed to connect to PostgreSQL: {e}")

def migrate_data(message):

        data = message.value.decode('utf-8')
        data = json.loads(data)
        print('loaded')
        Session = session()

        store = Session.query(Store).filter_by(name=data['store']).first()
        if not store:
            store = Store(name=data['store'])
            Session.add(store)
            Session.commit() 
            print('added store')
        
        sale = Sale(store=store, date=data['date'], total_price=data['total_price'])
        Session.add(sale)
        print('added sale')
        
        for product_data in data['products']:
            product = Session.query(Product).filter_by(name=product_data['name']).first()
            if not product:
                product = Product(name=product_data['name'], category=product_data['category'])
                Session.add(product)
                Session.commit()  
                print('added product')
            
            sale_product = SaleProduct(sale=sale, product=product, price=product_data['price'])
            Session.add(sale_product)

        Session.commit()
        print('committed')
        Session.close()


