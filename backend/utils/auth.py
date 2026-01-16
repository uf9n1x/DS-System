"""
认证工具函数
"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity
from functools import wraps
from flask import jsonify
from datetime import timedelta
from ..config import JWT_ACCESS_TOKEN_EXPIRES
from ..models.user import User
from ..models.data_share import TableAccess
from ..extensions import db

def hash_password(password):
    """
    对密码进行哈希处理
    
    Args:
        password: 原始密码
    
    Returns:
        哈希后的密码
    """
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """
    验证密码是否匹配
    
    Args:
        password_hash: 哈希后的密码
        password: 原始密码
    
    Returns:
        bool: 密码是否匹配
    """
    return check_password_hash(password_hash, password)

def create_jwt_token(user_id):
    """
    创建JWT访问令牌
    
    Args:
        user_id: 用户ID
    
    Returns:
        tuple: (JWT访问令牌, 唯一的令牌标识符)
    """
    import uuid
    # 生成唯一的令牌标识符
    token_identifier = str(uuid.uuid4())
    
    # 创建带有额外声明的JWT令牌
    access_token = create_access_token(
        identity=str(user_id),  # 确保user_id是字符串类型
        expires_delta=timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES),
        additional_claims={
            'token_identifier': token_identifier  # 添加令牌标识符到JWT声明中
        }
    )
    
    return access_token, token_identifier


def check_table_access(table_name, required_permission='view'):
    """
    检查用户对表格的访问权限
    
    Args:
        table_name: 表格名称
        required_permission: 所需权限，可选值为'view'、'edit'、'export'
    
    Returns:
        function: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取当前用户ID
            current_user_id = int(get_jwt_identity())
            user = User.query.get(current_user_id)
            
            # 管理员直接通过
            if user.role == 'admin':
                return func(*args, **kwargs)
            
            # 检查用户权限
            table_access = TableAccess.query.filter_by(
                user_id=current_user_id,
                table_name=table_name
            ).first()
            
            if not table_access:
                return jsonify({'error': '没有访问该表格的权限'}), 403
            
            # 检查具体权限
            if required_permission == 'view' and not table_access.can_view:
                return jsonify({'error': '没有查看该表格的权限'}), 403
            elif required_permission == 'edit' and not table_access.can_edit:
                return jsonify({'error': '没有编辑该表格的权限'}), 403
            elif required_permission == 'export' and not table_access.can_export:
                return jsonify({'error': '没有导出该表格的权限'}), 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
