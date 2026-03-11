@echo off
echo ======================================
echo  BookStore Microservices - Setup (Windows)
echo ======================================

echo.
echo [1/4] Setting up book-service...
cd book-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [2/4] Setting up cart-service...
cd cart-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [3/4] Setting up customer-service...
cd customer-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [4/4] Setting up api-gateway...
cd api-gateway
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests
call venv\Scripts\deactivate
cd ..

echo.
echo ======================================
echo  Setup complete!
echo  Run with Docker: docker-compose up --build
echo ======================================
