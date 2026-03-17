# BookStore Microservices

Dự án demo hệ thống microservices xây dựng với **Django + PostgreSQL + Docker**.

## Kiến trúc

```
api-gateway  →  book-service    (port 8002)
             →  cart-service    (port 8003)
             →  customer-service(port 8001)
```

Mỗi service có database PostgreSQL riêng.

## Yêu cầu

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.10+ (để phát triển local)

---

## Chạy với Docker (khuyến nghị)

```bash
docker-compose up --build
```

- 📚 Danh sách sách: http://localhost:8000/books/
- 🛒 Giỏ hàng: http://localhost:8000/cart/1/

> Dữ liệu mẫu được tự động chèn khi khởi động lần đầu.

---

## Phát triển local (không Docker)

**Windows:**
```bat
setup.bat
```

**Mac / Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

Sau đó chạy từng service thủ công với venv tương ứng.

---

## Cấu trúc thư mục

```
bookstore-microservice/
│
├── api-gateway/         # Django gateway, templates, routing
├── book-service/        # Quản lý sách
├── cart-service/        # Quản lý giỏ hàng
├── customer-service/    # Quản lý khách hàng
│
├── docker-compose.yml
├── setup.bat            # Setup venv (Windows)
└── setup.sh             # Setup venv (Mac/Linux)
```


---

## Chạy với Kubernetes

```bash
kubectl apply -f k8s-manifest.yaml
```

// lấy danh sách các pod bao gồm cả ip của pod
kubectl get pods -o wide

// forward port của service
kubectl port-forward svc/api-gateway 8000:80


