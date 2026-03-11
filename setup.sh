#!/bin/bash
echo "======================================"
echo " BookStore Microservices - Setup (Mac/Linux)"
echo "======================================"

echo ""
echo "[1/4] Setting up book-service..."
cd book-service
python3 -m venv venv
source venv/bin/activate
pip install django djangorestframework requests psycopg2-binary
deactivate
cd ..

echo ""
echo "[2/4] Setting up cart-service..."
cd cart-service
python3 -m venv venv
source venv/bin/activate
pip install django djangorestframework requests psycopg2-binary
deactivate
cd ..

echo ""
echo "[3/4] Setting up customer-service..."
cd customer-service
python3 -m venv venv
source venv/bin/activate
pip install django djangorestframework requests psycopg2-binary
deactivate
cd ..

echo ""
echo "[4/4] Setting up api-gateway..."
cd api-gateway
python3 -m venv venv
source venv/bin/activate
pip install django djangorestframework requests
deactivate
cd ..

echo ""
echo "======================================"
echo " Setup complete!"
echo " Run with Docker: docker-compose up --build"
echo "======================================"
