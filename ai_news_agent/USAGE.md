# AI投资新闻Agent - 使用指南

## 🎯 项目概述

AI投资新闻Agent是一个智能的实时新闻监控和分析系统，专门用于跟踪AI领域的投资新闻。它能够：

- 🔍 **实时监控**: 从多个新闻源获取AI投资相关新闻
- 🤖 **智能分析**: 使用AI技术对新闻进行投资角度的分析
- 📊 **数据可视化**: 提供直观的Web界面展示分析结果
- 🔄 **自动更新**: 定期检查新新闻并实时推送

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd ai_news_agent

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `.env` 文件：

```bash
# 必需：OpenAI API密钥
OPENAI_API_KEY=your_openai_api_key_here

# 可选：News API密钥（用于更多新闻源）
NEWS_API_KEY=your_news_api_key_here

# 其他配置
UPDATE_INTERVAL=30  # 更新间隔（分钟）
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### 3. 启动服务

```bash
# 方式1：直接运行
python run.py

# 方式2：使用uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# 方式3：Docker
docker-compose up -d
```

### 4. 访问界面

打开浏览器访问：http://localhost:8000

## 📱 功能特性

### Web界面功能

- **📊 市场概览**: 显示新闻统计和市场总结
- **🎛️ 控制面板**: 手动刷新、启动/停止监控
- **🔍 智能筛选**: 按情绪（积极/消极/中性）和影响程度筛选
- **📰 新闻列表**: 展示新闻详情和AI分析结果

### API接口

- `GET /api/news` - 获取所有新闻
- `GET /api/news/sentiment/{sentiment}` - 按情绪筛选新闻
- `GET /api/news/impact/{impact}` - 按影响程度筛选新闻
- `GET /api/summary` - 获取市场摘要
- `GET /api/status` - 获取Agent状态
- `POST /api/refresh` - 手动刷新新闻
- `POST /api/start` - 启动定时更新
- `POST /api/stop` - 停止定时更新

## 🔧 技术架构

### 核心组件

1. **NewsFetcher** (`news_fetcher.py`)
   - 从RSS源和News API获取新闻
   - 智能筛选AI投资相关新闻
   - 支持多源数据聚合

2. **AIAnalyzer** (`ai_analyzer.py`)
   - 使用OpenAI GPT进行新闻分析
   - 提供投资角度的见解
   - 生成情绪分析和影响评估

3. **AIInvestmentNewsAgent** (`ai_agent.py`)
   - 整合新闻获取和分析功能
   - 管理定时更新任务
   - 提供数据存储和状态管理

4. **Web API** (`main.py`)
   - FastAPI框架提供REST API
   - 实时Web界面
   - 支持异步操作

### 数据流程

```
新闻源 → NewsFetcher → AIAnalyzer → AIAgent → Web API → 用户界面
   ↓         ↓           ↓          ↓        ↓
 RSS/API   筛选过滤    AI分析    数据存储   实时展示
```

## 🛠️ 开发和部署

### 本地开发

```bash
# 运行测试
python test.py

# 启动开发服务器
python run.py

# 查看日志
tail -f ai_agent.log
```

### Docker部署

```bash
# 构建镜像
docker build -t ai-news-agent .

# 运行容器
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  ai-news-agent

# 使用docker-compose
docker-compose up -d
```

### 生产部署

1. **使用Nginx反向代理**
2. **配置SSL证书**
3. **设置环境变量**
4. **配置日志轮转**
5. **设置监控和告警**

## 📊 监控和维护

### 日志管理

- 应用日志：`ai_agent.log`
- 访问日志：由uvicorn自动生成
- 错误日志：包含详细的错误信息

### 性能优化

- 调整更新间隔：`UPDATE_INTERVAL`
- 限制新闻数量：`max_news_items`
- 优化AI分析频率
- 使用缓存减少API调用

### 故障排除

1. **API密钥问题**
   ```bash
   # 检查环境变量
   echo $OPENAI_API_KEY
   ```

2. **网络连接问题**
   ```bash
   # 测试网络连接
   curl -I https://api.openai.com
   ```

3. **依赖问题**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt --force-reinstall
   ```

## 🔒 安全考虑

- 保护API密钥安全
- 使用HTTPS部署
- 限制API访问频率
- 定期更新依赖包
- 监控异常访问

## 📈 扩展功能

### 可扩展的新闻源

- 添加更多RSS源
- 集成社交媒体API
- 支持自定义新闻源

### 增强分析功能

- 添加情感分析
- 实现趋势预测
- 支持多语言分析

### 用户功能

- 用户账户系统
- 个性化订阅
- 推送通知
- 数据导出

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 📄 许可证

MIT License

## 📞 支持

如有问题，请提交Issue或联系开发团队。

---

**注意**: 使用前请确保配置正确的OpenAI API密钥，否则AI分析功能将无法正常工作。