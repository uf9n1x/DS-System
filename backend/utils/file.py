"""
文件处理工具函数
"""

import os
import uuid
from werkzeug.utils import secure_filename
from ..config import UPLOAD_FOLDER

def allowed_file(filename):
    """
    检查文件是否允许上传
    
    Args:
        filename: 文件名
    
    Returns:
        bool: 文件是否允许上传
    """
    # 允许的文件类型
    ALLOWED_EXTENSIONS = {
        # 文档
        'txt', 'doc', 'docx', 'pdf', 'xls', 'xlsx', 'ppt', 'pptx',
        # 图像
        'jpg', 'jpeg', 'png', 'gif', 'webp',
        # 音频
        'mp3', 'wav', 'ogg',
        # 视频
        'mp4', 'avi', 'mov',
        # 压缩文件
        'zip', 'rar', '7z', 'tar', 'gz',
        # 代码文件
        'py', 'js', 'html', 'css', 'json', 'xml', 'md'
    }
    
    # 检查文件扩展名
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """
    保存上传的文件
    
    Args:
        file: 上传的文件对象
    
    Returns:
        tuple: (原始文件名, 相对文件路径)
    """
    # 确保上传目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # 保留原始文件名，用于显示和下载
    original_filename = file.filename
    
    # 生成唯一的文件存储名，使用secure_filename处理以避免存储问题
    file_ext = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # 保存文件
    absolute_filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(absolute_filepath)
    
    # 验证文件是否成功保存
    if not os.path.exists(absolute_filepath):
        raise Exception(f"文件保存失败: {absolute_filepath}")
    
    # 只返回相对路径（相对于UPLOAD_FOLDER）
    relative_filepath = unique_filename
    
    return original_filename, relative_filepath

def delete_file(filepath):
    """
    删除文件
    
    Args:
        filepath: 相对文件路径（相对于UPLOAD_FOLDER）
    
    Returns:
        bool: 文件是否删除成功
    """
    try:
        # 将相对路径转换为绝对路径
        absolute_filepath = os.path.join(UPLOAD_FOLDER, filepath)
        if os.path.exists(absolute_filepath):
            os.remove(absolute_filepath)
            return True
        return False
    except Exception as e:
        return False

def get_file_size(filepath):
    """
    获取文件大小
    
    Args:
        filepath: 相对文件路径（相对于UPLOAD_FOLDER）
    
    Returns:
        int: 文件大小（字节）
    """
    # 将相对路径转换为绝对路径
    absolute_filepath = os.path.join(UPLOAD_FOLDER, filepath)
    return os.path.getsize(absolute_filepath)

def cleanup_invalid_files():
    """
    清理数据库中不存在的文件记录
    
    Returns:
        int: 清理的无效记录数量
    """
    from ..models.file import File
    from ..extensions import db
    
    try:
        # 获取所有文件记录
        all_files = File.query.all()
        invalid_count = 0
        
        for file in all_files:
            # 构建文件的绝对路径
            if os.path.isabs(file.filepath):
                file_path = file.filepath
            else:
                file_path = os.path.join(UPLOAD_FOLDER, file.filepath)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                # 删除无效记录
                db.session.delete(file)
                invalid_count += 1
        
        # 提交更改
        if invalid_count > 0:
            db.session.commit()
        
        return invalid_count
    except Exception as e:
        # 发生错误时回滚
        db.session.rollback()
        return 0
