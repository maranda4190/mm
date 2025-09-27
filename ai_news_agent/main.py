"""
FastAPI Web服务器
提供REST API和Web界面
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import os
from datetime import datetime
import asyncio

from ai_agent import AIInvestmentNewsAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AI投资新闻Agent",
    description="实时监控和分析AI领域投资新闻的智能Agent",
    version="1.0.0"
)

# 全局Agent实例
agent: Optional[AIInvestmentNewsAgent] = None

# 请求/响应模型
class NewsResponse(BaseModel):
    id: str
    title: str
    description: str
    link: str
    source: str
    published: str
    analyzed: bool
    analysis: Optional[Dict] = None
    created_at: str

class SummaryResponse(BaseModel):
    total_news: int
    analyzed_news: int
    last_update: Optional[str]
    market_summary: str

class StatusResponse(BaseModel):
    is_running: bool
    last_update: Optional[str]
    total_news: int
    analyzed_news: int
    update_interval: int
    openai_configured: bool
    news_api_configured: bool

# API路由
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/news", response_model=List[NewsResponse])
async def get_all_news():
    """获取所有新闻"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    news_data = agent.get_all_news()
    return [NewsResponse(**item) for item in news_data]

@app.get("/api/news/sentiment/{sentiment}", response_model=List[NewsResponse])
async def get_news_by_sentiment(sentiment: str):
    """根据情绪获取新闻"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    if sentiment not in ['positive', 'negative', 'neutral']:
        raise HTTPException(status_code=400, detail="无效的情绪类型")
    
    news_data = agent.get_news_by_sentiment(sentiment)
    return [NewsResponse(**item) for item in news_data]

@app.get("/api/news/impact/{impact}", response_model=List[NewsResponse])
async def get_news_by_impact(impact: str):
    """根据影响程度获取新闻"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    if impact not in ['high', 'medium', 'low']:
        raise HTTPException(status_code=400, detail="无效的影响程度")
    
    news_data = agent.get_news_by_impact(impact)
    return [NewsResponse(**item) for item in news_data]

@app.get("/api/summary", response_model=SummaryResponse)
async def get_summary():
    """获取新闻摘要"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    summary = agent.get_news_summary()
    return SummaryResponse(**summary)

@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """获取Agent状态"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    status = agent.get_status()
    return StatusResponse(**status)

@app.post("/api/refresh")
async def refresh_news():
    """手动刷新新闻"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    try:
        result = await agent.fetch_and_analyze_news()
        return {"success": result['success'], "message": "新闻刷新完成"}
    except Exception as e:
        logger.error(f"刷新新闻失败: {e}")
        raise HTTPException(status_code=500, detail=f"刷新失败: {str(e)}")

@app.post("/api/start")
async def start_agent():
    """启动定时更新"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    agent.start_scheduled_updates()
    return {"success": True, "message": "定时更新已启动"}

@app.post("/api/stop")
async def stop_agent():
    """停止定时更新"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent未初始化")
    
    agent.stop_scheduled_updates()
    return {"success": True, "message": "定时更新已停止"}

# 错误处理
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "页面未找到"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误"}
    )

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化Agent"""
    global agent
    
    # 获取API密钥
    openai_api_key = os.getenv('OPENAI_API_KEY')
    news_api_key = os.getenv('NEWS_API_KEY')
    
    if not openai_api_key:
        logger.error("未找到OPENAI_API_KEY环境变量")
        return
    
    # 初始化Agent
    agent = AIInvestmentNewsAgent(openai_api_key, news_api_key)
    
    # 初始化并启动定时更新
    await agent.initialize()
    agent.start_scheduled_updates()
    
    logger.info("AI投资新闻Agent已启动")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时停止Agent"""
    global agent
    
    if agent:
        agent.stop_scheduled_updates()
        logger.info("AI投资新闻Agent已停止")

# 模板配置
templates = Jinja2Templates(directory="templates")

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    
    uvicorn.run(app, host=host, port=port)