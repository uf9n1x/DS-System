"""
数据共享模块路由
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from io import BytesIO
import os
from ..extensions import db
from ..models.user import User
from ..models.data_share import TableMetadata, TableAccess
from ..utils.data_utils import (
    get_table_data, get_table_columns, export_table_data, 
    check_table_exists, get_all_tables, import_table_from_file,
    create_table_from_sql, insert_table_row, update_table_row,
    delete_table_row, delete_table, global_search
)
from ..utils.auth import check_table_access

# 创建蓝图
bp = Blueprint('data', __name__, url_prefix='/api/data')


@bp.route('/admin/search', methods=['GET'], strict_slashes=False)
@jwt_required()
def admin_global_search():
    """
    管理员全局搜索所有表格内容
    
    参数：
    search: 搜索关键词
    
    返回：
    {"message": "搜索成功", "results": [{"table_name": "users", "display_name": "用户表", "rows": [{"id": 1, "matched_data": {"username": "admin"}}]}]}
    """
    try:
        print("=== 管理员全局搜索请求开始 ===")
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            print("无权限访问该接口")
            return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 获取搜索关键词
        search_query = request.args.get('search', '')
        print(f"搜索关键词: {search_query}")
        
        # 执行全局搜索（搜索所有表格）
        results = global_search(search_query)
        print(f"搜索结果数量: {len(results)}")
        
        return jsonify({
            'message': '搜索成功',
            'results': results
        }), 200
    except Exception as e:
        import traceback
        error_msg = f"Error in admin_global_search: {str(e)}"
        traceback_str = traceback.format_exc()
        print(f"Error: {error_msg}")
        print(f"Traceback: {traceback_str}")
        return jsonify({'error': error_msg, 'traceback': traceback_str}), 500
    finally:
        print("=== 管理员全局搜索请求结束 ===")


@bp.route('/search', methods=['GET'], strict_slashes=False)
@jwt_required()
def user_global_search():
    """
    普通用户全局搜索其可访问的表格内容
    
    参数：
    search: 搜索关键词
    
    返回：
    {"message": "搜索成功", "results": [{"table_name": "users", "display_name": "用户表", "rows": [{"id": 1, "matched_data": {"username": "admin"}}]}]}
    """
    try:
        print("=== 用户全局搜索请求开始 ===")
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # 获取搜索关键词
        search_query = request.args.get('search', '')
        print(f"搜索关键词: {search_query}")
        
        # 获取用户可访问的表格列表
        if user.role == 'admin':
            # 管理员可以访问所有表格
            user_tables = get_all_tables()
        else:
            # 普通用户只能访问其有查看权限的表格
            table_accesses = TableAccess.query.filter_by(user_id=current_user_id, can_view=True).all()
            user_tables = [access.table_name for access in table_accesses]
        
        print(f"用户可访问的表格数量: {len(user_tables)}")
        
        # 执行全局搜索（仅搜索用户可访问的表格）
        results = global_search(search_query, tables_to_search=user_tables)
        print(f"搜索结果数量: {len(results)}")
        
        return jsonify({
            'message': '搜索成功',
            'results': results
        }), 200
    except Exception as e:
        import traceback
        error_msg = f"Error in user_global_search: {str(e)}"
        traceback_str = traceback.format_exc()
        print(f"Error: {error_msg}")
        print(f"Traceback: {traceback_str}")
        return jsonify({'error': error_msg, 'traceback': traceback_str}), 500
    finally:
        print("=== 用户全局搜索请求结束 ===")
@bp.route('/tables', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_accessible_tables():
    """
    获取用户可访问的表格列表
    
    返回：
    {"message": "获取表格列表成功", "tables": [{"id": 1, "table_name": "users", "display_name": "用户表", "description": "系统用户信息"}]}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role == 'admin':
            # 管理员可以访问所有活跃的表格
            tables = TableMetadata.query.filter_by(is_active=True).all()
        else:
            # 普通用户只能访问被授权的表格
            table_accesses = TableAccess.query.filter_by(user_id=current_user_id, can_view=True).all()
            table_names = [access.table_name for access in table_accesses]
            tables = TableMetadata.query.filter(TableMetadata.table_name.in_(table_names) & TableMetadata.is_active==True).all()
        
        # 转换为响应格式
        table_list = []
        for table in tables:
            table_list.append({
                'id': table.id,
                'table_name': table.table_name,
                'display_name': table.display_name,
                'description': table.description,
                'created_at': table.created_at.isoformat(),
                'updated_at': table.updated_at.isoformat()
            })
        
        return jsonify({
            'message': '获取表格列表成功',
            'tables': table_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/tables/<string:table_name>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_table_metadata(table_name):
    """
    获取表格元数据
    
    参数：
    table_name: 表格名称
    
    返回：
    {"message": "获取表格元数据成功", "table": {"table_name": "users", "display_name": "用户表", "description": "系统用户信息", "columns": [{"name": "id", "type": "int"}]}}
    """
    try:
        print(f"Debug: get_table_metadata called with table_name: '{table_name}'")
        
        # 检查表格是否存在
        exists = check_table_exists(table_name)
        print(f"Debug: Table {table_name} exists: {exists}")
        
        if not exists:
            return jsonify({'error': '表格不存在'}), 404
        
        # 检查用户权限
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        print(f"Debug: Current user: {user.username}, role: {user.role}")
        
        if user.role != 'admin':
            table_access = TableAccess.query.filter_by(
                user_id=current_user_id,
                table_name=table_name,
                can_view=True
            ).first()
            if not table_access:
                return jsonify({'error': '没有访问该表格的权限'}), 403
        
        # 获取表格元数据
        table_metadata = TableMetadata.query.filter_by(table_name=table_name).first()
        print(f"Debug: Table metadata found: {table_metadata}")
        
        if not table_metadata:
            # 如果元数据不存在，创建默认元数据
            table_metadata = TableMetadata(
                table_name=table_name,
                display_name=table_name.replace('_', ' ').title(),
                description=f"{table_name.replace('_', ' ').title()}表"
            )
            db.session.add(table_metadata)
            db.session.commit()
            print(f"Debug: Created table metadata: {table_metadata}")
        
        # 获取表格列信息
        print(f"Debug: Calling get_table_columns with table_name: '{table_name}'")
        columns = get_table_columns(table_name)
        print(f"Debug: Got columns: {columns}")
        
        # 获取用户对该表格的编辑权限
        can_edit = False
        if user.role == 'admin':
            can_edit = True
        else:
            table_access = TableAccess.query.filter_by(
                user_id=current_user_id,
                table_name=table_name,
                can_edit=True
            ).first()
            can_edit = bool(table_access)
        
        return jsonify({
            'message': '获取表格元数据成功',
            'table': {
                'id': table_metadata.id,
                'table_name': table_metadata.table_name,
                'display_name': table_metadata.display_name,
                'description': table_metadata.description,
                'columns': columns,
                'can_edit': can_edit,
                'created_at': table_metadata.created_at.isoformat(),
                'updated_at': table_metadata.updated_at.isoformat()
            }
        }), 200
    except Exception as e:
        import traceback
        error_msg = f"Error in get_table_metadata: {str(e)}"
        traceback_str = traceback.format_exc()
        print(f"Error: {error_msg}")
        print(f"Traceback: {traceback_str}")
        return jsonify({'error': error_msg, 'traceback': traceback_str}), 500


@bp.route('/tables/<string:table_name>/data', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_table_data_endpoint(table_name):
    """
    获取表格数据（支持排序、分页）
    
    参数：
    table_name: 表格名称
    page: 页码，默认为1
    per_page: 每页条数，默认为10
    sort_by: 排序字段，默认为None
    sort_order: 排序方向，默认为'asc'，可选值为'asc'或'desc'
    
    返回：
    {"message": "获取表格数据成功", "data": [{"id": 1, "username": "admin"}], "pagination": {"page": 1, "per_page": 10, "total": 1, "pages": 1}}
    """
    try:
        print(f"Debug: get_table_data_endpoint called with table_name: '{table_name}'")
        
        # 检查表格是否存在
        exists = check_table_exists(table_name)
        print(f"Debug: Table {table_name} exists: {exists}")
        
        if not exists:
            return jsonify({'error': '表格不存在'}), 404
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        sort_by = request.args.get('sort_by')
        sort_order = request.args.get('sort_order', 'asc')
        search_query = request.args.get('search')
        print(f"Debug: Query params - page: {page}, per_page: {per_page}, sort_by: {sort_by}, sort_order: {sort_order}, search: {search_query}")
        
        # 检查用户权限
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        print(f"Debug: Current user: {user.username}, role: {user.role}")
        
        if user.role != 'admin':
            table_access = TableAccess.query.filter_by(
                user_id=current_user_id,
                table_name=table_name,
                can_view=True
            ).first()
            if not table_access:
                return jsonify({'error': '没有访问该表格的权限'}), 403
        
        # 获取表格数据
        print(f"Debug: Calling get_table_data with table_name: '{table_name}'")
        result = get_table_data(table_name, page, per_page, sort_by, sort_order, search_query=search_query)
        print(f"Debug: Got table data result: {result}")
        
        return jsonify({
            'message': '获取表格数据成功',
            'data': result['data'],
            'pagination': result['pagination']
        }), 200
    except Exception as e:
        import traceback
        error_msg = f"Error in get_table_data_endpoint: {str(e)}"
        traceback_str = traceback.format_exc()
        print(f"Error: {error_msg}")
        print(f"Traceback: {traceback_str}")
        return jsonify({'error': error_msg, 'traceback': traceback_str}), 500


@bp.route('/tables/<string:table_name>/export', methods=['GET'], strict_slashes=False)
@jwt_required()
def export_table_data_endpoint(table_name):
    """
    导出表格数据
    
    参数：
    table_name: 表格名称
    format: 导出格式，默认为'csv'，可选值为'csv'或'excel'
    
    返回：
    文件下载响应
    """
    try:
        # 检查表格是否存在
        if not check_table_exists(table_name):
            return jsonify({'error': '表格不存在'}), 404
        
        # 获取导出格式
        export_format = request.args.get('format', 'csv')
        if export_format not in ['csv', 'excel']:
            return jsonify({'error': '不支持的导出格式'}), 400
        
        # 检查用户权限
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            table_access = TableAccess.query.filter_by(
                user_id=current_user_id,
                table_name=table_name,
                can_export=True
            ).first()
            if not table_access:
                return jsonify({'error': '没有导出该表格的权限'}), 403
        
        # 导出表格数据
        filename, content, content_type = export_table_data(table_name, export_format)
        
        # 返回文件下载响应
        return send_file(
            BytesIO(content.encode('utf-8') if isinstance(content, str) else content),
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/test-table/<string:table_name>', methods=['GET'])
def test_table(table_name):
    """测试表格访问功能，无需认证"""
    try:
        print(f"Debug: test_table called with table_name: '{table_name}'")
        
        # 清理表名
        if '.' in table_name:
            table_name = table_name.split('.')[-1]
            table_name = table_name.strip("'\"")
        
        # 检查表格是否存在
        print(f"Debug: Testing table existence for: '{table_name}'")
        exists = check_table_exists(table_name)
        print(f"Debug: Table '{table_name}' exists: {exists}")
        
        return jsonify({
            "table_name": table_name,
            "exists": exists,
            "message": f"表格 '{table_name}' {'存在' if exists else '不存在'}"
        }), 200
    except Exception as e:
        import traceback
        print(f"Error in test_table: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# 管理员专用接口


@bp.route('/admin/database-tables', methods=['GET'], strict_slashes=False)
@jwt_required()
def admin_get_database_tables():
    """
    管理员获取数据库中所有实际存在的表格列表
    
    返回：
    {"message": "获取数据库表格列表成功", "tables": ["users", "files", "table_metadata"]}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 获取数据库中所有表
        tables = get_all_tables()
        
        return jsonify({
            'message': '获取数据库表格列表成功',
            'tables': tables
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/tables', methods=['GET'], strict_slashes=False)
@jwt_required()
def admin_get_all_tables():
    """
    管理员获取所有表格列表（包括非活跃的）
    
    返回：
    {"message": "获取所有表格列表成功", "tables": [{"id": 1, "table_name": "users", "display_name": "用户表", "description": "系统用户信息"}]}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 获取所有表格元数据
        tables = TableMetadata.query.all()
        
        # 转换为响应格式
        table_list = []
        for table in tables:
            table_list.append({
                'id': table.id,
                'table_name': table.table_name,
                'display_name': table.display_name,
                'description': table.description,
                'is_active': table.is_active,
                'created_at': table.created_at.isoformat(),
                'updated_at': table.updated_at.isoformat()
            })
        
        return jsonify({
            'message': '获取所有表格列表成功',
            'tables': table_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/tables', methods=['POST'], strict_slashes=False)
@jwt_required()
def admin_create_table_metadata():
    """
    管理员创建或更新表格元数据
    
    请求体：
    {"table_name": "users", "display_name": "用户表", "description": "系统用户信息", "is_active": true}
    
    返回：
    {"message": "创建表格元数据成功", "table": {"id": 1, "table_name": "users", "display_name": "用户表"}}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '没有权限访问该接口'}), 403
        
        data = request.get_json()
        table_name = data.get('table_name')
        
        if not table_name:
            return jsonify({'error': '缺少表格名称'}), 400
        
        # 检查表格是否存在
        if not check_table_exists(table_name):
            return jsonify({'error': '数据库中不存在该表格'}), 400
        
        # 查找或创建表格元数据
        table_metadata = TableMetadata.query.filter_by(table_name=table_name).first()
        
        if table_metadata:
            # 更新现有元数据
            table_metadata.display_name = data.get('display_name', table_metadata.display_name)
            table_metadata.description = data.get('description', table_metadata.description)
            table_metadata.is_active = data.get('is_active', table_metadata.is_active)
        else:
            # 创建新元数据
            table_metadata = TableMetadata(
                table_name=table_name,
                display_name=data.get('display_name', table_name.replace('_', ' ').title()),
                description=data.get('description'),
                is_active=data.get('is_active', True)
            )
            db.session.add(table_metadata)
        
        db.session.commit()
        
        return jsonify({
            'message': '创建/更新表格元数据成功',
            'table': {
                'id': table_metadata.id,
                'table_name': table_metadata.table_name,
                'display_name': table_metadata.display_name,
                'description': table_metadata.description,
                'is_active': table_metadata.is_active,
                'created_at': table_metadata.created_at.isoformat(),
                'updated_at': table_metadata.updated_at.isoformat()
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/tables/<string:table_name>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def admin_update_table_metadata(table_name):
    """
    管理员更新指定表格的元数据
    
    参数：
    table_name: 表格名称
    
    请求体：
    {"display_name": "用户表", "description": "系统用户信息", "is_active": true}
    
    返回：
    {"message": "更新表格元数据成功", "table": {"id": 1, "table_name": "users", "display_name": "用户表"}}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 查找表格元数据
        table_metadata = TableMetadata.query.filter_by(table_name=table_name).first()
        
        if not table_metadata:
            return jsonify({'error': '表格元数据不存在'}), 404
        
        # 更新元数据
        data = request.get_json()
        table_metadata.display_name = data.get('display_name', table_metadata.display_name)
        table_metadata.description = data.get('description', table_metadata.description)
        table_metadata.is_active = data.get('is_active', table_metadata.is_active)
        
        db.session.commit()
        
        return jsonify({
            'message': '更新表格元数据成功',
            'table': {
                'id': table_metadata.id,
                'table_name': table_metadata.table_name,
                'display_name': table_metadata.display_name,
                'description': table_metadata.description,
                'is_active': table_metadata.is_active,
                'created_at': table_metadata.created_at.isoformat(),
                'updated_at': table_metadata.updated_at.isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/access', methods=['GET'], strict_slashes=False)
@jwt_required()
def admin_get_table_access():
    """
    管理员获取用户表格访问权限列表
    
    返回：
    {"message": "获取用户表格访问权限列表成功", "access_list": [{"id": 1, "user_id": 1, "username": "admin", "table_name": "users", "can_view": true, "can_edit": true, "can_export": true}]}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 获取所有用户表格访问权限
        table_accesses = TableAccess.query.join(User).all()
        
        # 转换为响应格式
        access_list = []
        for access in table_accesses:
            access_list.append({
                'id': access.id,
                'user_id': access.user_id,
                'username': access.user.username,
                'table_name': access.table_name,
                'can_view': access.can_view,
                'can_edit': access.can_edit,
                'can_export': access.can_export,
                'created_at': access.created_at.isoformat(),
                'updated_at': access.updated_at.isoformat()
            })
        
        return jsonify({
            'message': '获取用户表格访问权限列表成功',
            'access_list': access_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/access', methods=['POST'], strict_slashes=False)
@jwt_required()
def admin_set_table_access():
    """
    管理员设置用户表格访问权限（支持单个或批量）
    
    请求体（单个）：
    {"user_id": 1, "table_name": "users", "can_view": true, "can_edit": false, "can_export": true}
    
    请求体（批量）：
    {
        "user_ids": [1, 2], 
        "table_names": ["users", "orders"], 
        "can_view": true, 
        "can_edit": false, 
        "can_export": true
    }
    
    返回：
    {"message": "设置用户表格访问权限成功", "success_count": 4, "access_list": [...]}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '没有权限访问该接口'}), 403
        
        data = request.get_json()
        
        # 检查是否为批量请求
        has_user_ids = 'user_ids' in data and isinstance(data['user_ids'], list)
        has_table_names = 'table_names' in data and isinstance(data['table_names'], list)
        
        access_list = []
        success_count = 0
        
        if has_user_ids and has_table_names:
            # 批量设置权限
            user_ids = data['user_ids']
            table_names = data['table_names']
            can_view = data.get('can_view', True)
            can_edit = data.get('can_edit', False)
            can_export = data.get('can_export', True)
            
            if not user_ids or not table_names:
                return jsonify({'error': '缺少用户ID列表或表格名称列表'}), 400
            
            # 遍历所有用户和表格的组合
            for user_id in user_ids:
                for table_name in table_names:
                    try:
                        # 检查用户是否存在
                        target_user = User.query.get(user_id)
                        if not target_user:
                            continue
                        
                        # 跳过管理员用户，防止管理员权限被意外修改
                        if target_user.role == 'admin':
                            print(f"跳过管理员用户 {user_id} 的权限设置")
                            continue
                        
                        # 检查表格是否存在
                        if not check_table_exists(table_name):
                            continue
                        
                        # 查找或创建访问权限
                        table_access = TableAccess.query.filter_by(user_id=user_id, table_name=table_name).first()
                        
                        if table_access:
                            # 更新现有权限
                            table_access.can_view = can_view
                            table_access.can_edit = can_edit
                            table_access.can_export = can_export
                        else:
                            # 创建新权限
                            table_access = TableAccess(
                                user_id=user_id,
                                table_name=table_name,
                                can_view=can_view,
                                can_edit=can_edit,
                                can_export=can_export
                            )
                            db.session.add(table_access)
                        
                        # 收集成功的权限记录
                        access_list.append({
                            'id': table_access.id,
                            'user_id': table_access.user_id,
                            'username': target_user.username,
                            'table_name': table_access.table_name,
                            'can_view': table_access.can_view,
                            'can_edit': table_access.can_edit,
                            'can_export': table_access.can_export,
                            'created_at': table_access.created_at.isoformat(),
                            'updated_at': table_access.updated_at.isoformat()
                        })
                        success_count += 1
                    except Exception as e:
                        print(f"设置用户 {user_id} 对表格 {table_name} 的权限失败: {str(e)}")
                        continue
        else:
            # 单个设置权限
            user_id = data.get('user_id')
            table_name = data.get('table_name')
            
            if not user_id or not table_name:
                return jsonify({'error': '缺少用户ID或表格名称'}), 400
            
            # 检查用户是否存在
            target_user = User.query.get(user_id)
            if not target_user:
                return jsonify({'error': '用户不存在'}), 404
            
            # 跳过管理员用户，防止管理员权限被意外修改
            if target_user.role == 'admin':
                return jsonify({'error': '管理员用户的权限不能被修改'}), 400
            
            # 检查表格是否存在
            if not check_table_exists(table_name):
                return jsonify({'error': '表格不存在'}), 404
            
            # 查找或创建访问权限
            table_access = TableAccess.query.filter_by(user_id=user_id, table_name=table_name).first()
            
            if table_access:
                # 更新现有权限
                table_access.can_view = data.get('can_view', table_access.can_view)
                table_access.can_edit = data.get('can_edit', table_access.can_edit)
                table_access.can_export = data.get('can_export', table_access.can_export)
            else:
                # 创建新权限
                table_access = TableAccess(
                    user_id=user_id,
                    table_name=table_name,
                    can_view=data.get('can_view', True),
                    can_edit=data.get('can_edit', False),
                    can_export=data.get('can_export', True)
                )
                db.session.add(table_access)
            
            # 收集成功的权限记录
            access_list.append({
                'id': table_access.id,
                'user_id': table_access.user_id,
                'username': target_user.username,
                'table_name': table_access.table_name,
                'can_view': table_access.can_view,
                'can_edit': table_access.can_edit,
                'can_export': table_access.can_export,
                'created_at': table_access.created_at.isoformat(),
                'updated_at': table_access.updated_at.isoformat()
            })
            success_count = 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功设置 {success_count} 条权限记录',
            'success_count': success_count,
            'access_list': access_list
        }), 201
    except Exception as e:
        import traceback
        error_msg = f"Error in admin_set_table_access: {str(e)}"
        traceback_str = traceback.format_exc()
        print(f"Error: {error_msg}")
        print(f"Traceback: {traceback_str}")
        return jsonify({'error': error_msg}), 500


@bp.route('/admin/access/<int:access_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def admin_delete_table_access(access_id):
    """
    管理员删除用户表格访问权限
    
    参数：
    access_id: 权限ID
    
    返回：
    {"message": "删除用户表格访问权限成功"}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 查找并删除权限
        table_access = TableAccess.query.get(access_id)
        
        if not table_access:
            return jsonify({'error': '权限不存在'}), 404
        
        db.session.delete(table_access)
        db.session.commit()
        
        return jsonify({
            'message': '删除用户表格访问权限成功'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/import-table', methods=['POST'], strict_slashes=False)
@jwt_required()
def admin_import_table():
    """
    管理员导入数据表
    
    支持两种导入方式：
    1. 从文件导入（CSV/Excel）
    2. 从SQL语句创建
    
    请求体：
    - 方式1（文件导入）：
      {"type": "file", "table_name": "users", "file": <file>}
    - 方式2（SQL创建）：
      {"type": "sql", "sql_statement": "CREATE TABLE users (...)"}
    
    返回：
    {"message": "表格导入成功", "table_name": "users"}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 获取导入类型
        import_type = request.form.get('type') or request.json.get('type')
        
        if not import_type:
            return jsonify({'error': '缺少导入类型'}), 400
        
        if import_type == 'file':
            # 文件导入方式
            # 检查是否有文件上传
            if 'file' not in request.files:
                return jsonify({'error': '缺少文件'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '文件名不能为空'}), 400
            
            # 获取目标表格名称
            table_name = request.form.get('table_name')
            if not table_name:
                return jsonify({'error': '缺少表格名称'}), 400
            
            # 保存文件到临时目录
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, file.filename)
            file.save(file_path)
            
            try:
                # 导入表格
                result = import_table_from_file(file_path, table_name)
                
                if result['success']:
                    # 创建或更新表格元数据
                    table_metadata = TableMetadata.query.filter_by(table_name=table_name).first()
                    if not table_metadata:
                        table_metadata = TableMetadata(
                            table_name=table_name,
                            display_name=table_name.replace('_', ' ').title(),
                            description=f"从文件导入的表格: {file.filename}",
                            is_active=True
                        )
                        db.session.add(table_metadata)
                        db.session.commit()
                    
                    return jsonify({
                        'message': result['message'],
                        'table_name': table_name,
                        'rows_imported': result['rows_imported'],
                        'columns': result['columns']
                    }), 201
                else:
                    return jsonify({'error': result['message']}), 400
            finally:
                # 删除临时文件
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        elif import_type == 'sql':
            # SQL语句创建方式
            sql_statement = request.json.get('sql_statement')
            if not sql_statement:
                return jsonify({'error': '缺少SQL语句'}), 400
            
            # 执行SQL语句创建表格
            result = create_table_from_sql(sql_statement)
            
            if result['success']:
                # 创建或更新表格元数据
                table_metadata = TableMetadata.query.filter_by(table_name=result['table_name']).first()
                if not table_metadata:
                    table_metadata = TableMetadata(
                        table_name=result['table_name'],
                        display_name=result['table_name'].replace('_', ' ').title(),
                        description="从SQL语句创建的表格",
                        is_active=True
                    )
                    db.session.add(table_metadata)
                    db.session.commit()
                
                return jsonify({
                    'message': result['message'],
                    'table_name': result['table_name']
                }), 201
            else:
                return jsonify({'error': result['message']}), 400
        
        else:
            return jsonify({'error': '不支持的导入类型'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/tables/<string:table_name>/rows', methods=['POST'], strict_slashes=False)
@jwt_required()
def admin_insert_table_row(table_name):
    """
    向表格中插入一行数据（管理员或拥有编辑权限的用户）
    
    参数：
    table_name: 表格名称
    
    请求体：
    {"column1": "value1", "column2": "value2"}
    
    返回：
    {"message": "数据行插入成功", "inserted_id": 1}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # 检查用户权限：管理员或拥有编辑权限
        if user.role != 'admin':
            table_access = TableAccess.query.filter_by(
                user_id=current_user_id,
                table_name=table_name,
                can_edit=True
            ).first()
            if not table_access:
                return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        # 检查表格是否存在
        if not check_table_exists(table_name):
            return jsonify({'error': '表格不存在'}), 404
        
        # 插入数据行
        result = insert_table_row(table_name, data)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'inserted_id': result['inserted_id']
            }), 201
        else:
            return jsonify({'error': result['message']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/tables/<string:table_name>/rows/<string:row_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def admin_update_table_row(table_name, row_id):
    """
    更新表格中的一行数据（管理员或拥有编辑权限的用户）
    
    参数：
    table_name: 表格名称
    row_id: 行ID，字符串格式
    
    请求体：
    {"column1": "new_value1", "column2": "new_value2"}
    
    查询参数：
    primary_key: 主键列名，默认为'id'
    
    返回：
    {"message": "数据行更新成功", "updated_rows": 1}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # 检查用户权限：管理员或拥有编辑权限
        if user.role != 'admin':
            table_access = TableAccess.query.filter_by(
                user_id=current_user_id,
                table_name=table_name,
                can_edit=True
            ).first()
            if not table_access:
                return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '缺少请求数据'}), 400
        
        # 检查表格是否存在
        if not check_table_exists(table_name):
            return jsonify({'error': '表格不存在'}), 404
        
        # 获取主键列名（默认为'id'）
        primary_key = request.args.get('primary_key', 'id')
        
        # 更新数据行
        result = update_table_row(table_name, row_id, data, primary_key)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'updated_rows': result['updated_rows']
            }), 200
        else:
            return jsonify({'error': result['message']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/tables/<string:table_name>/rows/<string:row_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def admin_delete_table_row(table_name, row_id):
    """
    删除表格中的一行数据（管理员或拥有编辑权限的用户）
    
    参数：
    table_name: 表格名称
    row_id: 行ID，字符串格式
    
    查询参数：
    primary_key: 主键列名，默认为'id'
    
    返回：
    {"message": "数据行删除成功", "deleted_rows": 1}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        # 检查用户权限：管理员或拥有编辑权限
        if user.role != 'admin':
            table_access = TableAccess.query.filter_by(
                user_id=current_user_id,
                table_name=table_name,
                can_edit=True
            ).first()
            if not table_access:
                return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 检查表格是否存在
        if not check_table_exists(table_name):
            return jsonify({'error': '表格不存在'}), 404
        
        # 获取主键列名（默认为'id'）
        primary_key = request.args.get('primary_key', 'id')
        
        # 删除数据行
        result = delete_table_row(table_name, row_id, primary_key)
        
        if result['success']:
            return jsonify({
                'message': result['message'],
                'deleted_rows': result['deleted_rows']
            }), 200
        else:
            return jsonify({'error': result['message']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/tables/<string:table_name>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def admin_delete_table(table_name):
    """
    管理员删除整个表格
    
    参数：
    table_name: 表格名称
    
    返回：
    {"message": "表格删除成功"}
    """
    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        
        if user.role != 'admin':
            return jsonify({'error': '没有权限访问该接口'}), 403
        
        # 直接执行删除操作，不进行存在性检查，因为 DROP TABLE IF EXISTS 会处理表格不存在的情况
        result = delete_table(table_name)
        if not result['success']:
            return jsonify({'error': result['message']}), 400
        
        # 清理系统库中的相关数据
        
        # 1. 删除表格元数据
        table_metadata = TableMetadata.query.filter_by(table_name=table_name).first()
        if table_metadata:
            db.session.delete(table_metadata)
            db.session.commit()
        
        # 2. 删除相关的访问权限
        table_accesses = TableAccess.query.filter_by(table_name=table_name).all()
        for access in table_accesses:
            db.session.delete(access)
        db.session.commit()
        
        # 返回成功消息
        return jsonify({'message': f'表格{table_name}删除成功'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
