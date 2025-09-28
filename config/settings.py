import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # News sources and keywords
    AI_KEYWORDS = [
        "artificial intelligence", "AI", "machine learning", "ML",
        "deep learning", "neural network", "LLM", "large language model",
        "OpenAI", "ChatGPT", "GPT", "Claude", "Anthropic", "Google AI",
        "Microsoft AI", "artificial general intelligence", "AGI",
        "computer vision", "natural language processing", "NLP",
        "robotics", "autonomous", "self-driving"
    ]
    
    INVESTMENT_KEYWORDS = [
        "funding", "investment", "venture capital", "VC", "Series A",
        "Series B", "Series C", "IPO", "acquisition", "merger",
        "startup", "valuation", "raise", "round", "investor",
        "capital", "equity", "financing", "backed", "led by"
    ]
    
    # News sources
    NEWS_SOURCES = [
        {
            "name": "TechCrunch",
            "rss_url": "https://techcrunch.com/feed/",
            "base_url": "https://techcrunch.com"
        },
        {
            "name": "VentureBeat",
            "rss_url": "https://venturebeat.com/feed/",
            "base_url": "https://venturebeat.com"
        },
        {
            "name": "MIT Technology Review",
            "rss_url": "https://www.technologyreview.com/feed/",
            "base_url": "https://www.technologyreview.com"
        },
        {
            "name": "AI News",
            "rss_url": "https://artificialintelligence-news.com/feed/",
            "base_url": "https://artificialintelligence-news.com"
        },
        {
            "name": "The Information",
            "rss_url": "https://www.theinformation.com/feed",
            "base_url": "https://www.theinformation.com"
        }
    ]
    
    # Update intervals
    NEWS_UPDATE_INTERVAL = int(os.getenv("NEWS_UPDATE_INTERVAL", 30))  # minutes
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_news.db")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Web server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Analysis settings
    MAX_NEWS_PER_FETCH = 50
    RELEVANCE_THRESHOLD = 0.7
    IMPORTANCE_THRESHOLD = 0.6

settings = Settings()