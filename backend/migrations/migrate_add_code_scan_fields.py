"""数据库迁移脚本：添加 language, sonar_project_key, sonar_host, sonar_login 字段到 code_scans 表"""
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Test@123456")
DB_NAME = os.getenv("DB_NAME", "bug_management")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def migrate():
    with engine.connect() as conn:
        # 检查并添加 language 字段
        try:
            conn.execute(text('ALTER TABLE code_scans ADD COLUMN language VARCHAR(50) COMMENT "编程语言：Java, Python, Go, PHP等"'))
            print('✅ Added language column')
        except Exception as e:
            if 'Duplicate column' in str(e):
                print('ℹ️ language column already exists')
            else:
                print(f'⚠️ Error adding language column: {e}')
        
        # 检查并添加 sonar_project_key 字段
        try:
            conn.execute(text('ALTER TABLE code_scans ADD COLUMN sonar_project_key VARCHAR(200) COMMENT "Sonar的projectKey"'))
            print('✅ Added sonar_project_key column')
        except Exception as e:
            if 'Duplicate column' in str(e):
                print('ℹ️ sonar_project_key column already exists')
            else:
                print(f'⚠️ Error adding sonar_project_key column: {e}')
        
        # 检查并添加 sonar_host 字段
        try:
            conn.execute(text('ALTER TABLE code_scans ADD COLUMN sonar_host VARCHAR(500) COMMENT "Sonar的服务host URL"'))
            print('✅ Added sonar_host column')
        except Exception as e:
            if 'Duplicate column' in str(e):
                print('ℹ️ sonar_host column already exists')
            else:
                print(f'⚠️ Error adding sonar_host column: {e}')
        
        # 检查并添加 sonar_login 字段
        try:
            conn.execute(text('ALTER TABLE code_scans ADD COLUMN sonar_login VARCHAR(200) COMMENT "Sonar的login token"'))
            print('✅ Added sonar_login column')
        except Exception as e:
            if 'Duplicate column' in str(e):
                print('ℹ️ sonar_login column already exists')
            else:
                print(f'⚠️ Error adding sonar_login column: {e}')
        
        conn.commit()
        print('\n🎉 Database migration completed!')

if __name__ == '__main__':
    migrate()

