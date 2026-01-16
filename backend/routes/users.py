"""
用户管理相关路由
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from backend.extensions import db
from backend.models.user import User
from backend.utils.auth import hash_password

# 创建蓝图
bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_users():
    """
    获取用户列表（管理员）
    
    返回：
    {"message": "获取用户列表成功", "users": [{"id": 1, "username": "test", "role": "user"}]}
    """
    try:
        # 检查当前用户是否为管理员
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin':
            return jsonify({'error': '只有管理员可以查看用户列表'}), 403
        
        # 获取用户列表
        users = User.query.all()
        user_list = []
        
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'status': user.status,
                'created_at': user.created_at.isoformat()
            })
        
        return jsonify({
            'message': '获取用户列表成功',
            'users': user_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_user():
    """
    创建用户（管理员）
    
    请求体：
    {"username": "test", "password": "123456", "email": "test@example.com", "role": "user"}
    
    返回：
    {"message": "创建用户成功", "user": {"id": 1, "username": "test"}}
    """
    try:
        # 检查当前用户是否为管理员
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin':
            return jsonify({'error': '只有管理员可以创建用户'}), 403
        
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
            email=data.get('email'),
            role=data.get('role', 'user')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': '创建用户成功',
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

@bp.route('/<int:user_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_user(user_id):
    """
    获取用户信息（管理员）
    
    返回：
    {"user": {"id": 1, "username": "test", "role": "user"}}
    """
    try:
        # 检查当前用户是否为管理员
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin' and current_user.id != user_id:
            return jsonify({'error': '只有管理员或本人可以查看用户信息'}), 403
        
        # 获取用户信息
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'status': user.status,
                'created_at': user.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:user_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_user(user_id):
    """
    更新用户信息（管理员）
    
    请求体：
    {"email": "test@example.com", "role": "admin"}
    
    返回：
    {"message": "更新用户信息成功", "user": {"id": 1, "username": "test"}}
    """
    try:
        # 检查当前用户是否为管理员
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin' and current_user.id != user_id:
            return jsonify({'error': '只有管理员或本人可以更新用户信息'}), 403
        
        # 获取用户信息
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.get_json()
        
        # 更新用户信息
        if 'email' in data:
            user.email = data['email']
        
        # 只有管理员可以更新角色
        if 'role' in data and current_user.role == 'admin':
            user.role = data['role']
        
        # 更新密码
        if 'password' in data:
            user.password_hash = hash_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': '更新用户信息成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:user_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_user(user_id):
    """
    删除用户（管理员）
    
    返回：
    {"message": "删除用户成功"}
    """
    try:
        # 检查当前用户是否为管理员
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if current_user.role != 'admin':
            return jsonify({'error': '只有管理员可以删除用户'}), 403
        
        # 不能删除自己
        if current_user.id == user_id:
            return jsonify({'error': '不能删除自己'}), 400
        
        # 获取用户信息
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': '删除用户成功'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
