FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install django djangorestframework requests psycopg2-binary pika

EXPOSE 8000

CMD python manage.py makemigrations && \
    python manage.py migrate && \
    python seed.py && \
    python manage.py runserver 0.0.0.0:8000
