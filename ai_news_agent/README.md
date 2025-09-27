# AI投资新闻Agent

一个智能的AI Agent，用于实时监控和分析AI领域的投资新闻。

## 功能特性

- 🔍 **实时新闻监控**: 从多个新闻源获取AI投资相关新闻
- 🤖 **智能筛选**: 使用AI技术筛选和分类相关新闻
- 📊 **投资分析**: 对新闻进行投资角度的分析和解读
- 🔄 **自动更新**: 定期检查新新闻并实时推送
- 🌐 **Web界面**: 简洁美观的用户界面

## 快速开始

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 配置环境变量:
```bash
cp .env.example .env
# 编辑 .env 文件，添加必要的API密钥
```

3. 启动服务:
```bash
python main.py
```

4. 访问 http://localhost:8000 查看界面

## 配置说明

在 `.env` 文件中配置以下参数:
- `OPENAI_API_KEY`: OpenAI API密钥（用于AI分析）
- `NEWS_API_KEY`: 新闻API密钥（可选）
- `UPDATE_INTERVAL`: 更新间隔（分钟）

## 技术栈

- **后端**: FastAPI + Python
- **AI分析**: OpenAI GPT API
- **新闻源**: RSS feeds, News API
- **前端**: HTML + CSS + JavaScript
- **实时更新**: WebSocket + 定时任务