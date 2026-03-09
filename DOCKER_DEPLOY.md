# DS-System 断网环境完整部署指南（远程数据库版）

## 📋 目录

- [第一阶段：有网环境准备](#第一阶段有网环境准备)
- [第二阶段：文件传输](#第二阶段文件传输)
- [第三阶段：远程数据库准备](#第三阶段远程数据库准备)
- [第四阶段：内网服务器部署](#第四阶段内网服务器部署)
- [第五阶段：验证与测试](#第五阶段验证与测试)
- [常见问题排查](#常见问题排查)

---

## 第一阶段：有网环境准备

### 1.1 环境要求

**有网机器需要安装：**
- Docker（版本 20.10+）

**内网服务器需要安装：**
- Docker（版本 20.10+）
- Docker Compose（版本 2.0+）

**远程MySQL数据库要求：**
- MySQL 5.7+ 或 MySQL 8.0+
- 允许内网服务器IP访问

### 1.2 获取项目代码

```bash
# 克隆或下载项目
git clone https://github.com/uf9n1x/DS-System.git
cd DS-System
```

### 1.3 拉取基础镜像

```bash
# 拉取所需的基础镜像
docker pull node:20-alpine
docker pull python:3.11-slim
docker pull nginx:alpine
```

### 1.4 构建应用镜像

```bash
# 在项目根目录执行
docker build -t ds-system:latest .
```

### 1.5 导出所有镜像

```bash
# 创建导出目录
mkdir -p docker-images

# 导出镜像（仅需3个，不需要MySQL）
docker save -o docker-images/ds-system-latest.tar ds-system:latest
docker save -o docker-images/nginx-alpine.tar nginx:alpine
docker save -o docker-images/node-20-alpine.tar node:20-alpine
docker save -o docker-images/python-3.11-slim.tar python:3.11-slim
```

### 1.6 准备传输文件清单

```
传输包/
├── docker-images/
│   ├── ds-system-latest.tar      # 应用镜像
│   ├── nginx-alpine.tar          # Nginx镜像
│   ├── node-20-alpine.tar        # Node镜像（备用）
│   └── python-3.11-slim.tar      # Python镜像（备用）
│
└── DS-System/                     # 项目完整目录
    ├── docker/
    │   └── nginx/
    │       ├── nginx.conf
    │       └── conf.d/
    │           └── default.conf
    ├── Dockerfile
    ├── docker-compose.remote-db.yml   # ⭐ 使用这个配置文件
    ├── .dockerignore
    ├── .env.example
    ├── requirements.txt
    ├── app.py
    ├── backend/
    └── frontend/
```

### 1.7 打包传输文件

```bash
# 返回上级目录
cd ..

# 打包所有文件
tar -czvf ds-system-deploy.tar.gz docker-images/ DS-System/
```

---

## 第二阶段：文件传输

### 2.1 传输方式

| 方式 | 适用场景 |
|------|---------|
| U盘/移动硬盘 | 物理距离近 |
| FTP/SFTP | 网络传输 |
| SCP | Linux服务器间 |

### 2.2 传输到内网服务器

```bash
# 使用SCP示例
scp ds-system-deploy.tar.gz user@内网服务器IP:/home/user/
```

---

## 第三阶段：远程数据库准备

### 3.1 连接远程MySQL

```bash
# 使用MySQL客户端连接
mysql -h 远程数据库IP -u root -p
```

### 3.2 创建所需数据库

```sql
-- 创建主数据库（系统数据）
CREATE DATABASE webtools 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 创建数据共享数据库
CREATE DATABASE datashare 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 验证创建结果
SHOW DATABASES;
```

### 3.3 创建应用专用用户（推荐）

```sql
-- 创建用户（替换为实际的用户名和密码）
CREATE USER 'ds_user'@'%' IDENTIFIED BY 'your_password';

-- 授权
GRANT ALL PRIVILEGES ON webtools.* TO 'ds_user'@'%';
GRANT ALL PRIVILEGES ON datashare.* TO 'ds_user'@'%';
FLUSH PRIVILEGES;
```

### 3.4 配置远程访问权限

确保MySQL配置允许内网服务器访问：

```bash
# 检查MySQL配置文件 /etc/mysql/mysql.conf.d/mysqld.cnf
# 注释掉或修改 bind-address
# bind-address = 127.0.0.1  改为
bind-address = 0.0.0.0

# 重启MySQL服务
systemctl restart mysql
```

### 3.5 验证网络连通性

在内网服务器上测试：

```bash
# 测试MySQL端口连通性
telnet 远程数据库IP 3306

# 或使用nc
nc -zv 远程数据库IP 3306
```

---

## 第四阶段：内网服务器部署

### 4.1 解压文件

```bash
# 解压
tar -xzvf ds-system-deploy.tar.gz

# 进入项目目录
cd DS-System
```

### 4.2 加载Docker镜像

```bash
# 加载镜像
docker load -i ../docker-images/ds-system-latest.tar
docker load -i ../docker-images/nginx-alpine.tar

# 验证
docker images
```

### 4.3 创建配置文件

```bash
# 复制环境变量示例
cp .env.example .env

# 编辑配置
vim .env
```

**⚠️ 必须修改的配置项：**

```env
# ==================== 远程数据库配置 ====================
DB_USER=root                          # 数据库用户名
DB_PASSWORD=123456                    # 数据库密码
DB_HOST=192.168.1.100                 # ⭐ 远程数据库IP
DB_PORT=3306
DB_NAME=webtools
DATASHARE_DB_NAME=datashare

# ==================== 安全配置 ====================
JWT_SECRET_KEY=请替换为32位随机字符串
SECRET_KEY=请替换为32位随机字符串

# ==================== 端口配置 ====================
NGINX_PORT=80                         # Web访问端口
```

### 4.4 启动服务

```bash
# ⭐ 使用远程数据库配置文件启动
docker-compose -f docker-compose.remote-db.yml up -d

# 查看启动日志
docker-compose -f docker-compose.remote-db.yml logs -f
```

### 4.5 检查服务状态

```bash
# 查看容器状态
docker-compose -f docker-compose.remote-db.yml ps
```

预期输出：
```
NAME        STATUS              PORTS
ds-app      running (healthy)   0.0.0.0:5001->5001/tcp
ds-nginx    running (healthy)   0.0.0.0:80->80/tcp
```

---

## 第五阶段：验证与测试

### 5.1 检查数据库连接

```bash
# 查看应用日志，确认数据库连接成功
docker-compose -f docker-compose.remote-db.yml logs app | grep -i database
```

预期看到：
```
数据库表创建成功!
默认管理员用户创建成功!
```

### 5.2 浏览器访问

```
http://内网服务器IP
```

### 5.3 登录测试

- 用户名：`admin`
- 密码：`admin123`

---

## 常见问题排查

### 问题1：数据库连接失败

```bash
# 检查网络连通性
docker exec ds-app ping 远程数据库IP

# 检查MySQL端口
docker exec ds-app nc -zv 远程数据库IP 3306

# 检查环境变量
docker exec ds-app env | grep DB_
```

**解决方案：**
1. 确认远程MySQL允许外部连接
2. 确认防火墙开放3306端口
3. 确认用户名密码正确

### 问题2：防火墙问题

**远程MySQL服务器端：**
```bash
# 开放MySQL端口
firewall-cmd --permanent --add-port=3306/tcp
firewall-cmd --reload

# 或 iptables
iptables -A INPUT -p tcp --dport 3306 -j ACCEPT
```

**内网服务器端：**
```bash
# 开放Web端口
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --reload
```

### 问题3：MySQL用户权限问题

```sql
-- 检查用户权限
SHOW GRANTS FOR 'root'@'%';

-- 如果没有权限，添加
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

---

## 运维命令速查

| 操作 | 命令 |
|------|------|
| 启动服务 | `docker-compose -f docker-compose.remote-db.yml up -d` |
| 停止服务 | `docker-compose -f docker-compose.remote-db.yml down` |
| 重启服务 | `docker-compose -f docker-compose.remote-db.yml restart` |
| 查看日志 | `docker-compose -f docker-compose.remote-db.yml logs -f` |
| 查看状态 | `docker-compose -f docker-compose.remote-db.yml ps` |

---

## 部署完成检查清单

- [ ] 远程MySQL已创建 webtools 和 datashare 数据库
- [ ] 远程MySQL允许内网服务器IP访问
- [ ] Docker镜像已加载
- [ ] .env 配置文件已修改（DB_HOST指向远程数据库）
- [ ] 容器状态为 healthy
- [ ] 浏览器可访问系统
- [ ] 可使用 admin/admin123 登录
