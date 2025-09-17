# AI-Front-Test 网络会话分析系统

基于React + TypeScript + Vite前端 + FastAPI后端的全栈网络会话分析应用，支持ClickHouse数据库集成。

## 功能特性

- 🔐 **用户认证系统** - 简单的登录界面，登录后可查看统计信息
- 👥 **用户管理** - 完整的用户管理界面，支持添加、删除和修改用户
- 📊 **数据统计** - 从ClickHouse获取基础五元组会话相关统计信息并展示
- 🔍 **多维查询** - 支持按照会话、IP等多维度的查询展示信息
- 📱 **响应式设计** - 基于Ant Design的现代化UI界面

## 技术栈

### 前端技术栈
- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite 4
- **UI组件库**: Ant Design 5
- **路由**: React Router DOM 6
- **HTTP客户端**: Axios
- **代码规范**: ESLint + TypeScript

### 后端技术栈
- **后端框架**: FastAPI (Python 3.9+)
- **ASGI服务器**: Uvicorn
- **数据库**: ClickHouse
- **认证**: JWT + BCrypt密码加密
- **文档**: OpenAPI/Swagger自动生成
- **跨域**: CORS中间件支持
- **环境管理**: python-dotenv

## 环境要求

### 前端环境
- Node.js >= 16.0.0
- npm >= 8.0.0

### 后端环境
- Python >= 3.9.0
- pip >= 21.0.0
- ClickHouse >= 22.0.0 (可选，用于数据统计功能)

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd AI-front-test
```

### 2. 启动后端服务

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install -r requirements.txt

# 启动后端服务
python main.py
```

后端服务将运行在 `http://localhost:8000`

**API文档访问**：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 启动前端服务

```bash
# 返回根目录
cd ..

# 安装前端依赖
npm install

# 启动前端开发服务器
npm run dev
```

前端服务将运行在 `http://localhost:3001`（如果3000端口被占用）

### 4. 访问应用

- **前端应用**: http://localhost:3001
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 详细安装说明

### 前端安装

**Windows平台:**
```bash
npm install
```

**Linux平台:**
```bash
# 如果从Windows环境迁移，需要清除node_modules重新安装
rm -rf node_modules package-lock.json
npm install
```

**注意**: 由于esbuild等工具是平台特定的，在不同操作系统间复制node_modules会导致兼容性问题。

### 后端安装

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选）
cp .env.example .env  # 如果有示例配置文件
```

### 环境配置

后端服务支持以下环境变量配置：

```bash
# .env 文件示例
HOST=0.0.0.0
PORT=8000
DEBUG=True
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=
CLICKHOUSE_DATABASE=default
```

### 3. 配置服务器

项目已配置为支持跨平台访问，配置文件位于 `vite.config.ts`:

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',    // 监听所有网络接口
    port: 3000,         // 端口号
    open: false         // 不自动打开浏览器
  }
})
```

### 4. 启动开发服务器

```bash
npm run dev
```

服务器启动后将显示:
```
➜  Local:   http://localhost:3000/
➜  Network: http://[服务器IP]:3000/
```

### 5. 访问应用

- **本地访问**: http://localhost:3000/
- **远程访问**: http://[服务器IP]:3000/

## 开发命令

### 前端命令
```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint

# 预览生产构建
npm run preview
```

### 后端命令
```bash
# 启动开发服务器（自动重载）
python main.py

# 启动生产服务器
uvicorn main:app --host 0.0.0.0 --port 8000

# 后台运行
nohup python main.py > backend.log 2>&1 &
```

## 服务端口说明

| 服务 | 端口 | 用途 | 访问地址 |
|------|------|------|----------|
| 前端React | 3000/3001 | 用户界面 | http://localhost:3001 |
| 后端FastAPI | 8000 | API服务 | http://localhost:8000 |
| ClickHouse | 9000 | 数据库 | localhost:9000 |
| API文档 | 8000/docs | Swagger UI | http://localhost:8000/docs |

## 后台进程管理

### 启动后台服务
```bash
# 使用nohup在后台运行
nohup npm run dev > app.log 2>&1 &

# 或使用screen/tmux会话
screen -S frontend-app
npm run dev
# Ctrl+A+D 分离会话
```

### 查看运行状态
```bash
# 查看端口占用
netstat -tlnp | grep :3000

# 查看进程
ps aux | grep vite
```

### 停止后台服务
```bash
# 根据端口杀死进程
sudo lsof -ti:3000 | xargs kill -9

# 或根据进程名杀死
pkill -f "vite"
```

## 项目结构

```
AI-front-test/
├── src/                          # 前端源代码目录
│   ├── components/               # React组件
│   ├── pages/                    # 页面组件
│   ├── services/                 # API服务
│   ├── utils/                    # 工具函数
│   ├── types/                    # TypeScript类型定义
│   └── App.tsx                   # 主应用组件
├── backend/                      # 后端源代码目录
│   ├── app/                      # FastAPI应用
│   │   ├── api/                  # API路由
│   │   │   ├── users.py          # 用户管理API
│   │   │   └── sessions.py       # 会话统计API
│   │   ├── models/               # 数据模型
│   │   ├── services/             # 业务逻辑
│   │   └── utils/                # 工具函数
│   ├── main.py                   # FastAPI主程序
│   ├── requirements.txt          # Python依赖
│   ├── .env                      # 环境变量配置
│   └── users.json                # 用户数据文件
├── public/                       # 静态资源
├── node_modules/                 # 前端依赖包
├── index.html                    # 入口HTML文件
├── package.json                  # 前端项目配置和依赖
├── vite.config.ts                # Vite配置文件
├── tsconfig.json                 # TypeScript配置
├── CLAUDE.md                     # Claude Code指导文档
└── README.md                     # 项目说明文档
```

## API接口文档

### 用户管理接口

| 方法 | 路径 | 描述 | 参数 |
|------|------|------|------|
| POST | `/api/users/login` | 用户登录 | username, password |
| GET | `/api/users` | 获取用户列表 | - |
| POST | `/api/users` | 创建用户 | username, password, role |
| PUT | `/api/users/{user_id}` | 更新用户 | username, password, role |
| DELETE | `/api/users/{user_id}` | 删除用户 | - |

### 会话统计接口

| 方法 | 路径 | 描述 | 参数 |
|------|------|------|------|
| GET | `/api/sessions/stats` | 获取会话统计 | start_time, end_time |
| GET | `/api/sessions/by-ip` | 按IP统计 | ip, limit |
| GET | `/api/sessions/search` | 多维度查询 | filters |

### 系统接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/docs` | API文档 (Swagger UI) |
| GET | `/redoc` | API文档 (ReDoc) |

## 防火墙配置

如需外部访问，请确保服务器防火墙允许相应端口:

```bash
# CentOS/RHEL - 开放前端和后端端口
sudo firewall-cmd --add-port=3000/tcp --permanent
sudo firewall-cmd --add-port=3001/tcp --permanent
sudo firewall-cmd --add-port=8000/tcp --permanent
sudo firewall-cmd --reload

# Ubuntu/Debian - 开放前端和后端端口
sudo ufw allow 3000
sudo ufw allow 3001
sudo ufw allow 8000
```

## 故障排除

### 1. 前端相关问题

**权限问题:**
```bash
# 修复node_modules执行权限
chmod +x node_modules/.bin/*
```

**平台兼容性问题:**
```bash
# 清除并重新安装依赖
rm -rf node_modules package-lock.json
npm install
```

**端口被占用:**
```bash
# 查看端口占用
sudo lsof -i :3000
sudo lsof -i :3001
# 杀死占用进程
sudo kill -9 <PID>
```

### 2. 后端相关问题

**Python依赖问题:**
```bash
# 升级pip
pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

**ClickHouse连接问题:**
```bash
# 检查ClickHouse服务状态
sudo systemctl status clickhouse-server

# 启动ClickHouse服务
sudo systemctl start clickhouse-server
```

**后端端口被占用:**
```bash
# 查看端口占用
sudo lsof -i :8000
# 杀死占用进程
sudo kill -9 <PID>
```

### 3. 网络访问问题

**跨域问题:**
- 确保后端CORS配置正确
- 检查前端API基础URL配置

**防火墙问题:**
- 确保相关端口已开放
- 检查云服务器安全组配置

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。