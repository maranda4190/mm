import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import json
import re
from datetime import datetime
import openai
from openai import AsyncOpenAI

from config.settings import settings

logger = logging.getLogger(__name__)

class NewsAnalyzer:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        
        # 预定义的投资轮次
        self.funding_rounds = [
            "pre-seed", "seed", "series a", "series b", "series c", "series d",
            "bridge round", "ipo", "acquisition", "merger"
        ]
        
        # 重要公司列表
        self.important_companies = [
            "openai", "anthropic", "google", "microsoft", "meta", "amazon",
            "apple", "nvidia", "tesla", "spacex", "deepmind", "hugging face",
            "stability ai", "midjourney", "runway", "character.ai", "perplexity"
        ]
    
    async def analyze_news_batch(self, news_list: List[Dict]) -> List[Dict]:
        """批量分析新闻"""
        analyzed_news = []
        
        # 分批处理以避免API限制
        batch_size = 5
        for i in range(0, len(news_list), batch_size):
            batch = news_list[i:i + batch_size]
            
            tasks = [self.analyze_single_news(news) for news in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error analyzing news: {result}")
                    continue
                if result:
                    analyzed_news.append(result)
            
            # 短暂延迟避免API限制
            await asyncio.sleep(1)
        
        return analyzed_news
    
    async def analyze_single_news(self, news: Dict) -> Dict:
        """分析单条新闻"""
        try:
            # 基础分析
            basic_analysis = self._basic_analysis(news)
            
            # AI分析（如果有API key）
            ai_analysis = {}
            if self.client and settings.OPENAI_API_KEY:
                ai_analysis = await self._ai_analysis(news)
            
            # 合并分析结果
            analysis = {
                **basic_analysis,
                **ai_analysis,
                'analyzed_at': datetime.utcnow().isoformat()
            }
            
            # 计算综合得分
            analysis['overall_score'] = self._calculate_overall_score(analysis)
            
            return {
                **news,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news '{news.get('title', '')[:50]}': {e}")
            return news
    
    def _basic_analysis(self, news: Dict) -> Dict:
        """基础规则分析"""
        title = news.get('title', '').lower()
        content = f"{news.get('summary', '')} {news.get('content', '')}".lower()
        full_text = f"{title} {content}"
        
        analysis = {
            'relevance_score': 0.0,
            'importance_score': 0.0,
            'funding_amount': None,
            'funding_round': None,
            'companies': [],
            'investors': [],
            'category': 'unknown',
            'urgency': 'low',
            'key_points': []
        }
        
        # 计算相关性得分
        analysis['relevance_score'] = self._calculate_relevance_score(full_text)
        
        # 提取投资信息
        analysis['funding_amount'] = self._extract_funding_amount(full_text)
        analysis['funding_round'] = self._extract_funding_round(full_text)
        
        # 提取公司信息
        analysis['companies'] = self._extract_companies(full_text)
        
        # 提取投资者信息
        analysis['investors'] = self._extract_investors(full_text)
        
        # 分类
        analysis['category'] = self._categorize_news(full_text)
        
        # 计算重要性
        analysis['importance_score'] = self._calculate_importance_score(analysis, full_text)
        
        # 确定紧急程度
        analysis['urgency'] = self._determine_urgency(analysis, news)
        
        return analysis
    
    def _calculate_relevance_score(self, text: str) -> float:
        """计算相关性得分"""
        score = 0.0
        
        # AI关键词权重
        ai_weights = {
            'artificial intelligence': 0.2, 'ai': 0.15, 'machine learning': 0.2,
            'deep learning': 0.15, 'neural network': 0.1, 'llm': 0.2,
            'openai': 0.3, 'chatgpt': 0.25, 'gpt': 0.2, 'claude': 0.2,
            'anthropic': 0.25, 'google ai': 0.2, 'microsoft ai': 0.2
        }
        
        # 投资关键词权重
        investment_weights = {
            'funding': 0.3, 'investment': 0.25, 'venture capital': 0.3,
            'series a': 0.35, 'series b': 0.35, 'series c': 0.35,
            'ipo': 0.4, 'acquisition': 0.4, 'merger': 0.35,
            'startup': 0.2, 'valuation': 0.25, 'raise': 0.3
        }
        
        # 计算AI相关性
        for keyword, weight in ai_weights.items():
            if keyword in text:
                score += weight
        
        # 计算投资相关性
        for keyword, weight in investment_weights.items():
            if keyword in text:
                score += weight
        
        return min(score, 1.0)
    
    def _extract_funding_amount(self, text: str) -> Optional[str]:
        """提取融资金额"""
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*(?:million|billion|m|b)',
            r'(\d+(?:\.\d+)?)\s*(?:million|billion)\s*(?:dollars?|\$)',
            r'raised\s+\$?(\d+(?:\.\d+)?)\s*(?:million|billion|m|b)',
            r'funding\s+of\s+\$?(\d+(?:\.\d+)?)\s*(?:million|billion|m|b)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def _extract_funding_round(self, text: str) -> Optional[str]:
        """提取融资轮次"""
        for round_type in self.funding_rounds:
            if round_type in text:
                return round_type
        return None
    
    def _extract_companies(self, text: str) -> List[str]:
        """提取公司名称"""
        companies = []
        
        # 检查重要公司
        for company in self.important_companies:
            if company in text:
                companies.append(company.title())
        
        # 使用正则表达式查找其他公司
        company_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:inc|corp|ltd|llc)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+raised',
            r'startup\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'company\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            companies.extend(matches)
        
        return list(set(companies))
    
    def _extract_investors(self, text: str) -> List[str]:
        """提取投资者信息"""
        investor_patterns = [
            r'led\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:ventures?|capital|partners?)',
            r'investors?\s+(?:include\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'backed\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        investors = []
        for pattern in investor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            investors.extend(matches)
        
        return list(set(investors))
    
    def _categorize_news(self, text: str) -> str:
        """新闻分类"""
        categories = {
            'funding': ['funding', 'investment', 'raise', 'round', 'capital'],
            'acquisition': ['acquisition', 'merger', 'acquired', 'bought'],
            'ipo': ['ipo', 'public', 'stock', 'nasdaq', 'nyse'],
            'product': ['launch', 'release', 'product', 'feature', 'model'],
            'partnership': ['partnership', 'collaboration', 'alliance', 'deal'],
            'research': ['research', 'paper', 'study', 'breakthrough', 'discovery'],
            'regulation': ['regulation', 'policy', 'law', 'government', 'ban']
        }
        
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        return 'general'
    
    def _calculate_importance_score(self, analysis: Dict, text: str) -> float:
        """计算重要性得分"""
        score = 0.0
        
        # 基于融资金额
        funding_amount = analysis.get('funding_amount')
        if funding_amount:
            try:
                amount = float(funding_amount)
                if 'billion' in text or 'b' in funding_amount:
                    score += 0.4
                elif amount >= 100:  # 100M+
                    score += 0.3
                elif amount >= 50:   # 50M+
                    score += 0.2
                else:
                    score += 0.1
            except:
                pass
        
        # 基于公司重要性
        companies = analysis.get('companies', [])
        important_found = any(comp.lower() in self.important_companies for comp in companies)
        if important_found:
            score += 0.3
        
        # 基于融资轮次
        funding_round = analysis.get('funding_round')
        if funding_round in ['ipo', 'acquisition', 'merger']:
            score += 0.4
        elif funding_round in ['series c', 'series d']:
            score += 0.3
        elif funding_round in ['series a', 'series b']:
            score += 0.2
        
        # 基于关键词密度
        if analysis.get('relevance_score', 0) > 0.8:
            score += 0.2
        
        return min(score, 1.0)
    
    def _determine_urgency(self, analysis: Dict, news: Dict) -> str:
        """确定紧急程度"""
        importance = analysis.get('importance_score', 0)
        
        # 检查时间敏感性
        published_date = news.get('published_date')
        if published_date:
            hours_old = (datetime.utcnow() - published_date).total_seconds() / 3600
            if hours_old < 2 and importance > 0.7:
                return 'high'
            elif hours_old < 6 and importance > 0.5:
                return 'medium'
        
        if importance > 0.8:
            return 'high'
        elif importance > 0.5:
            return 'medium'
        else:
            return 'low'
    
    async def _ai_analysis(self, news: Dict) -> Dict:
        """使用AI进行深度分析"""
        try:
            content = f"Title: {news.get('title', '')}\n"
            content += f"Summary: {news.get('summary', '')}\n"
            content += f"Content: {news.get('content', '')[:2000]}"  # 限制长度
            
            prompt = f"""
            请分析以下AI投资新闻，提供以下信息：
            1. 简短的中文摘要（50字以内）
            2. 关键要点（3-5个要点）
            3. 市场影响评估（1-5分）
            4. 投资趋势分析
            5. 风险评估
            
            新闻内容：
            {content}
            
            请以JSON格式返回：
            {{
                "summary": "中文摘要",
                "key_points": ["要点1", "要点2", "要点3"],
                "market_impact": 数字(1-5),
                "trend_analysis": "趋势分析",
                "risk_assessment": "风险评估"
            }}
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            ai_result = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                parsed_result = json.loads(ai_result)
                return {
                    'ai_summary': parsed_result.get('summary', ''),
                    'key_points': parsed_result.get('key_points', []),
                    'market_impact': parsed_result.get('market_impact', 3),
                    'trend_analysis': parsed_result.get('trend_analysis', ''),
                    'risk_assessment': parsed_result.get('risk_assessment', '')
                }
            except json.JSONDecodeError:
                return {'ai_summary': ai_result[:200]}
                
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {}
    
    def _calculate_overall_score(self, analysis: Dict) -> float:
        """计算综合得分"""
        relevance = analysis.get('relevance_score', 0) * 0.3
        importance = analysis.get('importance_score', 0) * 0.4
        market_impact = (analysis.get('market_impact', 3) / 5) * 0.3
        
        return relevance + importance + market_impact
    
    async def get_trending_topics(self, news_list: List[Dict]) -> List[Dict]:
        """获取热门话题"""
        topics = {}
        
        for news in news_list:
            analysis = news.get('analysis', {})
            companies = analysis.get('companies', [])
            category = analysis.get('category', 'general')
            
            # 统计公司
            for company in companies:
                if company not in topics:
                    topics[company] = {'count': 0, 'category': 'company', 'latest_news': []}
                topics[company]['count'] += 1
                topics[company]['latest_news'].append(news)
            
            # 统计分类
            category_key = f"category_{category}"
            if category_key not in topics:
                topics[category_key] = {'count': 0, 'category': 'topic', 'latest_news': []}
            topics[category_key]['count'] += 1
            topics[category_key]['latest_news'].append(news)
        
        # 排序并返回热门话题
        trending = []
        for topic, data in topics.items():
            if data['count'] >= 2:  # 至少出现2次
                trending.append({
                    'topic': topic,
                    'count': data['count'],
                    'category': data['category'],
                    'latest_news': data['latest_news'][:3]  # 最新3条
                })
        
        return sorted(trending, key=lambda x: x['count'], reverse=True)[:10]