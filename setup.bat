@echo off
echo ======================================
echo  BookStore Microservices - Setup (Windows)
echo ======================================

echo.
echo [1/12] Setting up book-service...
cd book-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [2/12] Setting up cart-service...
cd cart-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [3/12] Setting up customer-service...
cd customer-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [4/12] Setting up api-gateway...
cd api-gateway
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests
call venv\Scripts\deactivate
cd ..

echo.
echo [5/12] Setting up staff-service...
cd staff-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [6/12] Setting up manager-service...
cd manager-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [7/12] Setting up catalog-service...
cd catalog-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [8/12] Setting up order-service...
cd order-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [9/12] Setting up ship-service...
cd ship-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [10/12] Setting up pay-service...
cd pay-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [11/12] Setting up comment-rate-service...
cd comment-rate-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo [12/12] Setting up recommender-ai-service...
cd recommender-ai-service
python -m venv venv
call venv\Scripts\activate
pip install django djangorestframework requests psycopg2-binary
call venv\Scripts\deactivate
cd ..

echo.
echo ======================================
echo  Setup complete!
echo  Run with Docker: docker-compose up --build
echo ======================================
