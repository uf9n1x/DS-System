"""
主应用入口，初始化Flask应用，配置数据库连接等
"""

import os
import sys
from datetime import timedelta
from flask import Flask
# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
from backend.config import DB_CONFIG, DATASHARE_DB_CONFIG, DATASHARE_DB_BIND, JWT_SECRET_KEY, UPLOAD_FOLDER, MAX_CONTENT_LENGTH, DEBUG, SECRET_KEY, JWT_ACCESS_TOKEN_EXPIRES
from backend.extensions import cors, jwt, db, datashare_db

# 创建Flask应用
app = Flask(__name__)

# 配置应用
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 主数据库配置（系统库）
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# 数据共享数据库配置
datashare_uri = f"mysql+pymysql://{DATASHARE_DB_CONFIG['user']}:{DATASHARE_DB_CONFIG['password']}@{DATASHARE_DB_CONFIG['host']}:{DATASHARE_DB_CONFIG['port']}/{DATASHARE_DB_CONFIG['database']}"
app.config['SQLALCHEMY_BINDS'] = {
    DATASHARE_DB_BIND: datashare_uri
}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

# 添加日志配置
import logging
# 配置详细的日志格式
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# 初始化扩展
cors.init_app(app, origins="*", supports_credentials=True, expose_headers=["Authorization"])
jwt.init_app(app)  # 使用extensions.py中的jwt实例
db.init_app(app)

# 添加JWT令牌验证逻辑，防止同一账号多处同时登录
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from backend.models.user import User

@jwt.token_verification_loader
def verify_token_identifier(headers, payload):
    """
    验证JWT令牌标识符是否与用户表中存储的一致
    
    Args:
        headers: JWT头信息
        payload: JWT负载
    
    Returns:
        bool: 令牌是否有效
    """
    # 获取令牌标识符和用户ID
    token_identifier = payload.get('token_identifier')
    user_id = payload.get('sub')  # sub字段存储的是用户ID
    
    if not token_identifier or not user_id:
        return False
    
    # 查询用户
    user = User.query.get(int(user_id))
    if not user:
        return False
    
    # 验证令牌标识符是否匹配
    return user.jwt_token_identifier == token_identifier

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 导入并注册路由
from backend.routes.auth import bp as auth_bp
from backend.routes.files import bp as files_bp
from backend.routes.users import bp as users_bp
from backend.routes.data import bp as data_bp

app.register_blueprint(auth_bp)
app.register_blueprint(files_bp)
app.register_blueprint(users_bp)
app.register_blueprint(data_bp)

# 创建数据库表
try:
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员用户（如果不存在）
        from backend.models.user import User
        from backend.utils.auth import hash_password
        
        # 检查是否已存在管理员用户
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            # 创建默认管理员用户
            default_admin = User(
                username='admin',
                password_hash=hash_password('admin123'),
                email='admin@example.com',
                role='admin'
            )
            db.session.add(default_admin)
            db.session.commit()
            print("默认管理员用户创建成功!")
            print("用户名: admin, 密码: admin123")
    print("数据库表创建成功!")
except Exception as e:
    print(f"数据库表创建失败: {e}")
    import traceback
    traceback.print_exc()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=DEBUG)