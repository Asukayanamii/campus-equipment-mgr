# 后端说明

本目录是校园设备管理系统的 FastAPI 服务。路由层负责 HTTP 参数、鉴权依赖与响应；`service` 层处理业务规则和事务；`crud` 层封装单表数据访问。

## 目录结构

```text
backend/
├── app/
│   ├── api/          # user、admin、repair、common 路由
│   ├── constant/     # 状态、操作类型等常量
│   ├── core/         # 配置、JWT 鉴权、日志、异常处理
│   ├── crud/         # 数据访问
│   ├── db/           # SQLAlchemy 模型与会话
│   ├── schema/       # Pydantic 请求/响应模型
│   ├── service/      # 业务逻辑、事务、缓存失效和操作日志
│   └── main.py       # 应用入口
├── tests/            # 接口与流程测试
├── .env.template     # 本地配置模板
├── environment.yml   # Conda 环境定义
└── requirements.txt
```

## 环境与启动

推荐使用仓库提供的 Conda 环境：

```powershell
conda env create -f environment.yml
conda activate campus-equipment-mgr
Copy-Item .env.template .env
uvicorn app.main:app --reload
```

也可以使用已有 Python 环境安装依赖：

```powershell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

服务地址：`http://127.0.0.1:8000`

OpenAPI：`http://127.0.0.1:8000/docs`

应用启动时会按 SQLAlchemy 模型创建缺失表，不会删除或迁移已有数据。

## 配置

`.env` 不应提交真实密码、JWT 密钥、SMTP 授权码或 OSS AccessKey。最小配置示例：

```dotenv
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=campus_app
DB_PASSWORD=replace-with-password
DB_DATABASE=campus_equipment

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=replace-with-password
EQUIPMENT_QUERY_CACHE_TTL=300

USER_JWT_SECRET_KEY=replace-with-random-secret
ADMIN_JWT_SECRET_KEY=replace-with-random-secret
REPAIR_JWT_SECRET_KEY=replace-with-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=720

MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-smtp-authorization-code
MAIL_FROM=your-email@example.com
MAIL_SERVER=smtp.example.com
MAIL_PORT=465
MAIL_SSL_TLS=true
EMAIL_VERIFICATION_CODE_EXPIRE_SECONDS=60

ALIYUN_OSS_ACCESS_KEY_ID=your-access-key-id
ALIYUN_OSS_ACCESS_KEY_SECRET=your-access-key-secret
ALIYUN_OSS_REGION=cn-hangzhou
ALIYUN_OSS_BUCKET_NAME=your-bucket-name
IMAGE_MAX_SIZE=5
IMAGE_ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,webp
IMAGE_ALLOWED_CONTENT_TYPES=image/jpeg,image/png,image/gif,image/webp
DEFAULT_EQUIPMENT_IMAGE_URL=/assets/images/all-icon..png
DEFAULT_PROFILE_IMAGE_URL=/assets/images/all-icon..png
SUPER_ADMIN_USERNAME=superadmin123
```

`ACCESS_TOKEN_EXPIRE_MINUTES` 必须是整数，例如 `720`，不能填写 `60*12`。SMTP 未配置时仅邮箱验证码功能不可用；OSS 未配置时图片上传不可用。

## 接口约定

- 接口默认根路径为 `/`；容器部署通过 Nginx 的 `/api` 转发，因此线上接口地址为 `/api/<path>`。
- 统一响应格式为 `{"code": 0, "message": "success", "data": ...}`。`code=0` 表示成功。
- Pydantic 使用 camelCase 输出字段，例如 `equipmentNo`、`createTime`。
- 受保护接口的请求头使用 `token: <jwt>`，不是 `Authorization: Bearer`。
- 学生、管理员、维修人员的 JWT 密钥相互隔离，错误角色令牌会被后端拒绝。

## 主要接口分组

| 分组 | 前缀 | 主要能力 |
| --- | --- | --- |
| 学生 | `/user` | 用户名登录、邮箱验证码登录、邮箱绑定、资料更新、设备/分类、借用、归还、报修 |
| 管理员 | `/admin` | 登录、设备/分类、借用审核、报修确认、工单、维修员、注册码、操作日志 |
| 维修人员 | `/repair` | 登录、设备/分类、本人维修工单及工单日志 |
| 通用 | `/common` | 三端鉴权后的图片上传 |

完整请求字段和响应模型以 `/docs` 为准。根目录的 [接口文档.md](../接口文档.md) 提供联调参考。

## 关键规则

- 设备编号和未删除分类名称唯一；设备封面缺省时使用 `DEFAULT_EQUIPMENT_IMAGE_URL`。
- 设备查询缓存使用版本号命名空间；设备或分类变更提交后使缓存版本递增。Redis 故障时自动查询 MySQL。
- 借用申请在事务中锁定设备行，并校验状态与时间区间冲突。
- 个人资料未传密码字段时可更新普通资料；修改密码必须同时传原密码和新密码，后端校验原密码后才更新。
- 绑定邮箱仅允许未绑定账号发起。绑定验证码与邮箱注册登录验证码使用不同 Redis 键，成功验证后立即删除。
- 管理员和维修员注册均需对应类型的注册码；注册码仅由超级管理员管理。
- 管理员仅能在 `available` 与 `offline` 间切换设备状态；借用、归还和维修状态只能由对应业务流程流转，并写入操作日志。

## 开发规范

- 路由层不承载跨表业务判断；事务、状态流转、缓存失效和日志记录放在 `service` 层。
- CRUD 模块只负责数据访问，输入输出由 schema 校验。
- 新增状态、操作类型等固定值应写入常量类，不散落硬编码字符串。
- 新增业务逻辑使用中文注释说明关键约束和事务原因。
- 不提交 `.env`、测试账号密码、OSS 凭据或邮件授权码。

## 测试

```powershell
python -m compileall -q app
python -m unittest tests.test_api_contract_and_flow
```

第二条命令会请求运行在 `http://127.0.0.1:8000` 的服务，并写入、清理带测试前缀的数据。可通过 `CAMPUS_TEST_BASE_URL` 改写服务地址。
