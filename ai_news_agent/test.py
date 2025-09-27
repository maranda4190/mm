#!/usr/bin/env python3
"""
AI投资新闻Agent测试脚本
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_news_fetcher():
    """测试新闻获取功能"""
    print("测试新闻获取功能...")
    
    try:
        from news_fetcher import NewsFetcher
        
        async with NewsFetcher() as fetcher:
            news = await fetcher.fetch_rss_news()
            
        print(f"✅ 成功获取 {len(news)} 条新闻")
        
        if news:
            print("\n前3条新闻:")
            for i, item in enumerate(news[:3]):
                print(f"{i+1}. {item['title']}")
                print(f"   来源: {item['source']}")
                print(f"   链接: {item['link']}")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ 新闻获取测试失败: {e}")
        return False

async def test_ai_analyzer():
    """测试AI分析功能"""
    print("测试AI分析功能...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 未找到OPENAI_API_KEY，跳过AI分析测试")
        return False
    
    try:
        from ai_analyzer import AIAnalyzer
        
        analyzer = AIAnalyzer(api_key)
        
        # 创建测试新闻
        test_news = {
            'title': 'OpenAI获得新一轮10亿美元投资',
            'description': '人工智能公司OpenAI宣布获得新一轮10亿美元投资，将用于扩大AI模型研发',
            'source': 'TechCrunch'
        }
        
        analysis = await analyzer.analyze_news_item(test_news)
        
        print("✅ AI分析测试成功")
        print(f"分析结果: {analysis['analysis']}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI分析测试失败: {e}")
        return False

async def test_agent():
    """测试完整Agent功能"""
    print("测试完整Agent功能...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 未找到OPENAI_API_KEY，跳过Agent测试")
        return False
    
    try:
        from ai_agent import AIInvestmentNewsAgent
        
        agent = AIInvestmentNewsAgent(api_key)
        
        # 初始化Agent
        result = await agent.initialize()
        
        if result['success']:
            print("✅ Agent初始化成功")
            
            # 获取状态
            status = agent.get_status()
            print(f"状态: {status}")
            
            # 获取摘要
            summary = agent.get_news_summary()
            print(f"摘要: {summary}")
            
            return True
        else:
            print(f"❌ Agent初始化失败: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Agent测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试AI投资新闻Agent...")
    print("=" * 50)
    
    tests = [
        ("新闻获取", test_news_fetcher),
        ("AI分析", test_ai_analyzer),
        ("完整Agent", test_agent)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}测试:")
        print("-" * 30)
        
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Agent可以正常使用。")
    else:
        print("⚠️  部分测试失败，请检查配置和依赖。")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试异常: {e}")
        sys.exit(1)