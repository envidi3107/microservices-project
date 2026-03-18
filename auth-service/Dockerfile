FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir django djangorestframework psycopg2-binary PyJWT

EXPOSE 8000

CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
