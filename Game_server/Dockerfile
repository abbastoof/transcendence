# Use an official Python runtime as a parent image
FROM python:3.11

WORKDIR /app

COPY ./Game_server/ /app

RUN pip install --no-cache-dir -r requirements.txt

# Install network utilities
RUN apt-get update && \
    apt-get install -y net-tools lsof iproute2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
EXPOSE 8010
HEALTHCHECK --interval=30s --timeout=2s --start-period=5s --retries=3 CMD curl -sSf http://localhost:8010 > /dev/null &&  echo "success" || echo "failure"
CMD ["python3", "server.py"]