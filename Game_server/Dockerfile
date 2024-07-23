# Use an official Python runtime as a parent image
FROM python:3.8

WORKDIR /app

COPY ./Game_server/ /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8010

CMD ["python", "server.py"]