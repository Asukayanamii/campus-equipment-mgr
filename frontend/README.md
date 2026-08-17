# 前端说明

前端使用原生 HTML、CSS 和 JavaScript 实现，不依赖 Node.js、打包器或前端框架。页面通过 Fetch API 调用 FastAPI 接口，并按学生、管理员、维修人员三类身份渲染业务视图。

## 入口与页面

| 文件 | 说明 |
| --- | --- |
| `index.html` | 系统首页 |
| `login.html` | 三端登录与注册入口；学生支持邮箱验证码登录 |
| `pages/user.html` | 学生端设备、借用、归还、报修与个人资料 |
| `pages/admin.html` | 管理端设备、分类、审核、工单、注册码与日志 |
| `pages/repair.html` | 维修端工单、设备查询和维修操作历史 |

## 目录结构

```text
frontend/
├── assets/        # 图标与本地默认图片
├── css/           # 通用样式和三端业务样式
├── js/
│   ├── api.js     # 接口请求、令牌处理和通用错误处理
│   ├── login.js   # 登录、注册、学生邮箱验证码登录
│   ├── user/      # 学生端模块
│   ├── admin/     # 管理端模块
│   └── repair/    # 维修端模块
├── pages/         # 三端工作台页面
├── index.html
└── login.html
```

## 本地运行

前端是静态文件。为了保持页面的相对路径，从项目父目录启动静态服务器：

```powershell
cd ..
python -m http.server 5500
```

访问：

```text
http://127.0.0.1:5500/campus-equipment-mgr/frontend/
```

## 接口地址

所有请求由 `js/api.js` 集中处理。页面加载前可设置 `window.API_BASE` 覆盖接口根地址：

```html
<script>
  window.API_BASE = 'http://127.0.0.1:8000'
</script>
<script src="./js/api.js"></script>
```

本地开发时将 `frontend/js/api.js` 的默认 `BASE_URL` 指向 `http://127.0.0.1:8000`。Docker 部署副本 `deploy/frontend/dist/js/api.js` 默认使用 `${window.location.origin}/api`，由 Nginx 反向代理到后端，因此不需要配置跨域地址。

## 登录与会话

- 登录成功后，JWT 保存在 `sessionStorage` 的 `token` 字段。
- 受保护请求统一携带 `token` 请求头；后端返回未登录或令牌过期错误时，前端清除会话并跳转登录页。
- 前端不持久化 `role` 字段，角色与权限由后端鉴权结果控制。
- 学生可切换用户名密码登录和邮箱验证码登录。邮箱绑定成功后，个人资料弹窗会移除绑定组件。
- 管理员和维修员注册时必须填写相应注册码。

## 开发约定

- 新增接口优先在 `js/api.js` 封装，再由业务模块调用，避免页面散落重复 Fetch 逻辑。
- 页面按身份隔离在 `js/user`、`js/admin`、`js/repair` 中；通用工具放在根 `js` 目录。
- 需要修改密码时，页面应收集原密码、新密码和确认密码；无密码修改时不要传密码字段。
- 设备默认图片是本地资源 `/assets/images/all-icon..png`，上传的业务图片使用后端返回的 OSS URL。
- 静态资源更新后为 `<script>` 或 `<link>` 的 URL 增加版本查询参数，避免浏览器缓存旧文件。
