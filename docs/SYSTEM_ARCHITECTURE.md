# Tài Liệu Thiết Kế & Mô Tả Dự Án Hệ Thống Microservice Cửa Hàng Sách

Tài liệu này mô tả chi tiết hệ thống cửa hàng sách (Bookstore) được xây dựng theo kiến trúc Microservices. Mục tiêu cung cấp cái nhìn tổng quan về kiến trúc, công nghệ, danh sách API và các luồng chức năng (flow) cốt lõi của hệ thống.

---

## 1. Kiến Trúc Tổng Thể (Overall Architecture)
Hệ thống được thiết kế theo mô hình **Microservices Architecture (Kiến trúc Vi dịch vụ)** kết hợp với mẫu thiết kế **API Gateway Pattern (Cổng giao tiếp API)** và **Database-per-service (Cơ sở dữ liệu độc lập cho từng dịch vụ)**.

- **Frontend / Client**: Giao diện người dùng được render trực tiếp tại `api-gateway` sử dụng **Django Templates** thay vì xây dựng ứng dụng SPA (Single Page Application) độc lập.
- **API Gateway**: Đóng vai trò là cổng vào trung tâm duy nhất, tiếp nhận yêu cầu từ người dùng (HTTP requests) sau đó định tuyến và gọi sang các dịch vụ backend thích hợp.
- **Backend Services**: Các dịch vụ độc lập hoạt động, đóng gói nghiệp vụ riêng biệt:
  - `book-service`: Quản lý danh mục sách (sản phẩm).
  - `customer-service`: Quản lý thông tin khách hàng (người dùng).
  - `cart-service`: Quản lý giỏ hàng của từng khách hàng.
  - `order-service`: Quản lý đơn hàng và orchestration luồng checkout.
  - `pay-service`: Xử lý giao dịch thanh toán.
  - `ship-service`: Quản lý thông tin vận chuyển.
  - `comment-rate-service`: Quản lý đánh giá và bình luận về sách.
  - Các service khác như `staff-service`, `manager-service`, `catalog-service`, `recommender-ai-service`.
- **Database**: Mỗi Service sở hữu một database riêng, không sử dụng chung db để giảm sự phụ thuộc và lỏng lẻo trong kết nối (loose coupling).

---

## 2. Công Nghệ Sử Dụng (Technology Stack)
- **Ngôn ngữ lập trình**: Python 3
- **Web Framework (Backend)**: Django, Django REST Framework (DRF)
- **Web Framework (Frontend)**: Django Templates (HTML/CSS thuần kết hợp biến template của Django)
- **Cơ sở dữ liệu**: PostgreSQL 15 (Sử dụng 11 container database riêng biệt cho từng service tương ứng)
- **Giao tiếp nội bộ (Inter-service Communication)**: RESTful API (Giao tiếp đồng bộ thông qua thư viện `requests` qua HTTP/JSON).
- **Môi trường & Triển khai**: Docker & Docker Compose (Quản lý toàn bộ 22 container của dự án).

---

## 3. Tài Liệu API Tính Năng Các Service (API Documentation)
Mỗi service nội bộ cung cấp REST API chuẩn cho API Gateway và các Service khác gọi:

### 3.1. `book-service` (Port 8002)
- `GET /books/`: Lấy danh sách toàn bộ sách.
- `POST /books/`: Tạo mới một cuốn sách (Yêu cầu: `title`, `author`, `price`, `stock`).
- `GET /books/{id}/`: Lấy thông tin sách cụ thể.
- `PUT /books/{id}/`: Cập nhật sách.
- `DELETE /books/{id}/`: Xóa sách.

### 3.2. `customer-service` (Port 8001)
- `GET /`: Lấy danh sách khách hàng.
- `POST /`: Đăng ký khách hàng mới (Yêu cầu: `name`, `email`). Service này sẽ đồng thời gọi HTTP POST tới `cart-service` để khởi tạo giỏ hàng.

### 3.3. `cart-service` (Port 8003)
- `GET /carts/{customer_id}/`: Lấy chi tiết giỏ hàng và danh sách sản phẩm trong giỏ của khách.
- `POST /carts/`: Khởi tạo giỏ hàng cho `customer_id`.
- `POST /carts/items/`: Thêm sách vào giỏ (Yêu cầu: `cart_id`, `book_id`, `quantity`). Giới hạn kiểm tra sách có tồn tại qua việc bắt HTTP GET tới `book-service`.
- `PUT /carts/items/{item_id}/`: Cập nhật số lượng sách trong giỏ (`quantity`).
- `DELETE /carts/items/{item_id}/`: Xóa một món đồ khỏi giỏ hàng.

### 3.4. `order-service` (Port 8007)
- `GET /orders/`: Lấy danh sách đơn hàng.
- `POST /orders/`: Tạo một đơn hàng mới (Yêu cầu: `customer_id`, `total_price`, `address`, `payment_method`, `shipping_method`).

### 3.5. `pay-service` (Port 8009)
- `POST /payments/`: Tạo thanh toán mới (Yêu cầu: `order_id`, `amount`, `status`).

### 3.6. `ship-service` (Port 8008)
- `POST /shipments/`: Tạo đơn vận chuyển (Yêu cầu: `order_id`, `address`, `status`).

### 3.7. `comment-rate-service` (Port 8010)
- `GET /reviews/`: Lấy toàn bộ đánh giá (API Gateway sẽ tự filter theo `book_id`).
- `POST /reviews/`: Gửi đánh giá sách (Yêu cầu: `book_id`, `customer_id`, `rating` (1-5), `comment`).

---

## 4. Luồng (Flow) Các Tính Năng Hệ Thống

Dưới đây mô tả trình tự tương tác (Flow) khi người dùng (Actor) thao tác trên Frontend (API Gateway):

### 4.1. Luồng #1: Đăng Ký Khách Hàng (Tự động khởi tạo giỏ hàng)
1. **Người dùng** nhập Name, Email tại trang `/register/` trên API Gateway.
2. **API Gateway** gửi request `POST /` tới `customer-service`.
3. `customer-service` lưu khách hàng mới vào DB (`postgres-customer`).
4. **`customer-service`** tự động gọi request đồng bộ `POST /carts/` truyền lên `customer_id` sang cho `cart-service`.
5. `cart-service` tạo một `Cart` trống trong DB (`postgres-cart`) và trả về `cart_id`.
6. API Gateway thông báo đăng ký thành công cho Người dùng.

### 4.2. Luồng #2: Quản Lý Sách (Staff)
1. **Nhân viên (Staff)** truy cập trang `/staff/books/` trên API Gateway.
2. Để **Hiển thị sách**, API Gateway gọi `GET /books/` từ `book-service` và render bảng điều khiển.
3. Để **Thêm mới**, nhân viên nhập form, API Gateway gọi `POST /books/` với payload JSON.
4. Để **Xóa sách**, nhân viên chọn Delete, API Gateway gọi DELETE tới `book-service`.

### 4.3. Luồng #3: Giỏ Hàng (Thêm, Xem, Cập nhật, Xóa)
- **Thêm vào giỏ**:
  1. KH bấm nút "Add to Cart" của 1 cuốn sách.
  2. API Gateway gọi `POST /carts/` để đảm bảo KH có ID sẵn giỏ hàng. 
  3. Sau đó API Gateway gọi `POST /carts/items/` truyền lên (`book_id`, `quantity` = 1) tới `cart-service`.
  4. `cart-service` gọi sang `book-service` để validate mã `book_id`, nếu đúng thì thêm Record vào csdl.
- **Xem giỏ hàng**:
  1. API Gateway gọi `GET /carts/{id}/` từ `cart-service`.
  2. Gateway lấy mảng các Item, bóc tách `book_id` và gọi tiếp sang `book-service` (`GET /books/`) lấy chi tiết Tiêu đề, Giá, Tác giả rổi tự động ráp (enrich) lại thành JSON cuối cùng để hiển thị cho UI.
- **Cập nhật / Xóa items**:
  1. KH thay đổi số lượng hoặc chọn Remove.
  2. API Gateway gửi `PUT /carts/items/{item_id}/` (Để update quantity) hoặc `DELETE /carts/items/{item_id}/` (Để gỡ bỏ khỏi giỏ).

### 4.4. Luồng #4: Checkout (Tạo Đơn -> Kích hoạt Thanh toán & Vận chuyển)
1. KH bấm "Checkout" từ giỏ hàng, chọn giao hàng (`Standard`/`Express`) và phương thức thanh toán.
2. API Gateway tính toán tổng tiền (`total_price`) qua thông tin lấy từ `cart-service` và `book-service`.
3. API Gateway gọi `POST /orders/` sang **`order-service`**.
4. **`order-service`** thực thi luồng *Orchestration* (Giao dịch liên dịch vụ):
   - Bước 1: Lưu Order vào CSDL (Trạng thái: "Placed").
   - Bước 2: Gọi đồng bộ sang `pay-service` (`POST /payments/`) truyền `order_id` và số tiền để thiết lập record thanh toán.
   - Bước 3: Gọi đồng bộ sang `ship-service` (`POST /shipments/`) truyền địa chỉ người mua, `order_id` để thiết lập lộ trình giao hàng ban đầu ("Pending").
5. API Gateway thông báo đặt hàng thành công tới trình duyệt của KH.

### 4.5. Luồng #5: Đánh Giá Sách (Rating & Comment)
1. Khách hàng xem chi tiết sách `/books/{id}/`.
2. API Gateway gọi `GET /books/{id}/` tới `book-service` lấy thông tin chung của sách.
3. API Gateway gọi `GET /reviews/` tới `comment-rate-service` và lọc ra các đánh giá trỏ tới sách hiện tại để hiển thị.
4. KH nhập số sao đánh giá (1-5) và thông điệp.
5. API Gateway tạo request `POST /reviews/` tới `comment-rate-service` để lưu thông tin. Trang được reload lại hiển thị kèm bình luận hệ thống mới tạo.
