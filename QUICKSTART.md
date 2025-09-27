# 🚀 快速开始指南

## 🎯 5分钟体验系统

### 第一步：获取代码
如果你还没有代码，请联系获取项目文件。

### 第二步：快速演示
```bash
# 进入项目目录
cd ai-investment-news-monitor

# 运行快速演示（自动处理一切）
python3 quick_demo.py
```

### 第三步：访问界面
打开浏览器访问: http://localhost:8000

🎉 **就这么简单！** 你将看到：
- 📰 AI投资新闻列表
- 📊 统计仪表板  
- 🔥 热门话题
- 🔍 搜索和筛选功能

## 🔧 正式使用（推荐）

### 1. 获取OpenAI API密钥
1. 访问 https://platform.openai.com/api-keys
2. 创建新的API密钥
3. 复制密钥备用

### 2. 配置系统
```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用你喜欢的编辑器
```

在 `.env` 文件中设置：
```bash
OPENAI_API_KEY=你的OpenAI密钥
NEWS_UPDATE_INTERVAL=30  # 30分钟更新一次
```

### 3. 启动系统
```bash
./start.sh
```

### 4. 访问界面
打开浏览器访问: http://localhost:8000

## 🐳 生产部署

### 使用Docker（推荐）
```bash
# 一键部署
./deploy.sh

# 访问地址
# http://localhost (通过Nginx)
# http://localhost:8000 (直接访问)
```

### 系统服务（Linux）
```bash
# 设置为系统服务
python3 run.py --setup-service

# 管理服务
sudo systemctl start ai-news-monitor
sudo systemctl status ai-news-monitor
sudo systemctl logs -f ai-news-monitor
```

## 🔧 常用命令

### 手动操作
```bash
# 立即获取新闻
python3 cli.py fetch

# 查看系统状态
python3 cli.py stats

# 显示最新新闻
python3 cli.py news --limit 10
```

### 系统测试
```bash
# 完整系统测试
python3 test_system.py

# 检查配置
python3 -c "from config.settings import settings; print('配置正常')"
```

## 📱 界面功能

### 主要功能区域
1. **📊 统计面板**: 今日新闻、投资事件、热门话题等统计
2. **🔍 搜索筛选**: 关键词搜索、分类筛选、排序功能
3. **📰 新闻列表**: 新闻卡片，包含AI分析结果
4. **🔥 热门话题**: 自动发现的热门公司和话题

### 新闻卡片信息
- **📰 标题和摘要**: 新闻基本信息
- **🤖 AI分析**: GPT生成的摘要和关键点
- **💰 投资信息**: 融资金额、轮次、相关公司
- **⭐ 评分系统**: 相关性、重要性、综合评分
- **🏷️ 分类标签**: 自动分类和紧急程度标记

## 🎯 使用技巧

### 💡 提升效果
1. **配置OpenAI API**: 获得更准确的AI分析
2. **调整更新频率**: 根据需求设置合适的更新间隔
3. **自定义关键词**: 编辑配置文件添加关注的公司或技术
4. **定期清理**: 使用CLI工具清理旧数据保持性能

### 🔍 高效使用
1. **关注重要性评分**: 优先查看高分新闻
2. **使用分类筛选**: 按融资、收购、IPO等分类查看
3. **热门话题**: 快速了解当前行业热点
4. **搜索功能**: 搜索特定公司或技术的相关新闻

## ❓ 常见问题

### Q: 为什么没有新闻显示？
A: 可能原因：
- 网络连接问题
- RSS源暂时不可用
- 关键词匹配过严
- 运行 `python3 demo_data.py` 创建演示数据

### Q: AI分析功能不工作？
A: 检查OpenAI API密钥是否正确配置在 `.env` 文件中

### Q: 如何添加新的新闻源？
A: 编辑 `config/settings.py` 文件，在 `NEWS_SOURCES` 列表中添加新源

### Q: 系统占用资源太多？
A: 调整 `.env` 中的 `NEWS_UPDATE_INTERVAL` 增加更新间隔

## 🆘 获取帮助

### 系统状态检查
```bash
# 查看API状态
curl http://localhost:8000/health

# 查看系统状态  
curl http://localhost:8000/api/status
```

### 日志查看
```bash
# 直接运行时查看控制台输出
python3 main.py

# Docker部署时查看日志
docker-compose logs -f ai-news-monitor
```

### 重置系统
```bash
# 删除数据库文件重新开始
rm ai_news.db

# 重新创建演示数据
python3 demo_data.py
```

---

🎊 **恭喜！你现在拥有了一个强大的AI投资新闻监控系统！**