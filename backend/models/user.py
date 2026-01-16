"""
用户模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from ..extensions import db

class User(db.Model):
    """用户表模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    role = Column(Enum('admin', 'user'), default='user', nullable=False)
    status = Column(Enum('online', 'offline'), default='offline', nullable=False)
    jwt_token_identifier = Column(String(255), nullable=True)  # 存储当前有效的令牌标识符
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    files = db.relationship('File', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
