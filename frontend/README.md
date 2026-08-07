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

