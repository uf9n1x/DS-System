"""
扩展管理文件
用于集中管理所有Flask扩展实例，避免循环导入问题
"""

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

# 创建扩展实例
cors = CORS()
jwt = JWTManager()

# 主数据库连接（系统库）
db = SQLAlchemy()

# 数据共享数据库连接
datashare_db = SQLAlchemy()

