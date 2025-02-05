import random
from datetime import datetime
import asyncio
import httpx
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


async def send_data(client, url):
    while True:
        data= create_receipt().dict()
        print('generated data', data)
        try:
            response = await client.post(url, json=data)
            if response.status_code == 200:
                print(f"Data sent successfully{data}")
            else:
                print(f"Failed to send data due to:{response.status_code}")
        except Exception as e:
            print(f"An  error occurred: {e}")
        await asyncio.sleep(random.uniform(0.5, 2))

async def main():
        url= 'http://localhost:8080/data'
        async with httpx.AsyncClient() as client:
            await send_data(client, url)
# async  def main():
#     url= 'http://localhost:8080/data'
#     async with httpx.AsyncClient()  as client:
#         await send_data(client,  url)

if __name__ == "__main__":
    asyncio.run(main())
print('done')