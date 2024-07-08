FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install setuptools==58.0.4 wheel
RUN pip --timeout=1000 install -r requirements.txt

WORKDIR /app

COPY . /app

RUN chown -R www-data:www-data /app

USER www-data

EXPOSE 8000

CMD ["manage.py", "runserver", "0.0.0.0:8000"]
