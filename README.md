# DS-System - 简单局域网数字共享系统

## 项目介绍

DS-System是一个基于Flask和Vue.js开发的简单局域网数字共享系统，旨在提供一个安全、高效的方式在局域网内共享数据和文件。系统支持用户认证、文件管理、数据共享等核心功能，适合小型团队或家庭内部使用。

## 功能特性

### 用户管理
- 用户注册、登录、登出功能
- 支持角色权限管理（管理员/普通用户）
- 在线状态显示
- JWT令牌验证，防止同一账号多处同时登录

### 文件管理
- 文件上传、下载功能
- 支持多种文件类型
- 文件列表展示
- 文件搜索功能
- 支持大文件上传（最大100MB）

### 数据共享
- 数据表创建和管理
- 数据增删改查功能
- 支持表格权限控制（查看/编辑/导出）
- 数据导出功能

### 其他功能
- 响应式设计，支持多种设备访问
- RESTful API设计
- 日志记录功能
- 安全的数据传输

## 技术栈

### 后端
- Python 3.8+
- Flask Web框架
- Flask-JWT-Extended 认证
- Flask-CORS 跨域支持
- SQLAlchemy ORM
- MySQL 数据库

### 前端
- Vue.js 3
- Vuex 状态管理
- Vue Router 路由管理
- Axios HTTP客户端
- Tailwind CSS 样式框架
- Vite 构建工具

## 安装和配置

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### 1. 克隆项目

```bash
git clone https://github.com/uf9n1x/DS-System.git
cd DS-System
```

### 2. 后端配置

#### 2.1 安装Python依赖

```bash
# 建议使用虚拟环境
python -m venv venv
# Windows激活虚拟环境
venv\Scripts\activate
# Linux/Mac激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2.2 数据库配置

1. 创建两个MySQL数据库：
   - 主数据库：`webtools`（用于存储用户、文件等系统数据）
   - 数据共享数据库：`datashare`（用于存储共享数据表）

2. 在MySQL中执行以下命令：

```sql
CREATE DATABASE webtools DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE datashare DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. 配置环境变量

创建`.env`文件，添加以下配置：

```env
# 数据库配置
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=webtools
DATASHARE_DB_NAME=datashare

# JWT配置
JWT_SECRET_KEY=a-very-secure-jwt-secret-key-change-this-in-production
JWT_ACCESS_TOKEN_EXPIRES=3600

# Flask配置
DEBUG=True
SECRET_KEY=your-flask-secret-key-change-this-in-production

# 文件上传配置
UPLOAD_FOLDER=backend/uploads
MAX_CONTENT_LENGTH=100
```

**注意**：请将`your_password`、`your-flask-secret-key-change-this-in-production`等替换为实际的值。

#### 2.3 初始化数据库

运行主应用，系统会自动创建数据库表：

```bash
python app.py
```

首次运行时，系统会自动创建默认管理员用户：
- 用户名：`admin`
- 密码：`admin123`

**建议**：登录后立即修改管理员密码。

### 3. 前端配置

#### 3.1 安装Node.js依赖

```bash
cd frontend
npm install
```

#### 3.2 配置API地址

在`frontend/src/store/index.js`中配置API地址：

```javascript
// 默认API地址为 http://localhost:5001/api
// 如果后端运行在不同的地址或端口，请修改此处
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5001/api'
```

或者通过环境变量配置：

创建`.env`文件在`frontend`目录下：

```env
VUE_APP_API_BASE_URL=http://your-backend-ip:5001/api
```

#### 3.3 构建前端项目

开发环境：
```bash
npm run dev
```

生产环境：
```bash
npm run build
```

构建完成后，将`dist`目录下的文件部署到Web服务器即可。

## 运行项目

### 本地开发调试启动方式

#### 1. 运行后端服务

**步骤1：确保已安装所有Python依赖**
```bash
# 在项目根目录下
python -m venv venv
# Windows激活虚拟环境
venv\Scripts\activate
# Linux/Mac激活虚拟环境
source venv/bin/activate
# 安装依赖
pip install -r requirements.txt
```

**步骤2：配置环境变量**
```bash
# 在项目根目录下创建.env文件，添加以下配置
# 参考前面的数据库配置部分
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=webtools
DATASHARE_DB_NAME=datashare
JWT_SECRET_KEY=a-very-secure-jwt-secret-key-change-this-in-production
DEBUG=True
```

**步骤3：启动后端服务**
```bash
# 在项目根目录下
python app.py
```

后端服务将运行在 `http://0.0.0.0:5001`，可以通过 `http://localhost:5001/api` 访问API

#### 2. 运行前端开发服务器

**步骤1：确保已安装所有Node.js依赖**
```bash
# 在frontend目录下
npm install
```

**步骤2：启动前端开发服务器**
```bash
# 在frontend目录下
npm run dev
```

前端开发服务器将运行在 `http://localhost:5173`

#### 3. 访问系统

在浏览器中访问：`http://localhost:5173`

**注意事项**：
- 确保MySQL服务已启动
- 确保后端服务和前端开发服务器都在运行
- 如果前端无法连接到后端，请检查API地址配置是否正确

### 生产环境部署说明

#### 1. 后端部署

**步骤1：准备生产环境**
```bash
# 1. 创建生产环境虚拟环境
python -m venv venv_prod
# 激活虚拟环境
venv_prod\Scripts\activate
# 安装生产依赖
pip install -r requirements.txt
```

**步骤2：配置生产环境变量**
```bash
# 在项目根目录下创建.env.prod文件
# 注意：生产环境务必使用强密码和密钥
DB_USER=root
DB_PASSWORD=your_strong_production_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=webtools_prod
DATASHARE_DB_NAME=datashare_prod
JWT_SECRET_KEY=your-very-strong-jwt-secret-key-production
JWT_ACCESS_TOKEN_EXPIRES=3600
DEBUG=False
SECRET_KEY=your-very-strong-flask-secret-key-production
```

**步骤3：使用WSGI服务器部署后端**

推荐使用Gunicorn或uWSGI作为WSGI服务器：

```bash
# 安装Gunicorn
pip install gunicorn

# 使用Gunicorn启动后端服务
# 示例：使用4个工作进程，绑定到0.0.0.0:5001
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

**步骤4：配置系统服务（可选，推荐）**

创建系统服务文件，如 `/etc/systemd/system/ds-system.service`（Linux系统）：

```ini
[Unit]
Description=DS-System Backend Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/DS-System
Environment=PATH=/path/to/DS-System/venv_prod/bin
ExecStart=/path/to/DS-System/venv_prod/bin/gunicorn -w 4 -b 0.0.0.0:5001 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 2. 前端部署

**步骤1：构建前端项目**

```bash
# 在frontend目录下
# 配置生产环境API地址
VUE_APP_API_BASE_URL=http://your-production-backend-ip:5001/api npm run build
```

或者在frontend目录下创建`.env.production`文件：

```env
VUE_APP_API_BASE_URL=http://your-production-backend-ip:5001/api
```

然后执行构建：

```bash
npm run build
```

构建完成后，将生成`dist`目录，包含所有静态文件。

**步骤2：部署前端静态文件**

可以使用Nginx或Apache等Web服务器部署前端静态文件。以下是Nginx配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/DS-System/frontend/dist;
    index index.html;

    # 处理单页应用路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 配置API反向代理
    location /api {
        proxy_pass http://localhost:5001/api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**步骤3：配置HTTPS（可选，推荐）**

可以使用Let's Encrypt等服务获取免费SSL证书：

```bash
# 安装Certbot
apt install certbot python3-certbot-nginx

# 获取SSL证书
certbot --nginx -d your-domain.com
```

#### 3. 数据库配置

**步骤1：创建生产数据库**

```sql
CREATE DATABASE webtools_prod DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE datashare_prod DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**步骤2：初始化生产数据库**

```bash
# 在项目根目录下
# 确保已激活生产虚拟环境
# 设置环境变量为生产配置
set FLASK_ENV=production
set FLASK_APP=app.py
python -c "from app import app; with app.app_context(): from backend.extensions import db; db.create_all()"
```

**步骤3：创建生产环境管理员用户**

可以通过运行以下Python脚本创建管理员用户：

```python
from app import app
from backend.extensions import db
from backend.models.user import User
from backend.utils.auth import hash_password

with app.app_context():
    # 检查是否已存在管理员用户
    admin_user = User.query.filter_by(role='admin').first()
    if not admin_user:
        # 创建默认管理员用户
        default_admin = User(
            username='admin',
            password_hash=hash_password('your_strong_admin_password'),
            email='admin@your-domain.com',
            role='admin'
        )
        db.session.add(default_admin)
        db.session.commit()
        print("生产环境管理员用户创建成功!")
    else:
        print("管理员用户已存在!")
```

将上述脚本保存为`create_admin.py`，然后执行：

```bash
python create_admin.py
```

#### 4. 启动生产环境

**步骤1：启动后端服务**

```bash
# 使用Gunicorn启动后端
cd /path/to/DS-System
source venv_prod/bin/activate
gunicorn -w 4 -b 0.0.0.0:5001 app:app --daemon
```

或者使用系统服务：

```bash
systemctl start ds-system
systemctl enable ds-system
```

**步骤2：启动Nginx服务**

```bash
systemctl start nginx
systemctl enable nginx
```

**步骤3：验证部署**

在浏览器中访问：`http://your-domain.com` 或 `https://your-domain.com`（如果配置了HTTPS）

#### 5. 生产环境监控和维护

**建议**：
- 配置日志监控，定期检查日志
- 定期备份数据库
- 定期更新依赖包
- 配置防火墙，只开放必要的端口
- 考虑使用Docker容器化部署，便于管理和扩展

### 部署架构示意图

```
+-------------------+     +-------------------+     +-------------------+
|  用户浏览器       |     |  Nginx Web服务器  |     |  Flask后端服务    |
|                   |     |                   |     |                   |
|  HTTPS请求        |---->|  1. 静态文件服务  |     |  1. API处理       |
|                   |     |  2. API反向代理   |---->|  2. 数据库操作    |
+-------------------+     +-------------------+     |  3. 业务逻辑      |
                                                    +-------------------+
                                                           |
                                                           v
                                                    +-------------------+
                                                    |  MySQL数据库      |
                                                    |  1. webtools_prod |
                                                    |  2. datashare_prod|
                                                    +-------------------+
```

## 使用说明

### 1. 用户管理

#### 1.1 注册新用户
1. 访问登录页面，点击"注册"链接
2. 填写用户名、密码和邮箱
3. 点击"注册"按钮

#### 1.2 登录系统
1. 访问登录页面
2. 输入用户名和密码
3. 点击"登录"按钮

#### 1.3 管理用户（管理员）
1. 登录管理员账号
2. 进入"用户管理"页面
3. 可以查看、编辑和删除用户

### 2. 文件管理

#### 2.1 上传文件
1. 登录系统
2. 进入"文件管理"页面
3. 点击"上传文件"按钮
4. 选择要上传的文件
5. 点击"确定"按钮

#### 2.2 下载文件
1. 登录系统
2. 进入"文件管理"页面
3. 找到要下载的文件
4. 点击"下载"按钮

#### 2.3 查看文件详情
1. 登录系统
2. 进入"文件管理"页面
3. 找到要查看的文件
4. 点击文件名查看详情

### 3. 数据共享

#### 3.1 创建数据表
1. 登录系统
2. 进入"数据共享"页面
3. 点击"创建数据表"按钮
4. 填写表名和字段信息
5. 点击"创建"按钮

#### 3.2 管理数据表
1. 登录系统
2. 进入"数据共享"页面
3. 点击数据表名称进入详情页
4. 可以添加、编辑、删除数据
5. 可以设置表格权限

#### 3.3 导出数据
1. 进入数据表详情页
2. 点击"导出"按钮
3. 选择导出格式（CSV/Excel）
4. 点击"确定"按钮

## 项目结构

```
DS-System/
├── backend/                # 后端代码目录
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   ├── file.py        # 文件模型
│   │   └── data_share.py  # 数据共享模型
│   ├── routes/            # API路由
│   │   ├── auth.py        # 认证路由
│   │   ├── files.py       # 文件路由
│   │   ├── users.py       # 用户路由
│   │   └── data.py        # 数据共享路由
│   ├── utils/             # 工具函数
│   │   ├── auth.py        # 认证工具
│   │   ├── file.py        # 文件工具
│   │   └── data_utils.py  # 数据工具
│   ├── sockets/           # WebSocket相关（预留）
│   ├── uploads/           # 文件上传目录
│   ├── config.py          # 配置文件
│   ├── extensions.py      # 扩展初始化
│   └── __init__.py        # 后端包初始化
├── frontend/              # 前端代码目录
│   ├── public/            # 静态资源
│   ├── src/               # 源代码
│   │   ├── assets/        # 资源文件
│   │   ├── components/    # 组件
│   │   ├── router/        # 路由
│   │   ├── store/         # 状态管理
│   │   ├── views/         # 页面
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 入口文件
│   ├── index.html         # HTML模板
│   └── package.json       # 依赖配置
├── app.py                 # 主应用入口
├── requirements.txt       # Python依赖
├── README.md              # 项目说明
├── LICENSE                # 许可证
└── .gitignore             # Git忽略文件
```

## 配置文件说明

### .env 文件

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| DB_USER | 数据库用户名 | root |
| DB_PASSWORD | 数据库密码 | root |
| DB_HOST | 数据库主机 | localhost |
| DB_PORT | 数据库端口 | 3306 |
| DB_NAME | 主数据库名称 | webtools |
| DATASHARE_DB_NAME | 数据共享数据库名称 | datashare |
| JWT_SECRET_KEY | JWT密钥 | a-very-secure-jwt-secret-key-1234567890 |
| JWT_ACCESS_TOKEN_EXPIRES | JWT令牌过期时间（秒） | 3600 |
| UPLOAD_FOLDER | 文件上传目录 | backend/uploads |
| MAX_CONTENT_LENGTH | 最大文件大小（MB） | 100 |
| DEBUG | 调试模式 | False |
| SECRET_KEY | Flask密钥 | your-flask-secret-key |

## 安全建议

1. 生产环境中，务必修改默认的JWT_SECRET_KEY和SECRET_KEY
2. 生产环境中，禁用DEBUG模式
3. 定期备份数据库
4. 限制文件上传大小，防止恶意上传
5. 建议使用HTTPS协议，特别是在公网环境中
6. 定期更新依赖包，修复安全漏洞

## 常见问题

### 1. 无法连接到数据库
- 检查数据库服务是否正常运行
- 检查数据库配置是否正确
- 检查数据库用户权限

### 2. 文件上传失败
- 检查文件大小是否超过限制
- 检查上传目录权限
- 检查网络连接

### 3. 前端无法连接到后端
- 检查后端服务是否正常运行
- 检查API地址配置是否正确
- 检查CORS配置

### 4. 登录失败
- 检查用户名和密码是否正确
- 检查JWT令牌是否过期
- 检查同一账号是否在其他地方登录

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

**注意**：本项目仅供学习和内部使用，请勿用于生产环境或商业用途。在生产环境中使用前，请进行充分的安全测试和评估。