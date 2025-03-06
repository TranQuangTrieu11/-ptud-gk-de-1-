# Flask Blog

Đây là một ứng dụng blog web đơn giản được xây dựng bằng Flask. Nó cho phép người dùng đăng ký, đăng nhập, tạo và xem các bài đăng trên blog.

## Project Structure

```
flask-blog
├── app.py               # Main entry point of the application
├── config.py            # Configuration settings
├── models.py            # Data models for the application
├── requirements.txt     # Project dependencies
├── static               # Static files (CSS, JS)
│   ├── css
│   │   └── style.css    # Styles for the application
│   └── js
│       └── main.js      # JavaScript for client-side functionality
├── templates            # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Homepage
│   ├── login.html       # Login form
│   ├── post.html        # Single blog post
│   └── register.html    # Registration form
└── README.md            # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd flask-tiny-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and go to `http://127.0.0.1:5000` to access the blog.

## Admin Access

1. Đăng nhập với tài khoản admin mặc định:
   - Username: admin
   - Password: admin123

2. Sau khi đăng nhập, bạn sẽ thấy liên kết "Admin Panel" trong thanh điều hướng
3. Hoặc truy cập trực tiếp: http://127.0.0.1:5000/admin

## Features

- User registration and authentication
- Create, read, update, and delete blog posts
- Responsive design with CSS
- Client-side interactivity with JavaScript

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.