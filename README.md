# AI Investment News Monitor

一个实时监控AI领域投资新闻的智能代理系统。

## 功能特性

- 🔍 **多源新闻抓取**: 从多个权威科技和投资媒体获取AI相关新闻
- 🤖 **智能分析**: 使用AI对新闻进行分类、重要性评估和摘要生成
- 🚀 **实时更新**: 自动定时抓取最新新闻并推送更新
- 📊 **可视化界面**: 现代化的Web界面展示新闻动态
- 🔔 **智能通知**: 重要新闻实时推送
- 📈 **趋势分析**: 投资趋势和热点话题分析

## 快速启动

### 方式一：快速演示（无需配置）
```bash
python quick_demo.py
```
*自动安装依赖、创建演示数据、启动系统*

### 方式二：一键启动（推荐）
```bash
./start.sh
```

### 方式三：手动启动
1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 设置环境变量:
```bash
cp .env.example .env
# 编辑 .env 文件，添加OpenAI API密钥
```

3. 启动应用:
```bash
python main.py
```

### 方式四：Docker部署
```bash
./deploy.sh
```

启动后访问 http://localhost:8000 查看新闻监控界面

## 主要功能

### 🔍 智能新闻抓取
- 支持多个权威科技媒体RSS源
- 自动识别AI和投资相关内容
- 智能去重和内容提取

### 🤖 AI驱动分析
- 使用OpenAI GPT进行新闻分析
- 自动分类：融资、收购、IPO、产品发布等
- 重要性评分和紧急程度标记
- 关键信息提取：融资金额、轮次、公司、投资者

### 📊 实时监控界面
- 现代化响应式设计
- 实时WebSocket更新
- 多维度筛选和搜索
- 趋势分析和统计报表

### 🔔 智能通知系统
- 重要新闻实时推送
- 自定义关键词监控
- 多级别紧急程度分类

## 配置

在 `.env` 文件中配置:
- `OPENAI_API_KEY`: OpenAI API密钥（用于新闻分析）
- `NEWS_UPDATE_INTERVAL`: 新闻更新间隔（分钟）
- `DATABASE_URL`: 数据库连接URL（可选）

## 使用指南

### 基础使用

1. **快速启动**:
```bash
./start.sh
```

2. **测试系统**:
```bash
python test_system.py
```

3. **命令行管理**:
```bash
# 手动获取新闻
python cli.py fetch

# 查看统计信息
python cli.py stats

# 显示最新新闻
python cli.py news --limit 5

# 清理30天前的数据
python cli.py cleanup --days 30
```

### 高级使用

1. **Docker部署**:
```bash
./deploy.sh
```

2. **开发模式**:
```bash
python run.py --dev --port 8000
```

3. **生产部署**:
```bash
python run.py --setup-service  # 设置systemd服务
```

### API接口

- `GET /api/news` - 获取新闻列表
- `GET /api/trending` - 获取热门话题
- `GET /api/stats` - 获取统计信息
- `GET /api/search?q=关键词` - 搜索新闻
- `POST /api/refresh` - 手动刷新新闻
- `WebSocket /ws` - 实时更新推送

## 项目结构

```
├── main.py                 # 应用主入口
├── cli.py                  # 命令行工具
├── test_system.py         # 系统测试
├── run.py                 # 启动脚本
├── start.sh               # 一键启动
├── deploy.sh              # Docker部署
├── config/
│   └── settings.py        # 配置管理
├── scraper/
│   └── news_fetcher.py    # 新闻抓取
├── analyzer/
│   └── news_analyzer.py   # AI分析
├── database/
│   ├── models.py          # 数据模型
│   └── database.py        # 数据库连接
├── web/
│   └── templates/
│       └── index.html     # Web界面
├── utils/
│   └── scheduler.py       # 定时任务
├── nginx/
│   └── nginx.conf         # Nginx配置
├── docker-compose.yml     # Docker编排
├── Dockerfile             # Docker镜像
└── requirements.txt       # Python依赖
```

## 常见问题

### Q: 如何配置OpenAI API密钥？
A: 编辑 `.env` 文件，设置 `OPENAI_API_KEY=你的密钥`

### Q: 如何修改新闻更新频率？
A: 编辑 `.env` 文件，设置 `NEWS_UPDATE_INTERVAL=分钟数`

### Q: 如何添加新的新闻源？
A: 编辑 `config/settings.py` 中的 `NEWS_SOURCES` 列表

### Q: 数据存储在哪里？
A: 默认使用SQLite数据库 `ai_news.db`，可通过环境变量配置其他数据库

### Q: 如何查看系统日志？
A: 日志输出到控制台，Docker部署时可用 `docker-compose logs -f` 查看