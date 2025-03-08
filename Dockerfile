# Sử dụng Python 3.9 làm hình ảnh cơ sở
FROM python:3.9-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các thư viện phụ thuộc
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép tất cả mã nguồn vào container
COPY . .

# Đảm bảo thư mục instance tồn tại cho database SQLite
RUN mkdir -p instance

# Mở cổng 5000 để truy cập ứng dụng
EXPOSE 5000

# Thiết lập biến môi trường
ENV FLASK_ENV=production

# Lệnh khởi động ứng dụng
CMD ["python", "app.py"]