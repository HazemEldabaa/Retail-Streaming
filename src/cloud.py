import pyodbc
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import urllib
import os
from dotenv import load_dotenv
from src.models import Store, Product, Sale, SaleProduct

load_dotenv()

def ingest_azure():
    print('Preparing ingestion...')
    
    # Load environment variables
    server = os.getenv('AZURE_SQL_SERVER')
    database = os.getenv('AZURE_SQL_DATABASE')
    username = os.getenv('AZURE_SQL_USER')
    password = os.getenv('AZURE_SQL_PASSWORD') 

    # Check if environment variables are loaded
    if not all([server, database, username, password]):
        print("Error: One or more Azure SQL environment variables are not set.")
        return

    driver = '{ODBC Driver 17 for SQL Server}'
    params = urllib.parse.quote_plus(
        f"DRIVER={driver};"
        f"SERVER={server},1433;"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password}"
    )
    sql_connection_string = f"mssql+pyodbc:///?odbc_connect={params}"

    pg_connection_string = 'postgresql://hazem:admin@retail-streaming-postgres-1/Delhaize_Sales'

    # Create Azure SQL Database engine
    sql_engine = create_engine(sql_connection_string)
    # Create PostgreSQL engine
    pg_engine = create_engine(pg_connection_string)

    # Create a new session for Azure SQL
    SqlSession = sessionmaker(bind=sql_engine)
    sql_session = SqlSession()

    # Create a new session for PostgreSQL
    PgSession = sessionmaker(bind=pg_engine)
    pg_session = PgSession()

    try:
        # Fetch and insert stores
        pg_stores = pg_session.query(Store).all()
        for pg_store in pg_stores:
            existing_store = sql_session.query(Store).filter_by(id=pg_store.id).first()
            if not existing_store:
                sql_session.add(Store(id=pg_store.id, name=pg_store.name))
        print('Fetched and inserted stores.')

        # Fetch and insert products
        pg_products = pg_session.query(Product).all()
        for pg_product in pg_products:
            existing_product = sql_session.query(Product).filter_by(id=pg_product.id).first()
            if not existing_product:
                sql_session.add(Product(id=pg_product.id, name=pg_product.name, category=pg_product.category))
        print('Fetched and inserted products.')

        # Fetch and insert sales
        pg_sales = pg_session.query(Sale).all()
        for pg_sale in pg_sales:
            existing_sale = sql_session.query(Sale).filter_by(id=pg_sale.id).first()
            if not existing_sale:
                sql_session.add(Sale(id=pg_sale.id, store_id=pg_sale.store_id, date=pg_sale.date, total_price=pg_sale.total_price))
        print('Fetched and inserted sales.')

        # Fetch and insert sale_products
        pg_sale_products = pg_session.query(SaleProduct).all()
        for pg_sale_product in pg_sale_products:
            existing_sale_product = sql_session.query(SaleProduct).filter_by(id=pg_sale_product.id).first()
            if not existing_sale_product:
                sql_session.add(SaleProduct(id=pg_sale_product.id, sale_id=pg_sale_product.sale_id, product_id=pg_sale_product.product_id, price=pg_sale_product.price))
        print('Fetched and inserted sale_products.')

        # Commit the session
        sql_session.commit()
        print('Data ingestion completed successfully.')
    except SQLAlchemyError as e:
        print(f"SQLAlchemy error occurred: {e}")
        sql_session.rollback()
    except Exception as e:
        print(f"An error occurred: {e}")
        sql_session.rollback()
    finally:
        # Close sessions
        pg_session.close()
        sql_session.close()

    print("Data transfer complete.")

if __name__ == "__main__":
    ingest_azure()
