"""
数据共享模块模型
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from ..extensions import db

class TableMetadata(db.Model):
    """数据表元数据模型"""
    __tablename__ = 'table_metadata'
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def __repr__(self):
        return f"<TableMetadata {self.table_name} ({self.display_name})>"

class TableAccess(db.Model):
    """用户数据表访问权限模型"""
    __tablename__ = 'table_access'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    table_name = Column(String(100), nullable=False)
    can_view = Column(Boolean, default=True, nullable=False)
    can_edit = Column(Boolean, default=False, nullable=False)
    can_export = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # 关系
    user = db.relationship('User', backref=db.backref('table_accesses', lazy=True, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f"<TableAccess User:{self.user_id} Table:{self.table_name} View:{self.can_view} Edit:{self.can_edit} Export:{self.can_export}>"
