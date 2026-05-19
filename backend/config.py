"""
数据库配置
- 开发环境使用 SQLite
- 生产环境通过环境变量 DATABASE_URL 切换到 MySQL
"""
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'yaoqixie-prod-secret-key-change-me')

    # JWT 配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'yaoqixie-jwt-secret-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)  # 7天有效

    # =============================================
    # 数据库配置
    # =============================================
    # 优先读取环境变量（生产环境MySQL），否则使用SQLite（开发环境）
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "yaoqixie.db")}'
    )
    # MySQL 生产配置示例（通过环境变量设置）:
    # mysql+pymysql://yaoqixie:password@182.92.240.192:3306/yaoqixie?charset=utf8mb4

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # CORS 允许的前端域名
    CORS_ORIGINS = os.environ.get(
        'CORS_ORIGINS',
        'http://localhost:5500,http://127.0.0.1:5500,https://yaoqixie.github.io'
    )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
