"""
Gunicorn 启动入口
通过该文件启动生产环境的 Flask 应用
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
