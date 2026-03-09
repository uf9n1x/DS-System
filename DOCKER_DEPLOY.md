# DS-System Docker 部署指南

## 目录结构

部署所需的Docker相关文件结构如下：

```
DS-System/
├── docker/
│   ├── nginx/
│   │   ├── nginx.conf           # Nginx主配置
│   │   └── conf.d/
│   │       └── default.conf     # 站点配置
│   └── mysql/
│       ├── init/
│       │   └── 01-init-databases.sql  # 数据库初始化脚本
│       └── conf.d/
│           └── my.cnf           # MySQL自定义配置
├── Dockerfile                   # Docker镜像构建文件
├── docker-compose.yml           # Docker Compose编排文件
├── .dockerignore               # Docker构建忽略文件
└── .env.example                # 环境变量示例
```

---

## 一、断网环境部署方案

### 方案A：镜像导出导入（推荐）

在有网络的机器上完成镜像构建后，导出镜像传输到内网服务器。

#### 步骤1：在有网环境构建镜像

```bash
# 1. 进入项目目录
cd DS-System

# 2. 构建镜像
docker build -t ds-system:latest .

# 3. 导出镜像为tar文件
docker save -o ds-system-latest.tar ds-system:latest

# 4. 同时准备MySQL和Nginx镜像
docker pull mysql:8.0
docker pull nginx:alpine
docker save -o mysql-8.0.tar mysql:8.0
docker save -o nginx-alpine.tar nginx:alpine
```

#### 步骤2：传输文件到内网服务器

将以下文件传输到内网服务器：
- `ds-system-latest.tar`
- `mysql-8.0.tar`
- `nginx-alpine.tar`
- 整个 `DS-System` 项目目录

#### 步骤3：在内网服务器加载镜像

```bash
# 加载镜像
docker load -i ds-system-latest.tar
docker load -i mysql-8.0.tar
docker load -i nginx-alpine.tar

# 验证镜像已加载
docker images
```

### 方案B：离线构建包

如果内网服务器有Docker但无网络，可使用此方案：

```bash
# 在有网环境执行
# 下载所有依赖到本地
pip download -r requirements.txt -d ./pip-packages
cd frontend && npm install && cd ..

# 打包整个项目（包含依赖）
tar -czvf ds-system-offline.tar.gz DS-System/
```

---

## 二、部署操作步骤

### 步骤1：准备配置文件

```bash
# 1. 进入项目目录
cd DS-System

# 2. 复制环境变量示例文件
cp .env.example .env

# 3. 编辑配置（重要！）
# 修改数据库密码、JWT密钥等敏感信息
vim .env
```

**.env 配置说明：**

| 配置项 | 说明 | 默认值 | 是否必须修改 |
|--------|------|--------|--------------|
| DB_PASSWORD | MySQL root密码 | root123456 | **是** |
| JWT_SECRET_KEY | JWT加密密钥 | - | **是** |
| SECRET_KEY | Flask密钥 | - | **是** |
| NGINX_PORT | Web访问端口 | 80 | 否 |
| MYSQL_PORT | MySQL端口 | 3306 | 否 |

### 步骤2：启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 步骤3：验证部署

```bash
# 1. 检查容器状态
docker-compose ps

# 预期输出：
# NAME        STATUS    PORTS
# ds-mysql    running   0.0.0.0:3306->3306/tcp
# ds-app      running   0.0.0.0:5001->5001/tcp
# ds-nginx    running   0.0.0.0:80->80/tcp

# 2. 检查健康状态
docker inspect --format='{{.State.Health.Status}}' ds-mysql
docker inspect --format='{{.State.Health.Status}}' ds-app

# 3. 访问测试
curl http://localhost/health
```

### 步骤4：访问系统

浏览器访问：`http://服务器IP`

默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`

**重要：首次登录后请立即修改密码！**

---

## 三、常用运维命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重启单个服务
docker-compose restart app

# 查看日志
docker-compose logs -f app
docker-compose logs -f mysql
docker-compose logs -f nginx

# 进入容器
docker exec -it ds-app bash
docker exec -it ds-mysql mysql -uroot -p
```

### 数据管理

```bash
# 备份数据库
docker exec ds-mysql mysqldump -uroot -p${DB_PASSWORD} webtools > webtools_backup.sql
docker exec ds-mysql mysqldump -uroot -p${DB_PASSWORD} datashare > datashare_backup.sql

# 恢复数据库
docker exec -i ds-mysql mysql -uroot -p${DB_PASSWORD} webtools < webtools_backup.sql

# 查看数据卷
docker volume ls

# 清理未使用的数据卷
docker volume prune
```

### 更新部署

```bash
# 1. 拉取最新代码（如有）
git pull

# 2. 重新构建镜像
docker-compose build --no-cache

# 3. 停止并删除旧容器
docker-compose down

# 4. 启动新容器
docker-compose up -d

# 5. 清理旧镜像
docker image prune -f
```

---

## 四、故障排查

### 问题1：容器启动失败

```bash
# 查看详细日志
docker-compose logs app

# 检查配置文件
docker-compose config

# 检查容器状态
docker ps -a
```

### 问题2：数据库连接失败

```bash
# 检查MySQL是否就绪
docker exec ds-mysql mysqladmin ping -h localhost -uroot -p

# 检查网络连接
docker exec ds-app ping mysql

# 检查环境变量
docker exec ds-app env | grep DB_
```

### 问题3：前端页面无法访问

```bash
# 检查Nginx配置
docker exec ds-nginx nginx -t

# 检查Nginx日志
docker-compose logs nginx

# 检查后端服务
curl http://localhost:5001/
```

### 问题4：文件上传失败

```bash
# 检查上传目录权限
docker exec ds-app ls -la /app/backend/uploads

# 检查磁盘空间
df -h

# 检查数据卷
docker volume inspect ds-uploads-data
```

---

## 五、安全加固建议

### 1. 修改默认密码

```bash
# 登录后立即修改admin密码
# 或通过数据库修改
docker exec -it ds-mysql mysql -uroot -p
```

```sql
USE webtools;
UPDATE users SET password_hash='新密码的hash值' WHERE username='admin';
```

### 2. 修改密钥

在 `.env` 文件中设置强密钥：

```bash
# 生成随机密钥
openssl rand -hex 32
```

### 3. 防火墙配置

```bash
# 仅开放必要端口
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --reload

# 或使用iptables
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
```

### 4. 限制MySQL外网访问

修改 `docker-compose.yml`，移除MySQL端口映射：

```yaml
mysql:
  # 注释掉端口映射，仅允许内部访问
  # ports:
  #   - "${MYSQL_PORT:-3306}:3306"
```

---

## 六、性能优化

### 1. MySQL优化

编辑 `docker/mysql/conf.d/my.cnf`：

```ini
[mysqld]
# 根据服务器内存调整
innodb_buffer_pool_size=1G
innodb_log_file_size=256M
max_connections=500
```

### 2. Nginx优化

编辑 `docker/nginx/nginx.conf`：

```nginx
worker_processes auto;  # 自动匹配CPU核心数
worker_connections 2048;  # 增加连接数
```

### 3. 应用优化

考虑使用Gunicorn运行Flask：

```bash
# 安装Gunicorn
pip install gunicorn

# 启动命令
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

---

## 七、快速命令参考

| 操作 | 命令 |
|------|------|
| 启动服务 | `docker-compose up -d` |
| 停止服务 | `docker-compose down` |
| 重启服务 | `docker-compose restart` |
| 查看日志 | `docker-compose logs -f` |
| 查看状态 | `docker-compose ps` |
| 进入容器 | `docker exec -it ds-app bash` |
| 备份数据库 | `docker exec ds-mysql mysqldump -uroot -p webtools > backup.sql` |
| 重建镜像 | `docker-compose build --no-cache` |

---

## 八、联系支持

如有问题，请检查日志文件：
- 应用日志：`app.log`
- Nginx日志：`docker-compose logs nginx`
- MySQL日志：`docker-compose logs mysql`
