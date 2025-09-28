#!/bin/bash

# AI投资新闻监控系统 - 快速启动脚本

echo "🤖 AI投资新闻监控系统"
echo "================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3"
    exit 1
fi

echo "✅ Python3已安装"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

# 检查.env文件
if [ ! -f .env ]; then
    echo "📝 创建配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑.env文件，添加OpenAI API密钥"
    echo "📖 获取API密钥: https://platform.openai.com/api-keys"
    echo ""
    read -p "按Enter键继续（你可以稍后添加API密钥）..."
fi

# 启动应用
echo "🚀 启动应用..."
echo "📱 访问地址: http://localhost:8000"
echo "⏹️  按Ctrl+C停止服务"
echo "================================"

python main.py