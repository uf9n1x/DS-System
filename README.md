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
- Pinia 状态管理（**注意：不是Vuex**）
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

**方法1：使用标准虚拟环境**
```bash
# 创建虚拟环境
python -m venv venv
# Windows激活虚拟环境
venv\Scripts\activate
# Linux/Mac激活虚拟环境
source venv/bin/activate
# 安装依赖
pip install -r requirements.txt
```

**方法2：使用uv包管理器（推荐）**
```bash
# 创建虚拟环境
uv venv --python python311
# 激活虚拟环境
uv venv activate
# 安装依赖
uv pip install -r requirements.txt
```

#### 2.2 数据库配置

1. 创建两个MySQL数据库：
   - 主数据库：`webtools`（用于存储用户、文件等系统数据）
   - 数据共享数据库：`datashare`（用于存储共享数据表）

2. 在MySQL中执行以下命令：

```sql
CREATE DATABASE webtools DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
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

**注意**：
- 请将`your_password`、`your-flask-secret-key-change-this-in-production`等替换为实际的值
- 数据库排序规则可以根据实际需求调整，系统支持`utf8mb4_general_ci`和`utf8mb4_unicode_ci`

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

#### 3.2 API地址配置

**重要说明**：前端API地址采用相对路径配置，无需手动修改！

- 前端代码中已在`src/main.js`中配置`axios.defaults.baseURL = '/api'`
- 开发环境下，Vite开发服务器会自动将`/api`请求代理到后端服务
- 生产环境下，需要通过Web服务器（如Nginx）配置反向代理

**Vite开发服务器代理配置**：
前端已内置Vite代理配置，无需手动修改。代理配置位于`vite.config.js`中，会自动将`/api`请求代理到`http://localhost:5001`

## 运行项目

### 本地开发调试启动方式

**步骤1：启动后端服务**

```bash
# 在项目根目录下
# 确保已激活虚拟环境
python app.py
```

后端服务将运行在 `http://0.0.0.0:5001`

**步骤2：启动前端开发服务器**

```bash
# 在frontend目录下
npm run dev
```

前端开发服务器将运行在 `http://localhost:5173`

**步骤3：访问系统**

在浏览器中访问：`http://localhost:5173`

**注意事项**：
- 确保MySQL服务已启动
- 确保后端服务和前端开发服务器都在运行
- 前端会自动将所有`/api`请求代理到后端服务

### 生产环境部署说明

#### 1. 后端部署

**步骤1：准备生产环境**
```bash
# 1. 创建生产环境虚拟环境
uv venv --python python311 venv_prod
# 激活虚拟环境
venv_prod\Scripts\activate
# 安装生产依赖
uv pip install -r requirements.txt
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
uv pip install gunicorn

# 使用Gunicorn启动后端服务
# 示例：使用4个工作进程，绑定到0.0.0.0:5001
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

#### 2. 前端部署

**步骤1：构建前端项目**

```bash
# 在frontend目录下
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

    # 配置API反向代理，将/api请求转发到后端服务
    location /api {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**步骤3：启动生产环境**

```bash
# 启动后端服务
cd /path/to/DS-System
source venv_prod/bin/activate
gunicorn -w 4 -b 0.0.0.0:5001 app:app --daemon

# 启动Nginx服务
systemctl start nginx
systemctl enable nginx
```

**步骤4：验证部署**

在浏览器中访问：`http://your-domain.com` 或 `https://your-domain.com`（如果配置了HTTPS）

## 项目结构

```
DS-System/
├── backend/                # 后端代码目录
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   ├── file.py        # 文件模型
│   │   └── data_share.py  # 数据共享模型
│   ├── routes/            # API路由
│   │   ├── auth.py        # 认证路由 (/api/auth)
│   │   ├── files.py       # 文件路由 (/api/files)
│   │   ├── users.py       # 用户路由 (/api/users)
│   │   └── data.py        # 数据共享路由 (/api/data)
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
│   │   ├── components/    # Vue组件
│   │   ├── router/        # 路由配置
│   │   ├── store/         # Pinia状态管理
│   │   │   ├── index.js   # Pinia实例创建
│   │   │   ├── auth.js    # 认证状态
│   │   │   ├── files.js   # 文件状态
│   │   │   ├── data.js    # 数据共享状态
│   │   │   └── users.js   # 用户管理状态
│   │   ├── views/         # 页面组件
│   │   ├── App.vue        # 根组件
│   │   ├── main.js        # 入口文件（含axios配置）
│   │   └── style.css      # 全局样式
│   ├── index.html         # HTML模板
│   ├── package.json       # 依赖配置
│   ├── vite.config.js     # Vite配置（含API代理）
│   └── tailwind.config.js # Tailwind CSS配置
├── app.py                 # 主应用入口
├── requirements.txt       # Python依赖
├── README.md              # 项目说明
├── LICENSE                # 许可证
└── .gitignore             # Git忽略文件
```

## 核心配置说明

### 1. 后端配置文件（backend/config.py）

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

### 2. 前端核心配置

#### 2.1 API配置（src/main.js）
```javascript
// 配置axios基础URL，使用相对路径
axios.defaults.baseURL = '/api'
```

#### 2.2 Vite代理配置（vite.config.js）
```javascript
// 已内置代理配置，无需手动修改
// 会自动将/api请求代理到http://localhost:5001
```

#### 2.3 状态管理
- 使用**Pinia**进行状态管理，不是Vuex
- 状态定义在`src/store/`目录下的各个模块文件中

## 开发注意事项

### 1. API请求格式

所有API请求都使用相对路径，例如：
- 用户登录：`POST /api/auth/login`
- 获取文件列表：`GET /api/files`
- 上传文件：`POST /api/files`

### 2. 状态管理

- 使用`useAuthStore()`、`useFilesStore()`等钩子函数访问状态
- 示例：
  ```javascript
  import { useAuthStore } from '../store/auth'
  const authStore = useAuthStore()
  authStore.login(credentials)
  ```

### 3. 数据库迁移

- 系统使用SQLAlchemy ORM，不使用Alembic等迁移工具
- 修改模型后，需要删除旧的数据库表并重新运行应用创建新表
- 生产环境中建议先备份数据再进行模型修改

## 常见问题

### 1. 无法连接到数据库
- 检查数据库服务是否正常运行
- 检查数据库配置是否正确
- 检查数据库用户权限
- 确保已创建所需的数据库

### 2. 文件上传失败
- 检查文件大小是否超过限制（默认100MB）
- 检查上传目录权限
- 检查网络连接

### 3. 前端无法连接到后端
- 确保后端服务正在运行
- 确保前端开发服务器正在运行
- 检查浏览器控制台是否有CORS错误
- 检查Vite代理配置是否正确

### 4. 登录失败
- 检查用户名和密码是否正确
- 检查JWT令牌是否过期
- 检查同一账号是否在其他地方登录

### 5. 数据库排序规则问题
- 系统支持`utf8mb4_general_ci`和`utf8mb4_unicode_ci`排序规则
- 可以根据实际需求在创建数据库时指定
- 不同排序规则可能会影响字符串比较和排序结果

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