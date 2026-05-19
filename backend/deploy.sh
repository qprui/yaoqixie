#!/bin/bash
# ============================================
# 肴柒蟹 后端部署脚本 (Ubuntu/CentOS)
# 阿里云服务器: 182.92.240.192
# ============================================
set -e

echo "🦀 肴柒蟹 后端部署开始..."

# 1. 系统更新
sudo apt update && sudo apt upgrade -y

# 2. 安装 Python3 + pip + venv (如果没有)
sudo apt install -y python3 python3-pip python3-venv nginx

# 3. 创建项目目录
sudo mkdir -p /opt/yaoqixie
sudo chown -R $USER:$USER /opt/yaoqixie

# 4. 上传后端代码 (需要先在本地打包上传，或使用 git clone)
# 假设已经把 backend/ 目录的内容上传到了 /opt/yaoqixie/
cd /opt/yaoqixie

# 5. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 6. 安装依赖
pip install -r requirements.txt

# 7. 配置环境变量 (请修改密码!)
export SECRET_KEY="your-random-secret-key-change-me"
export JWT_SECRET_KEY="your-jwt-secret-key-change-me"
export CORS_ORIGINS="http://localhost:5500,https://yaoqixie.github.io"
# 使用 MySQL (可选): 
# export DATABASE_URL="mysql+pymysql://yaoqixie:password@localhost:3306/yaoqixie?charset=utf8mb4"

# 8. 使用 SQLite 初始化数据库
python -c "from wsgi import app; print('数据库初始化完成')"

# 9. 测试启动
echo "测试启动... (按 Ctrl+C 停止)"
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

echo "✅ 部署完成！"
echo "📝 请继续完成 Nginx 配置 (见下方说明)"
