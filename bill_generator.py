import random
from datetime import datetime

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

def random_product_selector():
    random_produce  =  random.choice(list(produce_dict.keys()))
    produce_object= produce_dict[random_produce]
    return {'name': random_produce.__str__(), 'id': produce_object['id'], 'price': produce_object['price']}

def random_products_list_generator():
    product_list =  []
    for x in range(random.randint(1, 10)):
        product_list.append( random_product_selector())
    return product_list


def  create_receipt():
    receipt_id = random.randint(1000,  100000).__str__()
    store = 'Brussels'
    date= datetime.now().__str__()
    products= random_products_list_generator()

    receipt= {'id': receipt_id, 'store': store, 'date': date, 'products': products}
    return receipt


print(create_receipt())