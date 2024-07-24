# Use an official Python runtime as a parent image
FROM python:3.8

WORKDIR /app

COPY ./Game_server/ /app

RUN pip install --no-cache-dir -r requirements.txt

# Install network utilities
RUN apt-get update && \
    apt-get install -y net-tools lsof iproute2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
EXPOSE 8010

CMD ["python3", "server.py"]