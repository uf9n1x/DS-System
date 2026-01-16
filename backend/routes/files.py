"""文件共享相关路由
"""

import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..extensions import db
from ..models.file import File
from ..models.user import User
from ..utils.file import save_file, delete_file, allowed_file
from ..config import UPLOAD_FOLDER

# 创建蓝图
bp = Blueprint('files', __name__, url_prefix='/api/files')

@bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def upload_file():
    """
    上传文件
    
    请求体：multipart/form-data格式，包含file字段
    
    返回：
    {"message": "文件上传成功", "files": [{"id": 1, "filename": "test.txt", "size": 1024}]}
    """
    try:
        # 获取当前用户ID
        current_user_id = int(get_jwt_identity())
        
        if 'file' not in request.files:
            return jsonify({'error': '没有文件被上传'}), 400
        
        files = request.files.getlist('file')
        uploaded_files = []
        
        uploaded_files_data = []
        new_files = []
        
        # 获取共享状态参数
        is_shared = request.form.get('is_shared', 'false').lower() == 'true'
        
        for file in files:
            if file.filename == '':
                continue
            
            if allowed_file(file.filename):
                # 保存文件
                filename, filepath = save_file(file)
                # 获取文件大小 - 将相对路径转换为绝对路径
                absolute_filepath = os.path.join(UPLOAD_FOLDER, filepath)
                file_size = os.path.getsize(absolute_filepath)
                
                # 创建文件记录
                new_file = File(
                    filename=filename,
                    filepath=filepath,
                    size=file_size,
                    user_id=current_user_id,
                    is_shared=is_shared
                )
                
                new_files.append(new_file)
                db.session.add(new_file)
                uploaded_files_data.append({
                    'filename': filename,
                    'size': file_size
                })
        
        db.session.commit()
        
        # 构建响应数据，此时可以获取到数据库生成的ID和时间
        uploaded_files = []
        for i, new_file in enumerate(new_files):
            uploaded_files.append({
                'id': new_file.id,
                'filename': new_file.filename,
                'size': new_file.size,
                'is_shared': new_file.is_shared,
                'created_at': new_file.created_at.isoformat()
            })
        
        return jsonify({
            'message': '文件上传成功',
            'files': uploaded_files
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_files():
    """
    获取文件列表
    
    查询参数：
    - shared: 是否只获取共享文件（可选）
    - all: 是否获取所有用户的文件（仅管理员可用）
    
    返回：
    {"message": "获取文件列表成功", "files": [{"id": 1, "filename": "test.txt", "size": 1024}]}
    """
    try:
        # 获取当前用户ID和角色
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # 获取查询参数
        shared_param = request.args.get('shared')
        all_param = request.args.get('all')
        
        # 查询文件列表
        if shared_param and shared_param.lower() == 'true':
            # 获取共享文件（所有用户的共享文件）
            files = File.query.filter(File.is_shared == True).all()
        elif all_param and all_param.lower() == 'true' and user.role == 'admin':
            # 管理员获取所有用户的文件
            files = File.query.all()
        else:
            # 获取当前用户的文件
            files = File.query.filter(File.user_id == current_user_id).all()
        
        # 转换为响应格式
        file_list = []
        for file in files:
            file_list.append({
                'id': file.id,
                'filename': file.filename,
                'size': file.size,
                'is_shared': file.is_shared,
                'created_at': file.created_at.isoformat(),
                'uploader': file.user.username
            })
        
        return jsonify({
            'message': '获取文件列表成功',
            'files': file_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:file_id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def download_file(file_id):
    """
    下载文件
    
    Args:
        file_id: 文件ID
    
    返回：
        文件下载响应
    """
    try:
        # 获取当前用户ID
        current_user_id = int(get_jwt_identity())
        
        # 查询文件
        file = File.query.get(file_id)
        if not file:
            return jsonify({'error': '文件不存在'}), 404
        
        # 检查权限：只有文件所有者或共享文件才能下载
        if file.user_id != current_user_id and not file.is_shared:
            return jsonify({'error': '没有权限下载该文件'}), 403
        
        # 处理文件路径：如果是绝对路径则直接使用，否则转换为相对路径
        if os.path.isabs(file.filepath):
            # 旧文件：使用绝对路径
            filename = os.path.basename(file.filepath)
            directory = os.path.dirname(file.filepath)
        else:
            # 新文件：使用相对路径，结合UPLOAD_FOLDER
            filename = file.filepath
            directory = UPLOAD_FOLDER
        
        # 发送文件
        return send_from_directory(directory, filename, as_attachment=True, download_name=file.filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:file_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_file_route(file_id):
    """
    删除文件
    
    Args:
        file_id: 文件ID
    
    返回：
    {"message": "文件删除成功"}
    """
    try:
        # 获取当前用户ID和角色
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # 查询文件
        file = File.query.get(file_id)
        if not file:
            return jsonify({'error': '文件不存在'}), 404
        
        # 检查权限：管理员可以删除所有文件，普通用户只能删除自己的文件
        if user.role != 'admin' and file.user_id != current_user_id:
            return jsonify({'error': '没有权限删除该文件'}), 403
        
        # 删除文件 - 处理绝对路径和相对路径
        if os.path.isabs(file.filepath):
            # 旧文件：使用绝对路径
            absolute_filepath = file.filepath
        else:
            # 新文件：使用相对路径，结合UPLOAD_FOLDER
            absolute_filepath = os.path.join(UPLOAD_FOLDER, file.filepath)
        
        if os.path.exists(absolute_filepath):
            os.remove(absolute_filepath)
        
        # 删除数据库记录
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({'message': '文件删除成功'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:file_id>/copy', methods=['POST'], strict_slashes=False)
@jwt_required()
def copy_shared_file(file_id):
    """
    复制共享文件到个人文件
    
    Args:
        file_id: 文件ID
    
    返回：
    {"message": "文件复制成功", "file": {"id": 1, "filename": "test.txt", "size": 1024}}
    """
    try:
        # 获取当前用户ID
        current_user_id = int(get_jwt_identity())
        
        # 查询文件
        file = File.query.get(file_id)
        if not file:
            return jsonify({'error': '文件不存在'}), 404
        
        # 检查权限：只有共享文件才能复制
        if not file.is_shared:
            return jsonify({'error': '只有共享文件才能复制'}), 403
        
        # 处理文件路径：获取原始文件的绝对路径
        if os.path.isabs(file.filepath):
            # 旧文件：使用绝对路径
            original_absolute_filepath = file.filepath
        else:
            # 新文件：使用相对路径，结合UPLOAD_FOLDER
            original_absolute_filepath = os.path.join(UPLOAD_FOLDER, file.filepath)
        
        # 检查原始文件是否存在
        if not os.path.exists(original_absolute_filepath):
            return jsonify({'error': '原始文件不存在'}), 404
        
        # 生成新的文件名和路径
        import shutil
        import uuid
        
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1]
        new_unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        new_absolute_filepath = os.path.join(UPLOAD_FOLDER, new_unique_filename)
        
        # 复制文件内容
        shutil.copy2(original_absolute_filepath, new_absolute_filepath)
        
        # 获取文件大小
        file_size = os.path.getsize(new_absolute_filepath)
        
        # 创建新的文件记录，属于当前用户且非共享
        new_file = File(
            filename=file.filename,  # 使用原始文件名
            filepath=new_unique_filename,  # 使用新的文件路径
            size=file_size,
            user_id=current_user_id,
            is_shared=False  # 非共享文件
        )
        
        # 保存到数据库
        db.session.add(new_file)
        db.session.commit()
        
        # 构建响应数据
        response_file = {
            'id': new_file.id,
            'filename': new_file.filename,
            'size': new_file.size,
            'is_shared': new_file.is_shared,
            'created_at': new_file.created_at.isoformat()
        }
        
        return jsonify({
            'message': '文件复制成功',
            'file': response_file
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:file_id>/share', methods=['PUT'], strict_slashes=False)
@jwt_required()
def share_file(file_id):
    """
    分享/取消分享文件
    
    请求体：
    {"is_shared": true}
    
    返回：
    {"message": "文件分享状态更新成功"}
    """
    try:
        # 获取当前用户ID和角色
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # 查询文件
        file = File.query.get(file_id)
        if not file:
            return jsonify({'error': '文件不存在'}), 404
        
        # 检查权限：管理员可以分享/取消分享所有文件，普通用户只能操作自己的文件
        if user.role != 'admin' and file.user_id != current_user_id:
            return jsonify({'error': '没有权限分享该文件'}), 403
        
        # 更新分享状态
        data = request.get_json()
        file.is_shared = data.get('is_shared', False)
        db.session.commit()
        
        return jsonify({
            'message': '文件分享状态更新成功',
            'is_shared': file.is_shared
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:file_id>/rename', methods=['PUT'], strict_slashes=False)
@jwt_required()
def rename_file(file_id):
    """
    重命名文件
    
    请求体：
    {"filename": "new_filename.txt"}
    
    返回：
    {"message": "文件重命名成功", "file": {"id": 1, "filename": "new_filename.txt"}}
    """
    try:
        # 获取当前用户ID和角色
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # 查询文件
        file = File.query.get(file_id)
        if not file:
            return jsonify({'error': '文件不存在'}), 404
        
        # 检查权限：管理员可以重命名所有文件，普通用户只能操作自己的文件
        if user.role != 'admin' and file.user_id != current_user_id:
            return jsonify({'error': '没有权限重命名该文件'}), 403
        
        # 获取新文件名
        data = request.get_json()
        new_filename = data.get('filename')
        
        if not new_filename or new_filename.strip() == '':
            return jsonify({'error': '文件名不能为空'}), 400
        
        # 更新文件名
        file.filename = new_filename
        db.session.commit()
        
        return jsonify({
            'message': '文件重命名成功',
            'file': {
                'id': file.id,
                'filename': file.filename,
                'is_shared': file.is_shared
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
