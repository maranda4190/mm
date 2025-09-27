"""
AI分析模块
使用OpenAI API对新闻进行投资角度的分析
"""

import openai
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime
import os
import asyncio

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI新闻分析器"""
    
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
    
    async def analyze_news_item(self, news_item: Dict) -> Dict:
        """分析单条新闻"""
        try:
            prompt = self._create_analysis_prompt(news_item)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI投资分析师，擅长分析AI领域的投资新闻。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # 解析分析结果
            analysis = self._parse_analysis(analysis_text)
            
            return {
                'news_id': news_item.get('id', ''),
                'title': news_item['title'],
                'analysis': analysis,
                'raw_analysis': analysis_text,
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news item: {e}")
            return {
                'news_id': news_item.get('id', ''),
                'title': news_item['title'],
                'analysis': {'sentiment': 'neutral', 'impact': 'medium', 'summary': '分析失败'},
                'raw_analysis': f'分析失败: {str(e)}',
                'analyzed_at': datetime.now().isoformat()
            }
    
    def _create_analysis_prompt(self, news_item: Dict) -> str:
        """创建分析提示词"""
        prompt = f"""
请分析以下AI投资新闻，并提供投资角度的见解：

标题: {news_item['title']}
描述: {news_item.get('description', '')}
来源: {news_item.get('source', '')}

请从以下角度进行分析：
1. 投资情绪 (sentiment): positive/negative/neutral
2. 市场影响 (impact): high/medium/low
3. 投资机会 (opportunity): 描述潜在的投资机会
4. 风险因素 (risks): 识别相关风险
5. 行业趋势 (trends): 对AI行业趋势的影响
6. 关键要点 (key_points): 3-5个关键要点

请以JSON格式返回分析结果：
{{
    "sentiment": "positive/negative/neutral",
    "impact": "high/medium/low",
    "opportunity": "投资机会描述",
    "risks": "风险因素描述",
    "trends": "行业趋势分析",
    "key_points": ["要点1", "要点2", "要点3"]
}}
"""
        return prompt
    
    def _parse_analysis(self, analysis_text: str) -> Dict:
        """解析AI分析结果"""
        try:
            # 尝试提取JSON部分
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = analysis_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # 如果无法解析JSON，返回默认结构
                return {
                    'sentiment': 'neutral',
                    'impact': 'medium',
                    'opportunity': '需要进一步分析',
                    'risks': '需要进一步分析',
                    'trends': '需要进一步分析',
                    'key_points': ['分析结果解析失败']
                }
        except json.JSONDecodeError:
            logger.error("Failed to parse AI analysis JSON")
            return {
                'sentiment': 'neutral',
                'impact': 'medium',
                'opportunity': '需要进一步分析',
                'risks': '需要进一步分析',
                'trends': '需要进一步分析',
                'key_points': ['分析结果解析失败']
            }
    
    async def analyze_news_batch(self, news_items: List[Dict]) -> List[Dict]:
        """批量分析新闻"""
        analyses = []
        
        for news_item in news_items:
            analysis = await self.analyze_news_item(news_item)
            analyses.append(analysis)
            
            # 添加延迟避免API限制
            await asyncio.sleep(0.5)
        
        return analyses
    
    def generate_market_summary(self, analyses: List[Dict]) -> str:
        """生成市场总结"""
        if not analyses:
            return "暂无分析数据"
        
        # 统计情绪分布
        sentiments = [a['analysis'].get('sentiment', 'neutral') for a in analyses]
        sentiment_counts = {
            'positive': sentiments.count('positive'),
            'negative': sentiments.count('negative'),
            'neutral': sentiments.count('neutral')
        }
        
        # 统计影响分布
        impacts = [a['analysis'].get('impact', 'medium') for a in analyses]
        impact_counts = {
            'high': impacts.count('high'),
            'medium': impacts.count('medium'),
            'low': impacts.count('low')
        }
        
        summary = f"""
AI投资新闻市场总结 (基于{len(analyses)}条新闻):

情绪分析:
- 积极: {sentiment_counts['positive']}条
- 消极: {sentiment_counts['negative']}条  
- 中性: {sentiment_counts['neutral']}条

市场影响:
- 高影响: {impact_counts['high']}条
- 中等影响: {impact_counts['medium']}条
- 低影响: {impact_counts['low']}条

总体趋势: {'积极' if sentiment_counts['positive'] > sentiment_counts['negative'] else '消极' if sentiment_counts['negative'] > sentiment_counts['positive'] else '中性'}
"""
        return summary