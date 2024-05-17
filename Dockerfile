FROM python:3.9-slim

WORKDIR /retail_streaming

COPY requirements.txt .
RUN pip3 install -r requirements.txt
# Install system dependencies and ODBC drivers
RUN apt-get update && apt-get install -y \
    build-essential \
    unixodbc \
    unixodbc-dev \
    libsqliteodbc \
    odbcinst \
    curl \
    libpq-dev \
    iputils-ping \
    inetutils-telnet \
    && apt-get clean

# Install ODBC Driver 17 for SQL Server (Ubuntu 18.04)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

COPY ./src ./src




EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

CMD ["python3", "./src/app.py"]

VOLUME /retail_streaming/src
