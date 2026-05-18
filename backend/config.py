"""
数据库配置文件
- 开发环境使用 SQLite（零配置）
- 生产环境切换到 MySQL，修改 SQLALCHEMY_DATABASE_URI 即可
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'yaoqixie-secret-key-2026-change-in-production')

    # =============================================
    # 数据库配置
    # =============================================
    # --- 开发环境 (SQLite) ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "yaoqixie.db")}'
    )

    # --- 生产环境 (MySQL) ---
    # 取消下面注释并注释上面一行即可切换到 MySQL
    # SQLALCHEMY_DATABASE_URI = os.environ.get(
    #     'DATABASE_URL',
    #     'mysql+pymysql://username:password@localhost:3306/yaoqixie?charset=utf8mb4'
    # )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # 文件上传
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # 生产环境应设为 True
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 7  # 7天
