import json
from sqlalchemy.orm import sessionmaker
from src.models import Store, Product, Sale, SaleProduct

def migrate_data(engine, Base, message):
    # Decode the message value to get the JSON data
    data = message.value().decode('utf-8')
    data = json.loads(data)

    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if the store exists
        store = session.query(Store).filter_by(name=data['store']).first()
        if not store:
            store = Store(name=data['store'])
            session.add(store)
            session.commit()  # Commit to generate the store ID
        
        # Create a Sale instance
        sale = Sale(store=store, date=data['date'], total_price=data['total_price'])
        session.add(sale)
        
        # Process each product in the message
        for product_data in data['products']:
            # Check if the product exists
            product = session.query(Product).filter_by(name=product_data['name']).first()
            if not product:
                product = Product(name=product_data['name'], category=product_data['category'])
                session.add(product)
                session.commit()  # Commit to generate the product ID
            
            # Create a SaleProduct instance
            sale_product = SaleProduct(sale=sale, product=product, price=product_data['price'])
            session.add(sale_product)
        
        # Commit changes to the database
        session.commit()
    except Exception as e:
        # Rollback the session if an error occurs
        session.rollback()
        raise e

        # Close the session

