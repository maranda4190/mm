#!/usr/bin/env python3
"""
AI投资新闻监控系统测试脚本
"""

import asyncio
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_news_fetcher():
    """测试新闻抓取功能"""
    print("🔍 测试新闻抓取模块...")
    
    try:
        from scraper import NewsFetcher
        
        async with NewsFetcher() as fetcher:
            news_list = await fetcher.fetch_all_news()
        
        print(f"✅ 成功获取 {len(news_list)} 条新闻")
        
        if news_list:
            sample_news = news_list[0]
            print(f"📰 示例新闻标题: {sample_news.get('title', '')[:100]}...")
            print(f"📅 发布时间: {sample_news.get('published_date', '')}")
            print(f"🔗 来源: {sample_news.get('source', '')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 新闻抓取测试失败: {e}")
        return False

async def test_news_analyzer():
    """测试新闻分析功能"""
    print("\n🤖 测试新闻分析模块...")
    
    try:
        from analyzer import NewsAnalyzer
        
        # 创建测试新闻
        test_news = {
            'title': 'OpenAI raises $100 million in Series C funding led by Microsoft',
            'summary': 'Artificial intelligence company OpenAI announced today that it has raised $100 million in Series C funding round led by Microsoft Ventures.',
            'content': 'OpenAI, the artificial intelligence research company, has successfully raised $100 million in a Series C funding round. The round was led by Microsoft Ventures with participation from other major investors. This funding will be used to accelerate AI research and development.',
            'source': 'TechCrunch',
            'published_date': datetime.utcnow(),
            'link': 'https://example.com/openai-funding'
        }
        
        analyzer = NewsAnalyzer()
        analyzed_news = await analyzer.analyze_single_news(test_news)
        
        analysis = analyzed_news.get('analysis', {})
        print(f"✅ 分析完成")
        print(f"📊 相关性得分: {analysis.get('relevance_score', 0):.2f}")
        print(f"⭐ 重要性得分: {analysis.get('importance_score', 0):.2f}")
        print(f"🏷️  分类: {analysis.get('category', 'unknown')}")
        print(f"💰 融资金额: {analysis.get('funding_amount', 'N/A')}")
        print(f"🔄 融资轮次: {analysis.get('funding_round', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 新闻分析测试失败: {e}")
        return False

async def test_database():
    """测试数据库功能"""
    print("\n💾 测试数据库模块...")
    
    try:
        from database import init_database, AsyncSessionLocal, NewsArticle
        from sqlalchemy import select
        
        # 初始化数据库
        await init_database()
        
        # 测试数据库连接
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(NewsArticle).limit(1))
            existing_news = result.scalar_one_or_none()
            
        print("✅ 数据库连接正常")
        print(f"📊 现有新闻数量: {1 if existing_news else 0} (测试)")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_config():
    """测试配置"""
    print("\n⚙️ 测试配置...")
    
    try:
        from config.settings import settings
        
        print(f"✅ 配置加载成功")
        print(f"📊 新闻源数量: {len(settings.NEWS_SOURCES)}")
        print(f"⏰ 更新间隔: {settings.NEWS_UPDATE_INTERVAL} 分钟")
        print(f"🔑 OpenAI API: {'已配置' if settings.OPENAI_API_KEY else '未配置'}")
        print(f"💾 数据库: {settings.DATABASE_URL}")
        
        if not settings.OPENAI_API_KEY:
            print("⚠️  警告：未配置OpenAI API密钥，AI分析功能将受限")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

async def run_integration_test():
    """运行完整的集成测试"""
    print("\n🧪 运行集成测试...")
    
    try:
        from scraper import NewsFetcher
        from analyzer import NewsAnalyzer
        from database import init_database, AsyncSessionLocal, NewsArticle
        
        # 初始化数据库
        await init_database()
        
        # 获取新闻
        async with NewsFetcher() as fetcher:
            news_list = await fetcher.fetch_all_news()
        
        if not news_list:
            print("⚠️  未获取到新闻，可能是网络问题或新闻源无相关内容")
            return True
        
        # 分析新闻
        analyzer = NewsAnalyzer()
        analyzed_news = await analyzer.analyze_news_batch(news_list[:3])  # 只测试前3条
        
        # 保存到数据库
        async with AsyncSessionLocal() as db:
            saved_count = 0
            for news_data in analyzed_news:
                try:
                    analysis = news_data.get('analysis', {})
                    article = NewsArticle(
                        title=news_data.get('title', ''),
                        link=news_data.get('link', ''),
                        summary=news_data.get('summary', ''),
                        content=news_data.get('content', ''),
                        published_date=news_data.get('published_date'),
                        source=news_data.get('source', ''),
                        analysis=analysis,
                        relevance_score=analysis.get('relevance_score', 0.0),
                        importance_score=analysis.get('importance_score', 0.0),
                        overall_score=analysis.get('overall_score', 0.0),
                        category=analysis.get('category', 'general'),
                        urgency=analysis.get('urgency', 'low'),
                        analyzed_at=datetime.utcnow(),
                        is_processed=True
                    )
                    
                    db.add(article)
                    saved_count += 1
                    
                except Exception as e:
                    print(f"警告：保存新闻失败 - {e}")
                    continue
            
            await db.commit()
        
        print(f"✅ 集成测试完成，处理了 {saved_count} 条新闻")
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 AI投资新闻监控系统 - 功能测试")
    print("=" * 50)
    
    all_tests_passed = True
    
    # 基础配置测试
    if not test_config():
        all_tests_passed = False
    
    # 数据库测试
    if not await test_database():
        all_tests_passed = False
    
    # 新闻抓取测试
    if not await test_news_fetcher():
        all_tests_passed = False
    
    # 新闻分析测试
    if not await test_news_analyzer():
        all_tests_passed = False
    
    # 集成测试
    if not await run_integration_test():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 所有测试通过！系统可以正常运行")
        print("💡 下一步: 运行 ./start.sh 或 python main.py 启动系统")
    else:
        print("⚠️  部分测试失败，请检查配置和依赖")
        print("💡 尝试运行: pip install -r requirements.txt")
    
    print("=" * 50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n测试已中断")
    except Exception as e:
        print(f"\n💥 测试过程中出现错误: {e}")
        sys.exit(1)