# 🛍️Retail-Streaming

Welcome to the latest learning-project of my Data Engineering adventure, this project involves building a data pipeline for retail stores to process and analyze customer purchase data. The goals are to create an API that sends data to a Kafka queue (producer), preprocess the data (consumer), and store the processed data in a cloud database. Additionally, the project follows DevOps best practices including Docker, IaC, CI/CD, clean coding, and unit testing.

## 🛒Description

The API recieves raw unstructured data in the following format:
```JSON
{
    "id": "123456789",
    "store": "Brussels",
    "date": "2020-01-01",
    "products": [
        {
            "id": "123456789",
            "name": "Banana",
            "price": 1.5
        },
        {
            "id": "123456789",
            "name": "Bread",
            "price": 1.5
        },
        {
            "id": "123456789",
            "name": "Water",
            "price": 1.5
        }
    ]
}
```
The functions process the data into the following format before structuring them into a database:
```JSON
{
    "id": "123456789",
    "store": "Brussels",
    "date": "2020-01-01",
    "total_price": 4.5,
    "products": [
        {
            "id": "123456789",
            "name": "Banana",
            "price": 1.5,
            "category": "Fruit"
        },
        {
            "id": "123456789",
            "name": "Bread",
            "price": 1.5,
            "category": "Bakery"
        },
        {
            "id": "123456789",
            "name": "Water",
            "price": 1.5,
            "category": "Drink"
        }
    ]
}
```


##  📁Project Structure
- src :
    - app.py : The main FastAPI app with the post endpoint
    - models.py : Definition of the DB schema using pydantic models
    - consumer.py : Processing data into the desired format
    - orm.py : Creates a relational database
    - cloud.py : Merge the local Postgres DB with Azure SQL Server
- terraform :
    - main.tf : IaC to configure Azure SQL Server/Database
- bill_generator : Dummy bills generator sent to the API endpoint
- docker-compose.yml : docker-compose for the image
- Dockerfile : Virtual environment with all the dependencies of the apps.
# 🏁Getting Started

## 📋Prerequisites
- Python 3.x
- Docker Desktop
## 🛠️Installation

**Clone the Repository:**

```bash
git clone https://github.com/HazemEldabaa/Retail-Streaming.git
cd Retail-Streaming
```
**Create a Virtual Environment (Optional but recommended):**

```bash
python -m venv venv
source venv/bin/activate   # On Windows: \venv\Scripts\activate
```
**Install Dependencies:**

```bash
pip install -r requirements.txt
```
## 👩‍💻Usage
#### To run locally:
Firstly, configure your Azure Cloud app credentials in the ```terraform/main.tf``` then:

```bash
 cd terraform
 terraform init
 terraform apply
 ```
This should deploy all your resources and set up your authentication with the server.

Edit the ``` docker-compose.yml ``` with your desired Postgres credentials and environment variables

Make sure Docker Desktop is installed and running, then run in the terminal:
```bash
docker-compose up --build -d
```
after all the services are running, you should be able to check the API is running through http://localhost:8080/

To send requests to the endpoint:

```bash
python bill_generator.py
```




## 📷Screenshots
### Postgres DB on PgAdmin:
![Postgres DB on PgAdmin](https://i.ibb.co/vjvwyhZ/postgres-db.png)

### SQL DB on Microsoft SQL Server:
![Postgres DB on PgAdmin](https://i.ibb.co/KVbCfDk/azure-database.png)