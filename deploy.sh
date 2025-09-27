#!/bin/bash

# AI投资新闻监控系统部署脚本

set -e

echo "🚀 开始部署AI投资新闻监控系统..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误：Docker未安装"
    echo "请先安装Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误：Docker Compose未安装"
    echo "请先安装Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "📄 创建.env文件..."
    cp .env.example .env
    echo "⚠️  请编辑.env文件，添加必要的API密钥和配置"
    echo "特别是OPENAI_API_KEY，用于AI分析功能"
    read -p "是否继续部署？(y/N): " confirm
    if [[ $confirm != [yY] ]]; then
        echo "部署已取消"
        exit 0
    fi
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs
mkdir -p nginx/ssl

# 构建和启动服务
echo "🔨 构建Docker镜像..."
docker-compose build

echo "🏃 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 健康检查
echo "🔍 检查服务状态..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "🌐 访问地址:"
    echo "   主界面: http://localhost"
    echo "   API文档: http://localhost:8000/docs"
    echo "   健康检查: http://localhost:8000/health"
    echo ""
    echo "📊 管理命令:"
    echo "   查看日志: docker-compose logs -f"
    echo "   停止服务: docker-compose down"
    echo "   重启服务: docker-compose restart"
    echo "   查看状态: docker-compose ps"
    echo ""
    echo "🔧 配置说明:"
    echo "   - 编辑.env文件修改配置"
    echo "   - 数据库: PostgreSQL (端口5432)"
    echo "   - 缓存: Redis (端口6379)"
    echo "   - 应用: FastAPI (端口8000)"
    echo "   - 代理: Nginx (端口80)"
else
    echo "❌ 服务启动失败，请检查日志:"
    echo "docker-compose logs"
fi

echo ""
echo "部署完成！"