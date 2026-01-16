"""
认证相关路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..extensions import db
from ..models.user import User
from ..utils.auth import hash_password, verify_password, create_jwt_token

# 创建蓝图
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'], strict_slashes=False)
def register():
    """
    用户注册
    
    请求体：
    {"username": "test", "password": "123456", "email": "test@example.com"}
    
    返回：
    {"message": "注册成功", "user": {"id": 1, "username": "test", "email": "test@example.com"}}
    """
    try:
        data = request.get_json()
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if data.get('email') and User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已存在'}), 400
        
        # 创建新用户
        new_user = User(
            username=data['username'],
            password_hash=hash_password(data['password']),
            email=data.get('email')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': '注册成功',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'role': new_user.role
            }
        }), 201
        
    except KeyError as e:
        return jsonify({'error': f'缺少必要字段: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'], strict_slashes=False)
def login():
    """
    用户登录
    
    请求体：
    {"username": "test", "password": "123456"}
    
    返回：
    {"access_token": "jwt_token", "user": {"id": 1, "username": "test", "role": "user"}}
    """
    try:
        data = request.get_json()
        
        # 查找用户
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not verify_password(user.password_hash, data['password']):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 创建JWT令牌和唯一标识符
        access_token, token_identifier = create_jwt_token(user.id)
        
        # 更新用户状态为在线，并存储令牌标识符
        user.status = 'online'
        user.jwt_token_identifier = token_identifier
        db.session.commit()
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'status': user.status
            }
        }), 200
        
    except KeyError as e:
        return jsonify({'error': f'缺少必要字段: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/logout', methods=['POST'], strict_slashes=False)
@jwt_required()
def logout():
    """
    用户登出
    
    返回：
    {"message": "登出成功"}
    """
    try:
        # 获取当前用户ID
        current_user_id = int(get_jwt_identity())  # 将字符串转换为整数
        
        # 更新用户状态为离线，并清除令牌标识符
        user = User.query.get(current_user_id)
        if user:
            user.status = 'offline'
            user.jwt_token_identifier = None
            db.session.commit()
        
        return jsonify({'message': '登出成功'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/me', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_current_user():
    """
    获取当前登录用户信息
    
    返回：
    {"user": {"id": 1, "username": "test", "role": "user"}}
    """
    try:
        # 获取当前用户ID
        current_user_id = int(get_jwt_identity())  # 将字符串转换为整数
        
        # 查询用户信息
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'status': user.status
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
