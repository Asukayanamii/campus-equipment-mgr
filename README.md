# 校园设备借用与维修管理系统

面向学生、管理员和维修人员的前后端分离设备管理系统。项目覆盖设备查询与管理、借用申请、归还验收、损坏报修和维修流程的基础能力。

当前仓库已包含学生借还、损坏报修、管理员派单和维修结果确认的完整基础流程；

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
└── 暑期考核项目文档.txt         # 原始项目需求
```

## 当前功能

| 角色 | 已完成能力 |
| --- | --- |
| 学生 | 注册登录、设备与详情查询、本人借用记录和报修记录查询、提交归还 |
| 管理员 | 设备与设备分类管理、借用审核、报修确认、工单派发、维修确认和设备报废 |
| 维修人员 | 注册登录、设备查询、个人信息维护、本人工单接收、维修和结果提交 |

已实现的核心业务保障：

- 借用申请锁定设备行，并校验同一设备的借用时间冲突。
- 损坏归还在同一事务中创建报修记录和待派单工单。
- 借用审核、归还提交和设备状态变更在同一事务中完成。
- 三端使用独立 JWT 密钥；学生借用与报修数据按当前登录用户隔离。
- 图片上传接入阿里云 OSS，并校验扩展名白名单和文件大小。

后端进阶能力：

- Redis 设备查询缓存：设备分页和详情查询使用带参数摘要、版本号命名空间和 TTL 的缓存；设备或分类事务提交后递增版本号，避免旧数据继续命中。Redis 不可用时自动回源数据库。
- 邮箱验证码安全机制：验证码使用随机六位数字生成，bcrypt 哈希后写入 Redis；`SET NX` 限制有效期内重复发送，校验成功后立即删除，配合 SMTP 完成邮箱注册/登录。
- OSS 对象存储：头像、设备图片、损坏凭证和维修前后图片只在业务表保存 URL，文件统一上传阿里云 OSS；服务端校验扩展名、MIME 类型和大小。
- 并发借用保护：借用申请在事务内使用数据库行级锁校验设备状态和时间冲突；归还、报修、工单和设备状态同步提交，避免超卖和脏状态。

前端体验增强：

- 使用原生 JavaScript 按角色动态渲染学生、管理员和维修人员页面，减少页面之间的重复结构。
- 设备、分类、借用记录和报修记录支持条件筛选、联查、重置搜索和分页，分页状态按业务视图独立维护。
- 设备卡片支持悬浮查看详情；个人资料、设备编辑、记录详情使用动态弹窗和遮罩层，完成后端数据的即时回显。
- 使用原生 CSS 提供卡片悬浮、按钮过渡、淡入和响应式布局，并在减少动态效果偏好下自动降低动画强度。
- `dev-frontend` 分支进一步重构登录页和主页视觉：增加角色选择状态、管理员注册码输入区域、登录/注册交互提示、背景与卡片动效，并优化不同屏幕尺寸下的布局。

需求文档中规划的前端进阶加分项（设备瀑布流与滚动懒加载、热门设备/搜索词推荐、多图轮播与放大预览）当前版本尚未实现，现有图片能力主要由后端 OSS 上传接口和前端 URL 展示组成。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端 | 原生 HTML、CSS、JavaScript、Fetch API |
| 后端 | Python、FastAPI、SQLAlchemy、Pydantic v2 |
| 数据库 | MySQL、PyMySQL |
| 鉴权 | JWT、bcrypt |
| 文件存储 | 阿里云 OSS |
| 缓存与验证码 | Redis、SMTP |

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
