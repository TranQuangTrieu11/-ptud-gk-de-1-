import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # Lưu database trong thư mục instance để persistent data
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/blog.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False