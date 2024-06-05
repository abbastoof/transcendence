FROM python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# this will copy the entire project into the container 
COPY . .

EXPOSE 8000

CMD ["gunicorn", "user_service.wsgi:application", "--bind", "0.0.0.0:8000"]
