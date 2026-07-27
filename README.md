# 🏫 校园设备管理系统 (Campus Equipment Manager)

校园设备管理系统的前端界面，用于设备的录入、借用、归还、维修跟踪及状态查看。

## 目录结构

```
campus-equipment-mgr/
├── index.html              # 项目主入口，首页
├── login.html              # 登录页面
├── assets/
│   └── images/             # 图片、图标等静态资源
├── css/
│   ├── reset.css           # 浏览器默认样式重置
│   └── main.css            # 项目核心业务样式
├── js/
│   ├── api.js              # 后端接口请求统一封装
│   ├── utils.js            # 公共工具函数（格式化时间等）
│   └── app.js              # 页面交互与 DOM 操作主逻辑
└── README.md               # 项目说明
```

### 各文件职责

| 文件/目录 | 说明 |
|-----------|------|
| `index.html` | 应用入口页面，所有路由/SPA 挂载点 |
| `login.html` | 登录页面，独立的认证入口 |
| `assets/images/` | 存放图片、图标等资源 |
| `css/reset.css` | 清除浏览器默认边距、字体等差异，每个项目必须引入 |
| `css/main.css` | 业务组件、布局、响应式等主体样式 |
| `js/api.js` | 封装所有后端 Ajax/Fetch 请求，统一处理请求头、错误码 |
| `js/utils.js` | 时间格式化、防抖节流、校验等可复用工具函数 |
| `js/app.js` | 页面初始化、事件绑定、DOM 更新等交互逻辑 |

## 启动方式

直接用浏览器打开 `index.html` 即可预览，无需构建步骤。

```bash
# 如果使用 Live Server（推荐）
npx live-server
```

## 技术栈

- 原生 HTML + CSS + JavaScript（无框架依赖）
- 所有后端通信统一走 `api.js`，便于维护和切换接口地址

## 开发约定

1. **HTML 页面** — 独立页面直接放在根目录（如 `login.html`），首页固定命名为 `index.html`
2. **CSS** — `reset.css` 必须最先引入，之后才是 `main.css`
3. **JavaScript** — 引入顺序：`api.js` → `utils.js` → `app.js`，确保依赖前置
4. **图片资源** — 统一放入 `assets/images/`，不分散放置
5. **接口调用** — 不允许在 `app.js` 中直接写 `fetch`/`axios`，必须通过 `api.js` 中转
