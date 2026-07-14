import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """应用配置类"""
    SECRET_KEY = os.getenv('JWT_SECRET', 'dev-secret-key')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))

    # MySQL 数据库配置
    MYSQL_HOST = os.getenv('DB_HOST', 'localhost')
    MYSQL_PORT = os.getenv('DB_PORT', '3306')
    MYSQL_DATABASE = os.getenv('DB_NAME', 'agenthub')
    MYSQL_USER = os.getenv('DB_USER', 'root')
    MYSQL_PASSWORD = os.getenv('DB_PASSWORD', '')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('DEBUG', 'False') == 'True'
