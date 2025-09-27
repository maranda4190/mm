#!/usr/bin/env python3
"""
演示数据生成器 - 用于测试和展示
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import random

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 演示新闻数据
DEMO_NEWS = [
    {
        'title': 'OpenAI获得微软100亿美元投资，估值达到290亿美元',
        'summary': 'OpenAI宣布完成由微软领投的新一轮融资，本轮融资金额达100亿美元，公司估值飙升至290亿美元。资金将用于加速GPT模型研发和基础设施建设。',
        'content': 'OpenAI今日宣布完成了一轮重大融资，由微软领投，融资金额达到100亿美元，使得公司估值达到290亿美元。这轮融资的参与者还包括红杉资本、a16z等知名投资机构。OpenAI表示，这笔资金将主要用于扩大其AI研究团队，提升计算基础设施，以及加速下一代GPT模型的开发。CEO Sam Altman表示，这轮融资将帮助OpenAI实现其打造安全、有益的通用人工智能的使命。',
        'source': 'TechCrunch',
        'category': 'funding',
        'funding_amount': '10 billion',
        'funding_round': 'series c',
        'companies': ['OpenAI', 'Microsoft'],
        'investors': ['Microsoft', 'Sequoia Capital', 'Andreessen Horowitz'],
        'importance_score': 0.95,
        'relevance_score': 0.9,
        'urgency': 'high'
    },
    {
        'title': 'Anthropic完成45亿美元C轮融资，Google领投',
        'summary': '人工智能安全公司Anthropic宣布完成45亿美元C轮融资，由Google领投。此轮融资将用于扩展Claude AI助手的能力。',
        'content': 'AI安全公司Anthropic今天宣布完成45亿美元的C轮融资，由Google领投，Spark Capital和其他现有投资者跟投。Anthropic开发的Claude AI助手在安全性和可控性方面表现出色，此轮融资将帮助公司进一步扩展Claude的能力，并加强在AI安全研究方面的投入。',
        'source': 'VentureBeat',
        'category': 'funding',
        'funding_amount': '4.5 billion',
        'funding_round': 'series c',
        'companies': ['Anthropic', 'Google'],
        'investors': ['Google', 'Spark Capital'],
        'importance_score': 0.88,
        'relevance_score': 0.92,
        'urgency': 'high'
    },
    {
        'title': 'Stability AI推出新一代图像生成模型SDXL 2.0',
        'summary': 'Stability AI发布了其最新的图像生成模型SDXL 2.0，在图像质量和生成速度方面都有显著提升。',
        'content': 'Stability AI今日正式发布了新一代图像生成模型SDXL 2.0。新模型在图像分辨率、细节丰富度和生成速度方面都有显著改进。该公司表示，SDXL 2.0能够生成更高质量的图像，同时将推理时间减少了50%。这一突破为创意行业带来了新的可能性。',
        'source': 'MIT Technology Review',
        'category': 'product',
        'companies': ['Stability AI'],
        'importance_score': 0.72,
        'relevance_score': 0.85,
        'urgency': 'medium'
    },
    {
        'title': '英伟达AI芯片部门Q4营收创历史新高',
        'summary': '英伟达发布Q4财报，其数据中心业务营收达到476亿美元，主要得益于AI芯片需求激增。',
        'content': '英伟达公布的Q4财报显示，其数据中心业务营收达到476亿美元，同比增长217%，创下历史新高。这一增长主要归功于对AI训练和推理芯片的强劲需求。CEO黄仁勋表示，随着生成式AI的快速发展，公司预计这一增长趋势将持续下去。',
        'source': 'AI News',
        'category': 'general',
        'companies': ['NVIDIA'],
        'importance_score': 0.78,
        'relevance_score': 0.80,
        'urgency': 'medium'
    },
    {
        'title': 'Character.AI被Google以26亿美元收购',
        'summary': 'Google宣布以26亿美元收购AI聊天机器人公司Character.AI，这是Google在AI领域的又一重大投资。',
        'content': 'Google今日宣布以26亿美元的价格收购Character.AI，这家公司开发了广受欢迎的AI聊天机器人平台。Character.AI的创始人Noam Shazeer将重新加入Google，领导相关AI产品的开发。这笔交易预计将在未来几个月内完成，为Google的AI战略增添新的动力。',
        'source': 'TechCrunch',
        'category': 'acquisition',
        'companies': ['Google', 'Character.AI'],
        'importance_score': 0.85,
        'relevance_score': 0.90,
        'urgency': 'high'
    },
    {
        'title': 'Hugging Face获得2.35亿美元D轮融资',
        'summary': 'AI开源平台Hugging Face完成2.35亿美元D轮融资，估值达到45亿美元，将用于扩展开源AI生态系统。',
        'content': 'Hugging Face宣布完成2.35亿美元D轮融资，由Salesforce Ventures领投，Google、Amazon、NVIDIA等公司参投。此轮融资后，公司估值达到45亿美元。Hugging Face是全球最大的开源AI模型和数据集平台，拥有超过10万个预训练模型。',
        'source': 'VentureBeat',
        'category': 'funding',
        'funding_amount': '235 million',
        'funding_round': 'series d',
        'companies': ['Hugging Face'],
        'investors': ['Salesforce Ventures', 'Google', 'Amazon', 'NVIDIA'],
        'importance_score': 0.80,
        'relevance_score': 0.88,
        'urgency': 'medium'
    }
]

async def create_demo_data():
    """创建演示数据"""
    print("🎭 创建演示数据...")
    
    try:
        from database import init_database, AsyncSessionLocal, NewsArticle, TrendingTopic
        
        # 初始化数据库
        await init_database()
        
        async with AsyncSessionLocal() as db:
            # 清除现有演示数据
            print("🧹 清除现有演示数据...")
            
            # 创建新闻数据
            saved_count = 0
            for i, demo_news in enumerate(DEMO_NEWS):
                try:
                    # 生成随机发布时间（最近7天内）
                    days_ago = random.randint(0, 7)
                    hours_ago = random.randint(0, 23)
                    published_date = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
                    
                    # 构建分析数据
                    analysis = {
                        'relevance_score': demo_news.get('relevance_score', 0.8),
                        'importance_score': demo_news.get('importance_score', 0.7),
                        'funding_amount': demo_news.get('funding_amount'),
                        'funding_round': demo_news.get('funding_round'),
                        'companies': demo_news.get('companies', []),
                        'investors': demo_news.get('investors', []),
                        'category': demo_news.get('category', 'general'),
                        'urgency': demo_news.get('urgency', 'medium'),
                        'key_points': [
                            f"关键信息 {j+1}" for j in range(3)
                        ],
                        'market_impact': random.randint(3, 5),
                        'ai_summary': f"这是关于{demo_news['title'][:20]}的重要AI投资新闻。"
                    }
                    
                    overall_score = (
                        analysis['relevance_score'] * 0.3 + 
                        analysis['importance_score'] * 0.4 + 
                        analysis['market_impact'] / 5 * 0.3
                    )
                    
                    article = NewsArticle(
                        title=demo_news['title'],
                        link=f"https://demo.example.com/news/{i+1}",
                        summary=demo_news['summary'],
                        content=demo_news['content'],
                        published_date=published_date,
                        source=demo_news['source'],
                        source_url=f"https://{demo_news['source'].lower().replace(' ', '')}.com",
                        author=f"记者{i+1}",
                        tags=['AI', '投资', '科技'],
                        analysis=analysis,
                        relevance_score=analysis['relevance_score'],
                        importance_score=analysis['importance_score'],
                        overall_score=overall_score,
                        category=analysis['category'],
                        urgency=analysis['urgency'],
                        analyzed_at=datetime.utcnow(),
                        is_processed=True
                    )
                    
                    db.add(article)
                    saved_count += 1
                    
                except Exception as e:
                    print(f"⚠️  创建演示新闻失败: {e}")
                    continue
            
            # 创建热门话题
            trending_topics = [
                {'topic': 'OpenAI', 'category': 'company', 'count': 8},
                {'topic': 'Google AI', 'category': 'company', 'count': 6},
                {'topic': '大模型融资', 'category': 'topic', 'count': 12},
                {'topic': 'AI芯片', 'category': 'topic', 'count': 5},
                {'topic': 'Microsoft', 'category': 'company', 'count': 4}
            ]
            
            for topic_data in trending_topics:
                topic = TrendingTopic(
                    topic=topic_data['topic'],
                    category=topic_data['category'],
                    count=topic_data['count'],
                    latest_mention=datetime.utcnow() - timedelta(hours=random.randint(1, 24))
                )
                db.add(topic)
            
            await db.commit()
            
        print(f"✅ 成功创建 {saved_count} 条演示新闻")
        print(f"📊 创建 {len(trending_topics)} 个热门话题")
        print("🎉 演示数据创建完成！")
        print("💡 现在可以运行 ./start.sh 启动系统查看效果")
        
    except Exception as e:
        print(f"❌ 创建演示数据失败: {e}")

if __name__ == "__main__":
    asyncio.run(create_demo_data())