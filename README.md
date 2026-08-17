# 校园设备管理系统

面向学生、管理员和维修人员的校园设备借用、归还与维修管理系统。项目采用前后端分离架构：前端使用原生 HTML、CSS、JavaScript，后端基于 FastAPI，并使用 MySQL、Redis、阿里云 OSS 和 SMTP 完成业务支撑。

线上地址：[https://asukayanami.top](https://asukayanami.top)

## 核心能力

| 角色 | 功能 |
| --- | --- |
| 学生 | 用户名密码注册登录、邮箱验证码注册登录、绑定邮箱、设备与分类查询、借用申请、归还、报修、个人记录查询 |
| 管理员 | 设备与分类维护、借用审核、报修确认、维修工单派发与确认、设备状态管理、操作日志查询 |
| 超级管理员 | 管理员能力，以及管理员/维修员注册码的创建、更新、重置使用状态和删除 |
| 维修人员 | 设备与分类查询、接单、维修处理、维修结果提交、本人维修工单操作历史查询 |

## 业务与技术设计

- 借用申请在数据库事务内使用 `SELECT ... FOR UPDATE` 锁定设备行，校验设备状态与时间冲突，避免并发超借。
- 设备分页与详情查询使用 Redis 缓存。缓存键带版本号，设备或分类事务提交后更新版本，旧缓存自动失效；Redis 不可用时回源 MySQL。
- 邮箱验证码使用随机六位数字、bcrypt 哈希、Redis `SET NX` 和可配置 TTL；登录注册与邮箱绑定使用不同 Redis 键前缀隔离。
- 图片上传至阿里云 OSS，后端校验文件类型、扩展名与大小。未传设备封面时使用本地默认图片 `/assets/images/all-icon..png`。
- 审核、状态变更和设备创建会写入操作日志，便于管理员审计及维修人员查看工单历史。
- 三端 JWT 使用独立密钥；鉴权范围由后端控制，前端不保存角色字段。

## 技术栈

| 分类 | 技术 |
| --- | --- |
| 前端 | 原生 HTML、CSS、JavaScript、Fetch API |
| 后端 | Python 3.13、FastAPI、Pydantic v2、SQLAlchemy |
| 数据库 | MySQL 8 |
| 缓存 | Redis 7 |
| 认证 | JWT、bcrypt |
| 外部服务 | 阿里云 OSS、SMTP、Let's Encrypt |
| 部署 | Docker Compose、Nginx、Certbot |

## 项目结构

```text
campus-equipment-mgr/
├── frontend/       # 前端静态页面、样式、脚本与资源
├── backend/        # FastAPI 应用、模型、业务服务和测试
├── deploy/         # 可独立复制到服务器的 Docker Compose 部署目录
├── 接口文档.md      # 接口说明
└── 暑期考核项目文档.txt
```

## 本地开发

### 后端

在 `backend` 目录创建或激活 Conda 环境，配置 `.env` 后启动服务：

```powershell
conda env create -f environment.yml
conda activate campus-equipment-mgr
Copy-Item .env.template .env
uvicorn app.main:app --reload
```

后端默认地址为 `http://127.0.0.1:8000`，OpenAPI 文档为 `http://127.0.0.1:8000/docs`。配置项见 [后端 README](./backend/README.md)。

### 前端

前端无需 Node.js 构建。开发联调时，设置 `window.API_BASE` 为后端地址，或在 `frontend/js/api.js` 中将默认接口地址改为 `http://127.0.0.1:8000`。从项目父目录启动静态服务：

```powershell
cd ..
python -m http.server 5500
```

访问 `http://127.0.0.1:5500/campus-equipment-mgr/frontend/`。

## Docker 部署

`deploy` 目录包含前端静态资源、后端代码、MySQL 初始化脚本、Nginx 和 Docker Compose 配置。复制整个目录到服务器后，按 [部署 README](./deploy/README.md) 配置环境变量、申请证书并启动容器。

生产环境由 Nginx 统一提供静态页面与 `/api` 反向代理，HTTP 自动跳转 HTTPS。MySQL、Redis 和 Let's Encrypt 证书使用 Docker 命名卷持久化。

## 测试

后端语法检查：

```powershell
cd backend
python -m compileall -q app
```

端到端接口测试需要先启动本地后端和 MySQL：

```powershell
python -m unittest tests.test_api_contract_and_flow
```

## 相关文档

- [后端说明](./backend/README.md)
- [前端说明](./frontend/README.md)
- [Docker 部署说明](./deploy/README.md)
- [接口文档](./接口文档.md)
