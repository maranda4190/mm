#!/usr/bin/env python3
"""
AI Investment News Monitor - 启动脚本
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✓ Python版本: {sys.version}")

def install_dependencies():
    """安装依赖"""
    print("安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 依赖安装完成")
    except subprocess.CalledProcessError as e:
        print(f"错误：依赖安装失败 - {e}")
        sys.exit(1)

def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("警告：.env 文件不存在，正在从 .env.example 创建...")
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✓ .env 文件已创建")
            print("请编辑 .env 文件，添加必要的API密钥")
        else:
            print("错误：.env.example 文件不存在")
            sys.exit(1)
    else:
        print("✓ .env 文件存在")

def create_database():
    """创建数据库表"""
    print("初始化数据库...")
    try:
        # 导入必要的模块来创建表
        sys.path.insert(0, os.getcwd())
        from database import init_database
        import asyncio
        
        asyncio.run(init_database())
        print("✓ 数据库初始化完成")
    except Exception as e:
        print(f"警告：数据库初始化可能有问题 - {e}")

def run_app(dev=False, port=8000, host="0.0.0.0"):
    """运行应用"""
    print(f"启动AI投资新闻监控服务...")
    print(f"访问地址: http://localhost:{port}")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        if dev:
            # 开发模式
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "main:app", 
                "--reload", 
                "--host", host, 
                "--port", str(port)
            ])
        else:
            # 生产模式
            subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"错误：启动失败 - {e}")
        sys.exit(1)

def setup_systemd_service():
    """设置systemd服务（Linux）"""
    if os.name != 'posix':
        print("systemd服务仅支持Linux系统")
        return
    
    service_content = f"""[Unit]
Description=AI Investment News Monitor
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={os.getcwd()}
Environment=PATH={os.environ.get('PATH')}
ExecStart={sys.executable} main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "/etc/systemd/system/ai-news-monitor.service"
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        subprocess.run(["sudo", "systemctl", "daemon-reload"])
        subprocess.run(["sudo", "systemctl", "enable", "ai-news-monitor"])
        
        print(f"✓ systemd服务已创建: {service_file}")
        print("使用以下命令管理服务:")
        print("  启动: sudo systemctl start ai-news-monitor")
        print("  停止: sudo systemctl stop ai-news-monitor")
        print("  查看状态: sudo systemctl status ai-news-monitor")
        print("  查看日志: journalctl -u ai-news-monitor -f")
        
    except PermissionError:
        print("错误：需要sudo权限来创建systemd服务")
    except Exception as e:
        print(f"错误：创建systemd服务失败 - {e}")

def main():
    parser = argparse.ArgumentParser(description="AI投资新闻监控系统")
    parser.add_argument("--install-deps", action="store_true", help="安装依赖包")
    parser.add_argument("--setup-db", action="store_true", help="初始化数据库")
    parser.add_argument("--setup-service", action="store_true", help="设置systemd服务")
    parser.add_argument("--dev", action="store_true", help="开发模式运行")
    parser.add_argument("--port", type=int, default=8000, help="端口号")
    parser.add_argument("--host", default="0.0.0.0", help="主机地址")
    parser.add_argument("--skip-checks", action="store_true", help="跳过环境检查")
    
    args = parser.parse_args()
    
    print("AI投资新闻监控系统")
    print("=" * 50)
    
    if not args.skip_checks:
        check_python_version()
    
    if args.install_deps:
        install_dependencies()
        return
    
    if args.setup_db:
        create_database()
        return
    
    if args.setup_service:
        setup_systemd_service()
        return
    
    # 默认启动流程
    if not args.skip_checks:
        check_env_file()
        
        # 检查关键依赖
        try:
            import fastapi, uvicorn, aiohttp, openai
            print("✓ 关键依赖检查通过")
        except ImportError as e:
            print(f"错误：缺少依赖 - {e}")
            print("请运行: python run.py --install-deps")
            sys.exit(1)
    
    # 启动应用
    run_app(dev=args.dev, port=args.port, host=args.host)

if __name__ == "__main__":
    main()