"""数据库迁移脚本：添加 parameters 和 request_body 字段到 api_endpoints 表"""
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
        # 检查并添加 parameters 字段
        try:
            conn.execute(text('ALTER TABLE api_endpoints ADD COLUMN parameters JSON'))
            print('✅ Added parameters column')
        except Exception as e:
            if 'Duplicate column' in str(e):
                print('ℹ️ parameters column already exists')
            else:
                print(f'⚠️ Error adding parameters column: {e}')
        
        # 检查并添加 request_body 字段
        try:
            conn.execute(text('ALTER TABLE api_endpoints ADD COLUMN request_body JSON'))
            print('✅ Added request_body column')
        except Exception as e:
            if 'Duplicate column' in str(e):
                print('ℹ️ request_body column already exists')
            else:
                print(f'⚠️ Error adding request_body column: {e}')
        
        conn.commit()
        print('\n🎉 Database migration completed!')

if __name__ == '__main__':
    migrate()
