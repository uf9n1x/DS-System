"""
数据共享模块工具函数
"""

import os
import csv
from io import StringIO, BytesIO
import pandas as pd
from flask import current_app
from sqlalchemy import text, desc
from ..extensions import db
from ..config import DATASHARE_DB_CONFIG, DATASHARE_DB_BIND
from ..models.data_share import TableMetadata

# 数据共享数据库配置常量
DATASHARE_DB_NAME = DATASHARE_DB_CONFIG['database']


def check_table_exists(table_name, database=DATASHARE_DB_NAME):
    """
    检查表格是否存在
    
    Args:
        table_name: 表格名称
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        bool: 表格是否存在
    """
    # 清理表名，移除可能的数据库名前缀
    if '.' in table_name:
        table_name = table_name.split('.')[-1]
        table_name = table_name.strip("'\"")
    
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
        inspector = db.inspect(engine)
    else:
        # 使用主数据库连接
        engine = db.engine
        inspector = db.inspect(engine)
    
    try:
        # 使用inspector.get_table_names()获取所有表格名称，然后进行精确匹配
        tables = inspector.get_table_names()
        return table_name in tables
    finally:
        engine.dispose()


def global_search(search_query, database=DATASHARE_DB_NAME, tables_to_search=None):
    """
    全局搜索指定表格内容
    
    Args:
        search_query: 搜索关键词
        database: 数据库名称，默认为DATASHARE_DB_NAME
        tables_to_search: 要搜索的表格列表，默认为None（搜索所有表格）
        
    Returns:
        list: 搜索结果列表，包含匹配的表格和数据
    """
    if not search_query:
        return []
    
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    connection = engine.connect()
    
    results = []
    
    try:
        # 获取要搜索的表格
        if tables_to_search:
            all_tables = tables_to_search
        else:
            all_tables = get_all_tables(database=database)
        
        # 一次性获取所有表格元数据，减少数据库连接开销
        try:
            main_engine = db.engine
            main_connection = main_engine.connect()
            metadata_query = text("SELECT table_name, display_name, description FROM table_metadata")
            metadata_results = main_connection.execute(metadata_query)
            all_metadata = {row.table_name: {'display_name': row.display_name, 'description': row.description} for row in metadata_results}
            main_connection.close()
        except Exception as e:
            print(f"获取表格元数据失败: {str(e)}")
            all_metadata = {}
        
        for table_name in all_tables:
            try:
                # 跳过系统表（以_或table_metadata开头的表）
                if table_name.startswith('_') or table_name == 'table_metadata':
                    continue
                
                # 获取表格元数据
                table_meta = all_metadata.get(table_name, {})
                display_name = table_meta.get('display_name', table_name)
                description = table_meta.get('description', '')
                
                # 检查表格是否有数据列
                columns_result = connection.execute(text(f"DESCRIBE `{table_name}`"))
                table_columns = []
                for col in columns_result.fetchall():
                    if len(col) >= 1:
                        table_columns.append(col[0])
                
                # 跳过没有数据列的表格
                if len(table_columns) < 1:  # 至少有一个列
                    continue
                
                # 构建搜索条件，使用简化的参数名，提高性能
                search_conditions = []
                
                # 只搜索非id列，提高性能
                non_id_columns = [col for col in table_columns if col.lower() != 'id']
                if not non_id_columns:
                    continue
                
                # 使用统一的参数名，避免复杂的参数映射
                search_pattern = f"%{search_query}%"
                params = {"search_pattern": search_pattern}
                
                for col in non_id_columns:
                    # 为每列构建搜索条件
                    search_conditions.append(f"`{col}` LIKE :search_pattern")
                
                # 构建查询语句，只查询前5条匹配结果，同时选择所有列
                query = f"SELECT * FROM `{table_name}` WHERE ({' OR '.join(search_conditions)}) LIMIT 5"
                
                # 执行查询
                result = connection.execute(text(query), params)
                rows = result.fetchall()
                
                if rows:
                    # 转换为响应格式，直接使用查询结果，不再重复检查匹配
                    matched_rows = []
                    columns = result.keys()
                    for row in rows:
                        row_dict = dict(zip(columns, row))
                        # 提取所有值，用于显示
                        matched_rows.append({
                            'id': row_dict.get('id', None),
                            'all_data': row_dict,  # 保留完整数据，便于点击跳转
                            'matched_columns': list(row_dict.keys())  # 标记所有列
                        })
                    
                    # 添加到结果列表
                    results.append({
                        'table_name': table_name,
                        'display_name': display_name,
                        'description': description,
                        'rows': matched_rows
                    })
            except Exception as e:
                # 跳过无法搜索的表格
                print(f"搜索表格 {table_name} 时出错: {str(e)}")
                continue
    finally:
        connection.close()
    
    return results


# 全局缓存，存储表格列信息，避免重复查询
table_columns_cache = {}

# 全局缓存，存储表格真实总记录数，定期更新
table_real_total_cache = {}


def get_table_data(table_name, page=1, per_page=10, sort_by=None, sort_order='asc', database=DATASHARE_DB_NAME, columns=None, search_query=None):
    """
    获取表格数据，支持分页、排序和搜索
    
    Args:
        table_name: 表格名称
        page: 页码，默认为1
        per_page: 每页条数，默认为10
        sort_by: 排序字段，默认为None
        sort_order: 排序方向，默认为'asc'，可选值为'asc'或'desc'
        database: 数据库名称，默认为DATASHARE_DB_NAME
        columns: 要返回的列列表，默认为None（返回所有列）
        search_query: 搜索关键词，默认为None
        
    Returns:
        dict: 包含数据和分页信息的字典
    """
    # 清理表名，移除可能的数据库名前缀
    if '.' in table_name:
        table_name = table_name.split('.')[-1]
        table_name = table_name.strip("'\"")
    
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    connection = engine.connect()
    
    try:
        # 构建缓存键
        cache_key = f"{database}.{table_name}"
        
        # 获取真实的表格总记录数（不考虑搜索条件），使用缓存优化
        real_total = 0
        if cache_key in table_real_total_cache:
            # 使用缓存的真实总记录数
            real_total = table_real_total_cache[cache_key]
        else:
            # 执行COUNT(*)查询获取真实总记录数
            real_total_result = connection.execute(text(f"SELECT COUNT(*) as real_total FROM `{table_name}`"))
            real_total = real_total_result.fetchone()[0]
            # 更新缓存
            table_real_total_cache[cache_key] = real_total
        
        # 确定要查询的列
        if columns:
            selected_columns = ', '.join([f'`{col}`' for col in columns])
        else:
            selected_columns = '*'
        
        # 构建基本查询
        query = f"SELECT {selected_columns} FROM `{table_name}`"
        
        # 添加搜索条件
        where_clauses = []
        params = {}
        
        if search_query:
            try:
                # 获取表格所有列，使用缓存优化
                table_columns = []
                if cache_key in table_columns_cache:
                    # 使用缓存的列信息
                    table_columns = table_columns_cache[cache_key]
                else:
                    # 执行DESCRIBE查询获取列信息
                    columns_result = connection.execute(text(f"DESCRIBE `{table_name}`"))
                    table_columns = [col for col in columns_result.fetchall()]
                    # 更新缓存
                    table_columns_cache[cache_key] = table_columns
                
                # 构建模糊搜索条件，排除主键列
                search_conditions = []
                # 使用统一的参数名，避免列名包含特殊字符导致的问题
                param_name = "search_query"
                params[param_name] = f"%{search_query}%"
                
                for col in table_columns:
                    # 确保元组有足够的元素，避免IndexError
                    if len(col) >= 4:
                        col_name = col[0]
                        col_key = col[3]  # 获取列的键类型（PRI表示主键）
                        # 排除主键列，而不仅仅是名为'id'的列
                        if col_key != 'PRI':
                            search_conditions.append(f"`{col_name}` LIKE :{param_name}")
                
                if search_conditions:
                    where_clauses.append(f"({' OR '.join(search_conditions)})")
            except Exception as e:
                # 搜索过程中出现错误，不影响基本数据查询，跳过搜索条件
                pass
        
        # 添加WHERE子句
        where_clauses_str = ""
        if where_clauses:
            where_clauses_str = f" WHERE {' AND '.join(where_clauses)}"
        
        # 获取搜索命中的记录数，只有在需要时才执行
        filtered_total = 0
        if page == 1:  # 只在第一页时获取总数，减少查询次数
            # 构建COUNT查询，直接使用WHERE条件
            count_query = f"SELECT COUNT(*) as filtered_total FROM `{table_name}`{where_clauses_str}"
            count_result = connection.execute(text(count_query), params)
            filtered_total = count_result.fetchone()[0]
        else:
            # 非第一页时，使用估算值或从请求参数中获取，这里暂时使用per_page作为默认值
            filtered_total = per_page
        
        # 添加WHERE子句到主查询
        if where_clauses_str:
            query += where_clauses_str
        
        # 添加排序
        if sort_by:
            order_dir = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
            query += f" ORDER BY `{sort_by}` {order_dir}"
        
        # 添加分页
        offset = (page - 1) * per_page
        query += f" LIMIT {per_page} OFFSET {offset}"
        
        # 执行查询获取数据
        result = connection.execute(text(query), params)
        rows = result.fetchall()
        
        # 获取列名
        columns = result.keys()
        
        # 转换为字典列表
        data = [dict(zip(columns, row)) for row in rows]
        
        # 如果是非第一页且filtered_total不准确，使用实际返回的行数估算
        if page != 1 and len(data) > 0:
            # 估算总记录数，假设每页都有per_page条记录
            estimated_total = (page - 1) * per_page + len(data)
            filtered_total = estimated_total
        
        return {
            'data': data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'real_total': real_total,
                'filtered_total': filtered_total,
                'pages': (filtered_total + per_page - 1) // per_page
            }
        }
    finally:
        connection.close()


def get_table_columns(table_name, database=DATASHARE_DB_NAME):
    """
    获取表格列信息
    
    Args:
        table_name: 表格名称
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        list: 列信息列表
    """
    # 清理表名，移除可能的数据库名前缀
    # 处理格式如：datashare.table_name 或 'datashare.'table_name 的情况
    if '.' in table_name:
        # 只保留最后一个点后面的部分作为表名
        table_name = table_name.split('.')[-1]
        # 移除可能的引号
        table_name = table_name.strip("'\"")
    
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    connection = engine.connect()
    
    try:
        # 获取列信息 - 使用正确的引号处理表名
        result = connection.execute(text(f"DESCRIBE `{table_name}`"))
        columns = result.fetchall()
        
        # 转换为字典列表
        column_info = []
        for column in columns:
            column_info.append({
                'name': column[0],
                'type': column[1],
                'null': column[2],
                'key': column[3],
                'default': column[4],
                'extra': column[5]
            })
        
        return column_info
    finally:
        connection.close()


def export_table_data(table_name, format='csv', database=DATASHARE_DB_NAME):
    """
    导出表格数据
    
    Args:
        table_name: 表格名称
        format: 导出格式，默认为'csv'，可选值为'csv'或'excel'
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        tuple: (文件名, 文件内容, Content-Type)
    """
    # 清理表名，移除可能的数据库名前缀
    if '.' in table_name:
        table_name = table_name.split('.')[-1]
        table_name = table_name.strip("'\"")
    
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    connection = engine.connect()
    
    try:
        # 获取所有数据
        query = f"SELECT * FROM `{table_name}`"
        result = connection.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()
        
        # 转换为DataFrame
        df = pd.DataFrame(rows, columns=columns)
        
        if format == 'csv':
            # 导出为CSV
            output = StringIO()
            df.to_csv(output, index=False, encoding='utf-8-sig')
            content = output.getvalue()
            filename = f"{table_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            content_type = 'text/csv; charset=utf-8'
        elif format == 'excel':
            # 导出为Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=table_name)
            content = output.getvalue()
            filename = f"{table_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        return filename, content, content_type
    finally:
        connection.close()


def get_all_tables(database=DATASHARE_DB_NAME):
    """
    获取数据库中所有表格名称
    
    Args:
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        list: 表格名称列表
    """
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
        inspector = db.inspect(engine)
    else:
        # 使用主数据库连接
        engine = db.engine
        inspector = db.inspect(engine)
    
    try:
        # 获取所有表格
        tables = inspector.get_table_names()
        return tables
    finally:
        engine.dispose()


def execute_sql_query(query, params=None, database=DATASHARE_DB_NAME):
    """
    执行SQL查询
    
    Args:
        query: SQL查询语句
        params: 查询参数，默认为None
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        list: 查询结果列表
    """
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    
    connection = engine.connect()
    
    try:
        result = connection.execute(text(query), params or {})
        return result.fetchall()
    finally:
        connection.close()


def import_table_from_file(file_path, table_name, database=DATASHARE_DB_NAME):
    """
    从文件导入数据表
    
    Args:
        file_path: 文件路径
        table_name: 目标表格名称
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        dict: 导入结果
    """
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    
    try:
        # 根据文件扩展名选择读取方式
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            return {'success': False, 'message': '不支持的文件格式'}
        
        # 清理表名，移除可能的数据库名前缀和引号
        if '.' in table_name:
            table_name = table_name.split('.')[-1]
        table_name = table_name.strip("'\"`")
        
        # 处理NaN值，替换为None，MySQL支持NULL
        import numpy as np
        df = df.replace({np.nan: None})
        
        # 转换空字符串为None
        df = df.replace({'': None})
        
        # 确保所有列名都是字符串类型
        df.columns = [str(col) for col in df.columns]
        
        # 1. 创建表格，添加自增id作为主键
        connection = engine.connect()
        
        # 构建CREATE TABLE语句，添加自增id列
        columns_def = []
        
        # 添加自增id作为主键
        columns_def.append("`id` INT AUTO_INCREMENT PRIMARY KEY")
        
        # 添加数据列，默认使用VARCHAR类型，后续可以根据数据类型自动调整
        for col in df.columns:
            columns_def.append(f"`{col}` VARCHAR(255)")
        
        create_table_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({', '.join(columns_def)})"
        
        # 执行创建表格语句
        print(f"执行SQL: {create_table_sql}")
        connection.execute(text(create_table_sql))
        connection.commit()
        
        # 2. 插入数据，忽略id列（由数据库自动生成）
        # 构建INSERT语句，使用安全的参数名（param_0, param_1, ...）
        columns = ', '.join([f'`{col}`' for col in df.columns])
        safe_param_names = [f'param_{i}' for i in range(len(df.columns))]
        values = ', '.join([f':{param}' for param in safe_param_names])
        insert_sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({values})"
        
        # 转换数据为安全的字典列表，使用安全的参数名
        data_list = df.to_dict('records')
        safe_data_list = []
        
        for data in data_list:
            safe_data = {}
            for i, (col, value) in enumerate(data.items()):
                # 清理数据，确保没有nan值
                if pd.isna(value) or value == '':
                    safe_data[safe_param_names[i]] = None
                else:
                    safe_data[safe_param_names[i]] = value
            safe_data_list.append(safe_data)
        
        # 执行批量插入
        print(f"执行SQL: {insert_sql}")
        print(f"安全数据样本: {safe_data_list[:2]}")
        connection.execute(text(insert_sql), safe_data_list)
        connection.commit()
        connection.close()
        
        # 3. 返回结果，包含新增的id列
        columns_with_id = ['id'] + list(df.columns)
        
        return {
            'success': True,
            'message': f'表格{table_name}导入成功，已自动添加自增id主键',
            'rows_imported': len(df),
            'columns': columns_with_id
        }
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"导入错误: {str(e)}")
        print(f"堆栈信息: {traceback_str}")
        return {'success': False, 'message': f'导入失败: {str(e)}', 'traceback': traceback_str}


def create_table_from_sql(sql_statement, database=DATASHARE_DB_NAME):
    """
    从SQL语句创建数据表
    
    Args:
        sql_statement: SQL CREATE TABLE语句
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        dict: 创建结果
    """
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    
    connection = engine.connect()
    
    try:
        # 提取表格名称
        import re
        table_name_match = re.search(r'CREATE TABLE\s+([a-zA-Z0-9_]+)', sql_statement, re.IGNORECASE)
        table_name = table_name_match.group(1) if table_name_match else 'unknown'
        
        # 检查SQL语句中是否包含主键定义
        has_primary_key = re.search(r'PRIMARY\s+KEY', sql_statement, re.IGNORECASE)
        
        # 如果没有主键，修改SQL语句，添加自增id作为主键
        if not has_primary_key:
            # 清理表名，移除可能的数据库名前缀和引号
            if '.' in table_name:
                table_name = table_name.split('.')[-1]
                table_name = table_name.strip("'\"")
            
            # 解析原始SQL语句，提取列定义
            columns_match = re.search(r'\(([^)]+)\)', sql_statement)
            if columns_match:
                columns_def = columns_match.group(1)
                # 添加自增id列作为主键
                modified_columns_def = f"`id` INT AUTO_INCREMENT PRIMARY KEY, {columns_def}"
                # 替换原始列定义
                sql_statement = re.sub(r'\(([^)]+)\)', f'({modified_columns_def})', sql_statement)
            else:
                # 如果无法解析列定义，创建一个简单的表格
                sql_statement = f"CREATE TABLE IF NOT EXISTS `{table_name}` (`id` INT AUTO_INCREMENT PRIMARY KEY)"
        
        # 执行SQL语句
        connection.execute(text(sql_statement))
        connection.commit()
        
        return {
            'success': True,
            'message': f'表格{table_name}创建成功，已确保有主键列',
            'table_name': table_name
        }
    except Exception as e:
        connection.rollback()
        return {'success': False, 'message': f'创建失败: {str(e)}'}
    finally:
        connection.close()


def insert_table_row(table_name, data, database=DATASHARE_DB_NAME):
    """
    向表格中插入一行数据
    
    Args:
        table_name: 表格名称
        data: 要插入的数据，字典格式 {列名: 值}
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        dict: 插入结果
    """
    # 清理表名，移除可能的数据库名前缀
    if '.' in table_name:
        table_name = table_name.split('.')[-1]
        table_name = table_name.strip("'\"")
    
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    
    connection = engine.connect()
    
    try:
        # 构建插入语句
        columns = ', '.join([f'`{col}`' for col in data.keys()])
        values = ', '.join([f':{col}' for col in data.keys()])
        insert_query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({values})"
        
        # 执行插入
        result = connection.execute(text(insert_query), data)
        connection.commit()
        
        return {
            'success': True,
            'message': f'数据行插入成功',
            'inserted_id': result.lastrowid
        }
    except Exception as e:
        connection.rollback()
        return {'success': False, 'message': f'插入失败: {str(e)}'}
    finally:
        connection.close()


def update_table_row(table_name, id_value, data, primary_key='id', database=DATASHARE_DB_NAME):
    """
    更新表格中的一行数据
    
    Args:
        table_name: 表格名称
        id_value: 要更新的数据行的主键值
        data: 要更新的数据，字典格式 {列名: 值}
        primary_key: 主键列名，默认为'id'
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        dict: 更新结果
    """
    # 清理表名，移除可能的数据库名前缀
    if '.' in table_name:
        table_name = table_name.split('.')[-1]
        table_name = table_name.strip("'\"")
    
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    
    connection = engine.connect()
    
    try:
        # 构建更新语句
        set_clause = ', '.join([f'`{col}` = :{col}' for col in data.keys()])
        update_query = f"UPDATE `{table_name}` SET {set_clause} WHERE `{primary_key}` = :id_value"
        
        # 准备参数
        params = data.copy()
        params['id_value'] = id_value
        
        # 执行更新
        result = connection.execute(text(update_query), params)
        connection.commit()
        
        return {
            'success': True,
            'message': f'数据行更新成功',
            'updated_rows': result.rowcount
        }
    except Exception as e:
        connection.rollback()
        return {'success': False, 'message': f'更新失败: {str(e)}'}
    finally:
        connection.close()


def delete_table_row(table_name, id_value, primary_key='id', database=DATASHARE_DB_NAME):
    """
    删除表格中的一行数据
    
    Args:
        table_name: 表格名称
        id_value: 要删除的数据行的主键值
        primary_key: 主键列名，默认为'id'
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        dict: 删除结果
    """
    # 清理表名，移除可能的数据库名前缀
    if '.' in table_name:
        table_name = table_name.split('.')[-1]
        table_name = table_name.strip("'\"")
    
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    
    connection = engine.connect()
    
    try:
        # 构建删除语句
        delete_query = f"DELETE FROM `{table_name}` WHERE `{primary_key}` = :id_value"
        
        # 执行删除
        result = connection.execute(text(delete_query), {'id_value': id_value})
        connection.commit()
        
        return {
            'success': True,
            'message': f'数据行删除成功',
            'deleted_rows': result.rowcount
        }
    except Exception as e:
        connection.rollback()
        return {'success': False, 'message': f'删除失败: {str(e)}'}
    finally:
        connection.close()


def delete_table(table_name, database=DATASHARE_DB_NAME):
    """
    删除整个表格
    
    Args:
        table_name: 表格名称
        database: 数据库名称，默认为DATASHARE_DB_NAME
        
    Returns:
        dict: 删除结果
    """
    # 清理表名，移除可能的数据库名前缀
    if '.' in table_name:
        table_name = table_name.split('.')[-1]
        table_name = table_name.strip("'\"")
    
    if database == DATASHARE_DB_NAME:
        # 使用datashare数据库连接
        engine = db.get_engine(bind=DATASHARE_DB_BIND)
    else:
        # 使用主数据库连接
        engine = db.engine
    
    connection = engine.connect()
    
    try:
        # 构建删除语句
        delete_query = f"DROP TABLE IF EXISTS `{table_name}`"
        
        # 执行删除
        connection.execute(text(delete_query))
        connection.commit()
        
        return {
            'success': True,
            'message': f'表格{table_name}删除成功'
        }
    except Exception as e:
        connection.rollback()
        return {'success': False, 'message': f'删除失败: {str(e)}'}
    finally:
        connection.close()
