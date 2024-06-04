from kafka import KafkaConsumer, KafkaProducer
import json
import logging
from threading import Thread
from src.orm  import migrate_data

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

def process(raw):
    logging.info(f'consumed data {raw}')
    data = json.loads(raw)
    total_price = sum(product['price'] for product in data['products'])

    data['total_price'] = total_price

    formatted_data = {
    "id": data["id"],
    "store": data["store"],
    "date": data["date"],
    "total_price": data["total_price"],
    "products": data["products"]
    }

    for product in formatted_data['products']:
        for category, products in categories.items():
            if product['name'] in products:
                product['category'] = category
                break
        else:
            product['category'] = "Unknown"

    formatted_data_str = json.dumps(formatted_data, indent=4)
    logging.info(f'formatted data {formatted_data_str}')

    try:
        migration_consumer_thread= Thread(target=data_migration)
        migration_consumer_thread.start()

        producer = KafkaProducer(bootstrap_servers='kafka:29092')
        producer.send('processed_data', formatted_data_str.encode('utf-8'))
        producer.flush()
    except Exception as e:
        logging.error(f"error in consumer {e}")    
        return {"status": "error", "message": str(e)}


def data_migration():
    try:
        logging.info('launching migration...')
        migration_consumer = KafkaConsumer(
            'processed_data',
            bootstrap_servers='kafka:29092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='migration-group'
        )
        logging.info('Migration Consumer started...')
        for message in migration_consumer:
            logging.info(f'received formatted data {message}')
            migrate_data(message)
    except Exception as e:
        logging.error(f"Error in consumer: {e}")
