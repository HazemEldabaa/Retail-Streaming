from kafka import KafkaConsumer, KafkaProducer
import json

import asyncio
from confluent_kafka import Consumer
import json
import os

def processing(msg):
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


    raw = msg.value().decode('utf-8')
    data = json.loads(raw)

    # Calculate total price
    total_price = sum(product['price'] for product in data['products'])
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
        product['category'] = get_category(product['name'])

    formatted_data_str = json.dumps(formatted_data, indent=4)


    producer = KafkaProducer(bootstrap_servers='kafka:29092')
    producer.send('processed_data', formatted_data_str.encode('utf-8'))
    producer.flush()

    print("Successfully sent data to Kafka topic: processed_data")

# Start the async processing function
if __name__ == "__main__":
    consumer_conf = {
        'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092'),
        'group.id': 'my_consumer_group',
        'auto.offset.reset': 'earliest'
    }
    asyncio.run(processing(consumer_conf))