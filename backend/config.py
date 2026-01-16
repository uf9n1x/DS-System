"""
配置文件，包含数据库连接信息等配置
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DB_NAME', 'webtools')
}

# 数据共享数据库配置
DATASHARE_DB_CONFIG = {
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'database': os.getenv('DATASHARE_DB_NAME', 'datashare')
}

# 数据共享数据库绑定名称
DATASHARE_DB_BIND = os.getenv('DATASHARE_DB_BIND', 'datashare')

# JWT配置
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'a-very-secure-jwt-secret-key-1234567890')  # 生产环境应使用更安全的密钥
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))  # 访问令牌过期时间，单位：秒

# 文件上传配置
# 设置为backend目录下的uploads文件夹
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(os.path.dirname(__file__), 'uploads'))
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '100')) * 1024 * 1024  # 100MB

# Flask配置
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'your-flask-secret-key')
