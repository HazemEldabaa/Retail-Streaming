import pyodbc
import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import urllib

def ingest_azure():
    print('preparing ingestion......')
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
    #sql_connection_string = f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}?driver={driver.replace(' ', '+')}"

    pg_connection_string = 'postgresql://hazem:admin@retail-streaming-postgres-1/Delhaize_Sales'
    # Define SQLAlchemy Base
    Base = declarative_base()

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

    # Create Azure SQL Database engine
    sql_engine = create_engine(sql_connection_string)
    Base.metadata.create_all(sql_engine)  # Create tables if they don't exist

    # Create a new session
    Session = sessionmaker(bind=sql_engine)
    session = Session()

    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(pg_connection_string)
    pg_cursor = pg_conn.cursor()

    # Fetch data from PostgreSQL and insert into Azure SQL Database
    try:
        # Fetch stores
        pg_cursor.execute("SELECT id, name FROM stores")
        stores = pg_cursor.fetchall()
        for store in stores:
            session.merge(Store(id=store[0], name=store[1]))

        # Fetch products
        pg_cursor.execute("SELECT id, name, category FROM products")
        products = pg_cursor.fetchall()
        for product in products:
            session.merge(Product(id=product[0], name=product[1], category=product[2]))

        # Fetch sales
        pg_cursor.execute("SELECT id, store_id, date, total_price FROM sales")
        sales = pg_cursor.fetchall()
        for sale in sales:
            session.merge(Sale(id=sale[0], store_id=sale[1], date=sale[2], total_price=sale[3]))

        # Fetch sale_products
        pg_cursor.execute("SELECT id, sale_id, product_id, price FROM sale_products")
        sale_products = pg_cursor.fetchall()
        for sale_product in sale_products:
            session.merge(SaleProduct(id=sale_product[0], sale_id=sale_product[1], product_id=sale_product[2], price=sale_product[3]))

        # Commit the session
        session.commit()
        print('boom bitch')
    except SQLAlchemyError as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        # Close connections
        pg_cursor.close()
        pg_conn.close()
        session.close()

    print("Data transfer complete.")