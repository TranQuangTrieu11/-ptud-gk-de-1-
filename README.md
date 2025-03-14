# Flask Blog

## Thông tin cá nhân
- **Họ tên:** Trần Quang Triều
- **Mã sinh viên:** 22002955

## Mô tả project
Flask Blog là một ứng dụng blog hoàn chỉnh được xây dựng bằng Python với framework Flask. Dự án này được phát triển nhằm mục đích tạo ra một nền tảng blog đơn giản nhưng đầy đủ tính năng, nơi người dùng có thể đăng ký, đăng nhập, tạo và quản lý các bài viết của mình.

### Các tính năng chính:
1. **Hệ thống người dùng**
   - Đăng ký và đăng nhập tài khoản
   - Phân quyền Admin/User
   - Admin có thể khóa tài khoản và đặt lại mật khẩu của người dùng
   - Người dùng có thể tự thay đổi mật khẩu của mình

2. **Quản lý bài viết**
   - Tạo, đọc, cập nhật, xóa bài viết
   - Hỗ trợ xóa hàng loạt bài viết
   - Phân trang hiển thị bài viết (5 bài/trang)

3. **Tương tác**
   - Hệ thống bình luận trên bài viết
   - Theo dõi bài viết yêu thích
   - Xem danh sách bài viết đã theo dõi
   - Hiển thị bài viết dạng thẻ (Card-based) với giao diện trực quan
   - Giao diện thân thiện người dùng

4. **Giao diện và trải nghiệm người dùng**
   - Thiết kế Card-Based hiện đại cho bài viết
   - Tích hợp biểu tượng Font Awesome để tăng tính trực quan
   - Giao diện tương thích với nhiều thiết bị (Responsive Design)
   - Xem trước ảnh khi tải lên

## Hướng dẫn cài đặt

1. Clone the repository:
   ```
   git clone https://github.com/TranQuangTrieu11/-ptud-gk-de-1.git
   cd ptud-gk-de-1
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open your web browser and go to `http://127.0.0.1:5000` to access the blog.

## Tài khoản mặc định

- **Admin:**
  - Username: admin
  - Password: admin123

## Quá trình phát triển
Ứng dụng đã trải qua 7 phiên bản phát triển:
- V1: Khởi tạo dự án, thiết lập cấu trúc
- V2: Tạo hệ thống đăng nhập/đăng ký
- V3: Thêm tính năng admin quản lý người dùng
- V4: Thêm tính năng xóa hàng loạt bài viết
- V5: Thêm tính năng phân trang
- V6: Thêm chức năng theo dõi bài viết (Post Follow)
- V7: Cải tiến giao diện với thiết kế Card-Based

## Link triển khai
Ứng dụng đã được triển khai tại: https://github.com/TranQuangTrieu11/-ptud-gk-de-1.git

## Sử dụng Docker

### Phương pháp 1: Sử dụng docker-setup.bat
1. Chạy file docker-setup.bat

### Phương pháp 2: Sử dụng lệnh Docker thủ công
1. Xây dựng Docker image:
   ```
   docker-compose build
   ```
2. Khởi động container:
   ```
   docker-compose up -d
   ```
3. Truy cập ứng dụng tại `http://localhost:5000`

4. Dừng container:
   ```
   docker-compose down
   ```
