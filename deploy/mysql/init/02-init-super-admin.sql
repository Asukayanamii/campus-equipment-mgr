USE campus_equipment;
SET NAMES utf8mb4;

-- MySQL 初始化脚本先于后端建表执行，因此在此预先创建超级管理员所需的管理员表。
CREATE TABLE IF NOT EXISTS admin (
  id BIGINT NOT NULL AUTO_INCREMENT COMMENT '管理员id',
  name VARCHAR(32) NULL COMMENT '姓名',
  username VARCHAR(32) NOT NULL COMMENT '用户名',
  password VARCHAR(64) NULL COMMENT '密码',
  image VARCHAR(255) NULL,
  email VARCHAR(64) NULL COMMENT '邮箱',
  create_time DATETIME NOT NULL COMMENT '创建时间',
  update_time DATETIME NOT NULL COMMENT '更新时间',
  PRIMARY KEY (id),
  CONSTRAINT username UNIQUE (username)
) COMMENT='管理员表';

-- 密码为 superadmin123 的 bcrypt 哈希；已存在同名账号时不覆盖已有资料和密码。
INSERT IGNORE INTO admin (name, username, password, image, create_time, update_time)
VALUES (
  '超级管理员',
  'superadmin123',
  '$2a$10$RRSWbDbRmlM3BeK6y1CiAetBvIcBvrs/Ne1dRrXsdtQrcLF34zLwC',
  '/assets/images/all-icon..png',
  NOW(),
  NOW()
);
