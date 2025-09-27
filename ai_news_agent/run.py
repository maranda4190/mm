#!/usr/bin/env python3
"""
AI投资新闻Agent启动脚本
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ai_agent.log')
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """检查环境配置"""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"缺少必需的环境变量: {', '.join(missing_vars)}")
        logger.error("请检查 .env 文件或设置相应的环境变量")
        return False
    
    return True

def main():
    """主函数"""
    logger.info("启动AI投资新闻Agent...")
    
    # 检查环境配置
    if not check_environment():
        sys.exit(1)
    
    # 导入并启动FastAPI应用
    try:
        import uvicorn
        from main import app
        
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        
        logger.info(f"服务器将在 http://{host}:{port} 启动")
        logger.info("按 Ctrl+C 停止服务器")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=os.getenv('LOG_LEVEL', 'info').lower()
        )
        
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()