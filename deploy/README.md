# Docker 部署说明

`deploy` 是可独立复制到 Linux 服务器的部署目录，包含前端静态文件、FastAPI 后端、MySQL 初始化脚本、Nginx 与 Docker Compose 编排。

服务组成：

| 服务 | 说明 |
| --- | --- |
| `frontend` | Nginx：静态页面、`/api` 反向代理、HTTP 跳转 HTTPS |
| `backend` | FastAPI 业务服务 |
| `mysql` | MySQL 8 数据库 |
| `redis` | Redis 7 缓存与验证码存储 |
| `certbot` | Let's Encrypt 免费证书续期检查 |

## 配置

复制环境变量模板并替换所有密码、JWT 密钥、OSS 与 SMTP 配置：

```bash
cp .env.example .env
```

至少修改 `MYSQL_ROOT_PASSWORD`、`MYSQL_PASSWORD`、`REDIS_PASSWORD`、三项 JWT 密钥和 OSS 配置。`HTTP_PORT` 与 `HTTPS_PORT` 默认是 `80`、`443`。

首次启动前，将 `nginx/default.conf` 中的 `asukayanami.top` 与证书路径改为你的域名。域名的 A 记录必须指向服务器公网 IP，且云安全组和服务器防火墙必须允许 TCP `80`、`443`。

## 首次申请免费证书

先使用 HTTP 校验配置启动服务，再申请 Let's Encrypt 证书。以下命令中的域名和邮箱替换为实际值：

```bash
docker compose up -d --build
docker compose run --rm --entrypoint certbot certbot certonly \
  --webroot --webroot-path /var/www/certbot \
  --email admin@example.com --agree-tos --no-eff-email \
  -d example.com -d www.example.com
```

证书签发后，配置 Nginx 的 `443 ssl` server 块并挂载：

```nginx
ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
```

然后重建前端：

```bash
docker compose up -d --build frontend
```

当前仓库已包含 `asukayanami.top` 的 HTTPS 配置和证书卷挂载。复制给其他域名时，必须先按上述流程替换域名与证书路径，否则 Nginx 会因找不到证书而无法启动。

## 日常操作

```bash
# 构建并启动全部服务
docker compose up -d --build

# 查看容器状态
docker compose ps

# 查看后端日志
docker compose logs -f backend

# 验证 Nginx 配置
docker compose exec frontend nginx -t

# 停止服务，保留数据和证书
docker compose down
```

MySQL、Redis、ACME 校验文件和 Let's Encrypt 证书保存在 Docker 命名卷。不要执行 `docker compose down -v`，除非确认需要删除数据库、Redis 数据和证书。

## 初始化账号

首次创建 MySQL 数据卷时，`mysql/init/02-init-super-admin.sql` 会创建超级管理员：

```text
用户名：superadmin123
密码：superadmin123
```

初始化脚本只在空 MySQL 数据卷时执行。生产部署后应立即修改密码。

## HTTPS 续期

`certbot` 每 12 小时执行一次 `certbot renew`。续期成功时会向前端 Nginx 发送热重载信号，无需人工重启容器。可用以下命令检查：

```bash
docker compose logs --tail 100 certbot
```
