import random
from datetime import datetime
import requests 
from pydantic import BaseModel
import json

produce_dict = {
    "apple": {"id": 101, "price": 0.75},
    "banana": {"id": 102, "price": 0.60},
    "orange": {"id": 103, "price": 0.80},
    "pear": {"id": 104, "price": 0.90},
    "kiwi": {"id": 105, "price": 1.00},
    "bread": {"id": 201, "price": 2.50},
    "croissant": {"id": 202, "price": 1.80},
    "baguette": {"id": 203, "price": 3.00},
    "cake": {"id": 204, "price": 4.50},
    "water": {"id": 301, "price": 1.20},
    "soda": {"id": 302, "price": 1.50},
    "beer": {"id": 303, "price": 2.00},
    "wine": {"id": 304, "price": 8.00}
}

class Product(BaseModel):
    id: str
    name: str
    price: float

class Item(BaseModel):
    id: str
    store: str
    date: str
    products: list[Product]

def random_product_selector():
    random_produce = random.choice(list(produce_dict.keys()))
    produce_object = produce_dict[random_produce]
    return {'id': produce_object['id'], 'name': random_produce, 'price': produce_object['price']}

def random_products_list_generator():
    product_list = []
    for _ in range(random.randint(1, 10)):
        product_list.append(random_product_selector())
    return product_list

def create_receipt():
    receipt_id = str(random.randint(1000, 100000))
    store = random.choice(["Brussels", "Leuven", "Ghent", "Antwerp", "Bruges", "Charleroi", "Namur"])
    date = datetime.now().isoformat()
    products = random_products_list_generator()

    product_list = []
    for product in products:
        product_list.append(Product(id=str(product['id']), name=product['name'], price=product['price']))

    return Item(id=receipt_id, store=store, date=date, products=product_list)

for _ in range(100):
    receipt_data = json.dumps(create_receipt().dict())
    requests.post('http://localhost:8080/data', data=receipt_data)
