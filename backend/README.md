# 校园设备借用与维修管理系统 - 后端

本目录是校园设备借用与维修管理系统的 FastAPI 后端。系统面向学生、管理员和维修人员三类角色，目标是覆盖设备查询、借用归还、损坏报修、维修派单及结果确认等流程。

当前已实现三端账号认证、个人信息维护、设备与分类管理、学生借用申请/归还/报修查询、管理员借用审核与维修工单管理，以及维修人员接单、维修和结果提交。

## 技术栈

- Python 3.10+
- FastAPI + Uvicorn
- SQLAlchemy + PyMySQL
- MySQL
- Pydantic v2 / pydantic-settings
- JWT（PyJWT）+ bcrypt
- fastapi-pagination
- 阿里云 OSS（图片对象存储）

## 项目结构

```text
backend/
├── app/
│   ├── api/          # 路由层，按学生、管理员、维修端划分
│   ├── core/         # 配置、鉴权、日志、异常处理
│   ├── crud/         # 单表数据访问
│   ├── db/           # SQLAlchemy 会话与 ORM 模型
│   ├── result/       # 统一响应结构
│   ├── schema/       # 请求与响应模型、参数校验
│   ├── service/      # 业务逻辑与事务处理
│   └── main.py       # 应用入口与路由注册
├── .env              # 本地环境变量，不应提交真实密钥
├── .env.template     # 环境变量模板
└── README.md
```

## 快速开始

### 1. 创建虚拟环境并安装依赖

在 `backend` 目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install fastapi "uvicorn[standard]" sqlalchemy pymysql pydantic-settings bcrypt PyJWT fastapi-pagination
```

### 2. 配置环境变量

复制 `.env.template` 为 `.env`，填写本地 MySQL 信息和三端独立的 JWT 密钥。令牌有效期须填写整数分钟，例如 `720`，不要使用 `60*12` 这样的表达式。

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-password
DB_DATABASE=campus_equipment_mgr

USER_JWT_SECRET_KEY=replace-with-a-long-random-secret
ADMIN_JWT_SECRET_KEY=replace-with-a-long-random-secret
REPAIR_JWT_SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720
```

数据库使用 MySQL。应用启动时会根据当前 ORM 模型创建缺失的数据表：`user`、`admin`、`repair_user`、`equipment`、`equipment_category`、`borrow_record`、`borrow_return_record`、`borrow_return_image`、`repair_report`、`repair_order`、`repair_order_image`。全新数据库部署后即可使用当前版本的完整表结构。

### 3. 启动服务

```powershell
uvicorn app.main:app --reload
```

默认地址为 `http://127.0.0.1:8000`，启动后可访问：

- OpenAPI 文档：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

## 接口约定

### 统一响应

所有业务接口返回以下结构：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

`code` 为 `0` 表示成功，`1` 表示业务失败。参数校验、未登录和业务异常会使用对应 HTTP 状态码，并保持相同的响应外层结构。

### 鉴权

登录接口返回 JWT。受保护接口使用 HTTP 请求头 `token` 传递令牌，不使用 `Authorization: Bearer` 格式：

```http
token: <login-response.data.token>
```

学生、管理员和维修人员使用彼此独立的 JWT 密钥，因此三个端的令牌不能混用。

学生端的借用记录和报修记录查询会固定使用当前令牌中的用户 ID 过滤，不接受客户端指定其他学生的数据范围。

### 字段命名

接口通过 Pydantic 统一使用驼峰命名输出，例如 `equipmentNo`、`createTime`、`updateTime`。请求参数同时遵循接口模型定义；联调时以 `/docs` 中的 schema 为准。

## 当前接口

### 账号与个人信息

学生、管理员、维修人员的账号接口结构一致，仅路径和鉴权范围不同。

| 方法 | 路径 | 是否鉴权 | 说明 |
| --- | --- | --- | --- |
| POST | `/user/register` | 否 | 学生注册 |
| POST | `/user/login` | 否 | 学生登录，返回学生令牌 |
| GET | `/user/me` | 学生 | 获取当前学生个人信息 |
| PUT | `/user/update` | 学生 | 更新当前学生昵称、密码、头像 |
| POST | `/admin/register` | 否 | 管理员注册 |
| POST | `/admin/login` | 否 | 管理员登录，返回管理员令牌 |
| GET | `/admin/me` | 管理员 | 获取当前管理员个人信息 |
| PUT | `/admin/update` | 管理员 | 更新当前管理员昵称、密码、头像 |
| POST | `/repair/register` | 否 | 维修人员注册 |
| POST | `/repair/login` | 否 | 维修人员登录，返回维修人员令牌 |
| GET | `/repair/me` | 维修人员 | 获取当前维修人员个人信息 |
| PUT | `/repair/update` | 维修人员 | 更新当前维修人员昵称、密码、头像 |

注册和登录请求体：

```json
{
  "username": "student_001",
  "password": "Password123"
}
```

更新个人信息请求体：

```json
{
  "name": "张三",
  "password": "NewPassword123",
  "image": "https://example.com/avatar.png"
}
```

密码在服务端使用 bcrypt 哈希后存储。个人信息更新时的用户 ID 由令牌取得，客户端不能指定其他人的 ID。

### 设备分页查询

三端均可查询设备列表，端点均需使用该端登录后获得的 `token`：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/user/equipment/page` | 学生端设备分页查询 |
| GET | `/admin/equipment/page` | 管理端设备分页查询 |
| GET | `/repair/equipment/page` | 维修端设备分页查询 |

### 设备详情与管理

三端均可根据设备 ID 查询未删除设备的详情，端点均需使用对应端的 `token`：

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/user/equipment/{equipmentId}` | 学生端设备详情 |
| GET | `/admin/equipment/{equipmentId}` | 管理端设备详情 |
| GET | `/repair/equipment/{equipmentId}` | 维修端设备详情 |
| POST | `/admin/equipment/` | 管理端新增设备 |
| PUT | `/admin/equipment/{equipmentId}` | 管理端更新设备，未传字段保持原值 |
| DELETE | `/admin/equipment/{equipmentId}` | 管理端逻辑删除设备 |

新增设备请求体至少包含 `equipmentNo` 和 `equipmentName`。`status` 默认为 `available`；可选状态值为
`available`、`pending_borrow`、`borrowed`、`pending_return`、`damaged`、`repair_pending`、`repairing`、
`repaired`、`scrapped`、`offline`。设备编号全局唯一。

更新设备时，名称、位置、品牌、封面等普通字段按请求更新；维修流程中的设备状态只能通过维修工单接口流转。

### 管理端设备分类

以下接口均需管理员 `token`。删除为逻辑删除，列表与详情不会返回已删除分类。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/admin/equipment-category/page` | 按 ID 或分类名分页查询 |
| GET | `/admin/equipment-category/{categoryId}` | 查询设备分类详情 |
| POST | `/admin/equipment-category/` | 新增设备分类 |
| PUT | `/admin/equipment-category/{categoryId}` | 更新设备分类，未传字段保持原值 |
| DELETE | `/admin/equipment-category/{categoryId}` | 删除设备分类 |

新增请求体中的 `categoryName` 必填，长度为 1-50；`sort` 默认为 `0`，值越小排序越靠前。
分页查询支持 `id`、`categoryName`、`page`、`size`、`sort` 和 `order` 参数，其中 `categoryName` 为模糊匹配。

可用查询参数包括：

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `page` | 页码，范围 1-10000 | `1` |
| `size` | 每页数量，范围 1-100 | `10` |
| `categoryId` | 设备分类 ID | 无 |
| `status` | 设备状态编码，例如 `available` | 无 |
| `equipmentName` / `equipmentNo` | 设备名称或资产编号 | 无 |
| `location` / `brand` / `spec` | 存放位置、品牌、规格型号 | 无 |
| `startTime` / `endTime` | 采购日期范围，格式 `YYYY-MM-DD` | 无 |
| `sort` / `order` | 排序字段与顺序 | `id` / `asc` |

示例：

```http
GET /user/equipment/page?page=1&size=10&status=available&equipmentName=投影仪
token: <student-token>
```

图片通过 `POST /common/upload-image` 上传到阿里云 OSS。服务端根据环境变量校验图片扩展名白名单和文件大小，并生成随机对象名，避免使用客户端原始文件名作为存储对象名。

## 设备状态

设备状态编码与业务含义如下，后续借用和维修流程应以此为准：

| 编码 | 含义 |
| --- | --- |
| `available` | 可借用 |
| `pending_borrow` | 借用审核中 |
| `borrowed` | 已借出 |
| `damaged` | 已损坏 |
| `repair_pending` | 待维修 |
| `repairing` | 维修中 |
| `repaired` | 已维修 |
| `scrapped` | 已报废 |
| `offline` | 已下架 |

## 借用、归还与报修接口

以下接口均返回 `Result` 包装，受保护接口需在请求头携带对应角色的 `token`。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/user/borrow-records` | 学生提交借用申请；校验设备可借和时间冲突后，设备进入 `pending_borrow` |
| GET | `/user/borrow-records/page` | 学生分页查看本人借用记录 |
| GET | `/user/borrow-records/{borrowRecordId}` | 学生查看本人借用记录及完整设备信息 |
| POST | `/user/borrow-records/{borrowRecordId}/return` | 学生提交归还；正常归还直接完成，损坏归还自动创建报修记录和待派单工单 |
| GET | `/user/repair-reports/page` | 学生分页查看本人报修记录 |
| GET | `/user/repair-reports/{repairReportId}` | 学生查看本人报修详情、损坏图片和维修进度 |
| GET | `/admin/borrow-records/page` | 管理员按申请人、设备、状态、关键字和时间范围分页查询全部借用记录 |
| GET | `/admin/borrow-records/{borrowRecordId}` | 管理员查看借用、归还、报修和工单摘要 |
| POST | `/admin/borrow-records/{borrowRecordId}/review` | 管理员审核待审核借用申请 |

借用申请会锁定目标设备，在同一事务中完成可借校验、时间冲突校验、申请创建和设备状态切换，避免并发申请占用重叠时段。审核借用仅允许处理 `pending` 记录：通过后借用记录和设备均变为 `borrowed`，驳回后借用记录为 `rejected`、设备恢复 `available`。学生归还提交后借用记录直接变为 `completed`：正常归还时设备恢复 `available`；损坏归还时同步创建报修记录和待派单工单，设备进入 `repair_pending`。设备状态 `pending_return` 保留为后续扩展状态，不参与当前归还流程。

## 维修工单接口

管理员可确认报修、查询和派发工单、确认维修完成或报废设备；维修人员仅可查询和处理分配给自己的工单。完整字段和状态流转见根目录 [接口文档.md](../接口文档.md)。

## 开发约定

- 路由层只处理 HTTP 输入输出和依赖注入，复杂业务放在 `service`；跨表状态流转与追溯记录由同一事务管理。
- 数据库读写放在 `crud`，跨表操作由 `service` 管理事务。
- 新接口应使用 `Result` 统一返回，使用 Pydantic schema 校验输入输出；响应字段统一采用 camelCase，状态编码转换为中文展示含义。
- 权限依赖使用 `user_verity`、`admin_verity`、`repair_verity`，不得仅依赖前端传入的用户 ID。
- 新增或变更接口后，同步维护 Apifox 接口文档。
- 不要提交 `.env` 中的数据库密码和 JWT 密钥。
