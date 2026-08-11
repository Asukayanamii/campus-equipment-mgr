# 校园设备借用与维修管理系统

面向学生、管理员和维修人员的前后端分离设备管理系统。项目覆盖设备查询与管理、借用申请、归还验收、损坏报修和维修流程的基础能力。

当前仓库已合并前端和后端第一版，可用于前后端联调；未完成的维修工单处理能力见 [接口文档.md](./接口文档.md)。

## 项目结构

```text
campus-equipment-mgr/
├── frontend/                 # 原生 HTML、CSS、JavaScript 前端
│   ├── index.html             # 前端入口
│   ├── login.html             # 三角色登录页
│   ├── pages/                 # 学生、管理员、维修人员页面
│   ├── js/api.js              # 后端接口与 BASE_URL 配置
│   └── css/                   # 页面样式
├── backend/                   # FastAPI 后端
│   ├── app/                   # 路由、业务服务、CRUD、ORM 模型
│   ├── requirements.txt       # Python 依赖
│   ├── environment.yml        # Conda 环境定义
│   └── README.md              # 后端详细说明
├── 接口文档.md                 # 接口需求与实现状态
└── 暑期考核项目文档.txt         # 原始项目需求
```

## 当前功能

| 角色 | 已完成能力 |
| --- | --- |
| 学生 | 注册登录、设备与详情查询、本人借用记录和报修记录查询、提交归还 |
| 管理员 | 设备与设备分类管理、查看全部借用记录、审核借用申请 |
| 维修人员 | 注册登录、设备查询和个人信息维护；工单处理流程待实现 |

已实现的核心业务保障：

- 借用申请锁定设备行，并校验同一设备的借用时间冲突。
- 损坏归还创建报修记录，维修工单由管理员后续创建。
- 借用审核、归还提交和设备状态变更在同一事务中完成。
- 三端使用独立 JWT 密钥；学生借用与报修数据按当前登录用户隔离。
- 图片上传接入阿里云 OSS，并校验扩展名白名单和文件大小。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端 | 原生 HTML、CSS、JavaScript、Fetch API |
| 后端 | Python、FastAPI、SQLAlchemy、Pydantic v2 |
| 数据库 | MySQL、PyMySQL |
| 鉴权 | JWT、bcrypt |
| 文件存储 | 阿里云 OSS |

## 快速启动

### 1. 启动后端

要求：Python 3.10+、MySQL。进入后端目录后安装依赖：

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

复制 `backend/.env.template` 为 `backend/.env`，填写 MySQL、JWT 和 OSS 配置。然后启动服务：

```powershell
uvicorn app.main:app --reload
```

默认后端地址为 `http://127.0.0.1:8000`，接口文档为 `http://127.0.0.1:8000/docs`。

> 使用已有数据库升级时，`Base.metadata.create_all()` 不会删除列；请执行 [归还确认字段迁移](./backend/migrations/20260810_remove_borrow_return_confirmation_fields.sql)。

### 2. 配置前端接口地址

前端不需要 Node.js 或构建命令。接口基地址位于 [frontend/js/api.js](./frontend/js/api.js)：

```js
const BASE_URL = `https://frp-put.com:58235`
```

该值当前为外网联调地址。本地联调时改为：

```js
const BASE_URL = `http://127.0.0.1:8000`
```

### 3. 启动前端静态服务

前端登录后的页面跳转使用 `/campus-equipment-mgr/frontend/...` 路径，因此从项目父目录启动静态服务：

```powershell
cd ..
python -m http.server 5500
```

浏览器访问：

```text
http://127.0.0.1:5500/campus-equipment-mgr/frontend/
```

## 联调约定

- 受保护接口通过请求头传递令牌：`token: <jwt>`。
- 后端统一返回 `Result`：`code=0` 表示成功，`data` 为响应数据。
- 请求和响应字段使用 camelCase；后端响应中的状态字段会转换为中文展示含义。
- 后端已开启开发环境跨域支持；本地前端静态服务可以直接请求后端。

## 借用状态流转

```text
available
  -> pending_borrow    学生提交借用申请
  -> borrowed          管理员审核通过
  -> completed         学生提交归还
  -> available         正常归还
  -> repair_pending    损坏归还
```

借用审核驳回时，借用记录变为 `rejected`，设备恢复 `available`。设备状态 `pending_return` 作为后续扩展预留，不参与当前归还流程。

## 相关文档

- [后端说明](./backend/README.md)
- [前端说明](./frontend/README.md)
