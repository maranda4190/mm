#!/usr/bin/env python3
"""
快速演示脚本 - 无需网络连接即可查看系统效果
"""

import asyncio
import sys
import os
import subprocess
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """检查基础依赖"""
    print("🔍 检查依赖...")
    
    try:
        import fastapi, uvicorn, sqlalchemy
        print("✅ 基础依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("💡 请运行: pip install -r requirements.txt")
        return False

async def setup_demo():
    """设置演示环境"""
    print("🎭 设置演示环境...")
    
    # 创建 .env 文件（如果不存在）
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 创建配置文件...")
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            
            # 设置演示配置
            with open(env_file, 'a') as f:
                f.write("\n# 演示模式配置\n")
                f.write("OPENAI_API_KEY=demo_key_not_required\n")
                f.write("NEWS_UPDATE_INTERVAL=60\n")
            
            print("✅ 配置文件已创建")
    
    # 创建演示数据
    from demo_data import create_demo_data
    await create_demo_data()

def start_demo_server():
    """启动演示服务器"""
    print("🚀 启动演示服务器...")
    print("📱 访问地址: http://localhost:8000")
    print("⏹️  按Ctrl+C停止服务")
    print("-" * 40)
    
    try:
        # 使用subprocess避免导入问题
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 演示结束")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

async def main():
    """主函数"""
    print("🎭 AI投资新闻监控 - 快速演示")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        print("\n💡 正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败，请手动安装")
            return
    
    # 设置演示环境
    await setup_demo()
    
    print("\n🎉 演示环境准备完成！")
    print("🚀 即将启动Web服务器...")
    input("按Enter键继续...")
    
    # 启动服务器
    start_demo_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 演示已退出")
    except Exception as e:
        print(f"\n💥 演示失败: {e}")
        sys.exit(1)