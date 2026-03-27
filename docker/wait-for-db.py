#!/usr/bin/env python3
"""等待数据库就绪的脚本"""
import sys
import time
import pymysql
import os

def wait_for_db(max_attempts=30, delay=2):
    """等待数据库连接就绪"""
    db_host = os.getenv("DB_HOST", "mysql")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "Test@123456")
    db_name = os.getenv("DB_NAME", "bug_management")
    
    print(f"等待数据库 {db_host}:{db_port} 就绪...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            conn = pymysql.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database=db_name,
                connect_timeout=5
            )
            conn.close()
            print(f"✅ 数据库连接成功！(尝试 {attempt}/{max_attempts})")
            return True
        except Exception as e:
            if attempt < max_attempts:
                print(f"⏳ 尝试 {attempt}/{max_attempts}: {str(e)}")
                time.sleep(delay)
            else:
                print(f"❌ 数据库连接失败: {str(e)}")
                return False
    
    return False

if __name__ == "__main__":
    if not wait_for_db():
        sys.exit(1)

