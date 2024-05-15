FROM python:3.9-slim

WORKDIR /retail_streaming

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./src ./src




EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

CMD ["python3", "./src/api.py"]

VOLUME /retail_streaming/src
