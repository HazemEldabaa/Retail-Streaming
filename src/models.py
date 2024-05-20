# models.py (or top of your existing file)

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Store(Base):
    __tablename__ = 'stores'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    sales = relationship("Sale", back_populates="store")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    category = Column(String)
    sales = relationship("SaleProduct", back_populates="product")

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
