FROM alpine:3.20

# Install Python and pip
RUN apk add --no-cache python3 py3-pip && \
    python3 -m ensurepip && \
    ln -sf python3 /usr/bin/python

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install setuptools==58.0.4 wheel
RUN pip --timeout=1000 install -r /requirements.txt

WORKDIR /app

COPY . /app

RUN addgroup -S www-data && adduser -S www-data -G www-data && \
    chown -R www-data:www-data /app

USER www-data

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
