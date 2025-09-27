#!/usr/bin/env python3
"""
AI投资新闻监控系统 - 命令行工具
"""

import asyncio
import sys
import os
import argparse
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def fetch_news():
    """手动获取新闻"""
    print("🔍 开始获取最新新闻...")
    
    try:
        from scraper import NewsFetcher
        from analyzer import NewsAnalyzer
        from database import init_database, AsyncSessionLocal, NewsArticle
        
        # 初始化数据库
        await init_database()
        
        # 获取新闻
        async with NewsFetcher() as fetcher:
            news_list = await fetcher.fetch_all_news()
        
        print(f"📰 获取到 {len(news_list)} 条相关新闻")
        
        if not news_list:
            print("😴 暂无新的AI投资新闻")
            return
        
        # 分析新闻
        analyzer = NewsAnalyzer()
        analyzed_news = await analyzer.analyze_news_batch(news_list)
        
        # 保存到数据库
        async with AsyncSessionLocal() as db:
            saved_count = 0
            for news_data in analyzed_news:
                try:
                    # 检查是否已存在
                    from sqlalchemy import select
                    existing_query = select(NewsArticle).where(NewsArticle.link == news_data['link'])
                    existing_result = await db.execute(existing_query)
                    existing_article = existing_result.scalar_one_or_none()
                    
                    if existing_article:
                        continue
                    
                    # 创建新闻记录
                    analysis = news_data.get('analysis', {})
                    article = NewsArticle(
                        title=news_data.get('title', ''),
                        link=news_data.get('link', ''),
                        summary=news_data.get('summary', ''),
                        content=news_data.get('content', ''),
                        published_date=news_data.get('published_date'),
                        source=news_data.get('source', ''),
                        source_url=news_data.get('source_url', ''),
                        author=news_data.get('author', ''),
                        tags=news_data.get('tags', []),
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
                    print(f"⚠️  保存失败: {e}")
                    continue
            
            await db.commit()
            print(f"💾 成功保存 {saved_count} 条新新闻")
        
    except Exception as e:
        print(f"❌ 获取新闻失败: {e}")

async def show_stats():
    """显示统计信息"""
    print("📊 系统统计信息")
    print("-" * 30)
    
    try:
        from database import AsyncSessionLocal, NewsArticle, TrendingTopic
        from sqlalchemy import select, func
        
        async with AsyncSessionLocal() as db:
            # 总新闻数
            total_query = select(func.count(NewsArticle.id))
            total_result = await db.execute(total_query)
            total_count = total_result.scalar() or 0
            
            # 今日新闻
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_query = select(func.count(NewsArticle.id)).where(
                NewsArticle.published_date >= today
            )
            today_result = await db.execute(today_query)
            today_count = today_result.scalar() or 0
            
            # 重要新闻
            important_query = select(func.count(NewsArticle.id)).where(
                NewsArticle.importance_score >= 0.7
            )
            important_result = await db.execute(important_query)
            important_count = important_result.scalar() or 0
            
            # 投资事件
            investment_query = select(func.count(NewsArticle.id)).where(
                NewsArticle.category.in_(['funding', 'acquisition', 'ipo'])
            )
            investment_result = await db.execute(investment_query)
            investment_count = investment_result.scalar() or 0
            
            # 热门话题
            trending_query = select(func.count(TrendingTopic.id))
            trending_result = await db.execute(trending_query)
            trending_count = trending_result.scalar() or 0
            
            print(f"📰 总新闻数量: {total_count}")
            print(f"📅 今日新闻: {today_count}")
            print(f"⭐ 重要新闻: {important_count}")
            print(f"💰 投资事件: {investment_count}")
            print(f"🔥 热门话题: {trending_count}")
            
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")

async def show_latest_news(limit=10):
    """显示最新新闻"""
    print(f"📰 最新 {limit} 条新闻")
    print("-" * 50)
    
    try:
        from database import AsyncSessionLocal, NewsArticle
        from sqlalchemy import select, desc
        
        async with AsyncSessionLocal() as db:
            query = select(NewsArticle).order_by(desc(NewsArticle.published_date)).limit(limit)
            result = await db.execute(query)
            news_articles = result.scalars().all()
            
            for i, article in enumerate(news_articles, 1):
                print(f"{i}. {article.title[:80]}...")
                print(f"   📅 {article.published_date.strftime('%Y-%m-%d %H:%M') if article.published_date else 'N/A'}")
                print(f"   🔗 {article.source}")
                if article.analysis:
                    print(f"   ⭐ 重要性: {article.importance_score:.2f} | 分类: {article.category}")
                print()
            
    except Exception as e:
        print(f"❌ 获取新闻失败: {e}")

async def cleanup_old_data(days=30):
    """清理旧数据"""
    print(f"🧹 清理 {days} 天前的数据...")
    
    try:
        from database import AsyncSessionLocal, NewsArticle, TrendingTopic
        from sqlalchemy import delete
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        async with AsyncSessionLocal() as db:
            # 删除旧新闻（保留重要新闻）
            delete_news_query = delete(NewsArticle).where(
                (NewsArticle.published_date < cutoff_date) &
                (NewsArticle.importance_score < 0.8)
            )
            news_result = await db.execute(delete_news_query)
            
            # 删除旧热门话题
            delete_trending_query = delete(TrendingTopic).where(
                TrendingTopic.latest_mention < cutoff_date
            )
            trending_result = await db.execute(delete_trending_query)
            
            await db.commit()
            
            print(f"🗑️  删除了 {news_result.rowcount} 条旧新闻")
            print(f"🗑️  删除了 {trending_result.rowcount} 个旧话题")
        
    except Exception as e:
        print(f"❌ 清理数据失败: {e}")

def main():
    parser = argparse.ArgumentParser(description="AI投资新闻监控系统CLI工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 获取新闻命令
    fetch_parser = subparsers.add_parser('fetch', help='手动获取新闻')
    
    # 显示统计命令
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    
    # 显示最新新闻命令
    news_parser = subparsers.add_parser('news', help='显示最新新闻')
    news_parser.add_argument('--limit', type=int, default=10, help='显示数量')
    
    # 清理数据命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧数据')
    cleanup_parser.add_argument('--days', type=int, default=30, help='保留天数')
    
    # 测试命令
    test_parser = subparsers.add_parser('test', help='运行系统测试')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🤖 AI投资新闻监控CLI")
    print("=" * 40)
    
    try:
        if args.command == 'fetch':
            asyncio.run(fetch_news())
        elif args.command == 'stats':
            asyncio.run(show_stats())
        elif args.command == 'news':
            asyncio.run(show_latest_news(args.limit))
        elif args.command == 'cleanup':
            asyncio.run(cleanup_old_data(args.days))
        elif args.command == 'test':
            from test_system import main as test_main
            asyncio.run(test_main())
            
    except KeyboardInterrupt:
        print("\n操作已中断")
    except Exception as e:
        print(f"\n💥 操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()