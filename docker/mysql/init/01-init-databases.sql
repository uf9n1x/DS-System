# ============================================
# MySQL 初始化脚本
# 创建所需的数据库
# ============================================

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 创建主数据库（webtools）
CREATE DATABASE IF NOT EXISTS webtools 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 创建数据共享数据库（datashare）
CREATE DATABASE IF NOT EXISTS datashare 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 授权（可选，根据需要调整）
-- GRANT ALL PRIVILEGES ON webtools.* TO 'root'@'%';
-- GRANT ALL PRIVILEGES ON datashare.* TO 'root'@'%';
-- FLUSH PRIVILEGES;

-- 输出创建结果
SELECT 'Database webtools created successfully.' AS Result;
SELECT 'Database datashare created successfully.' AS Result;
