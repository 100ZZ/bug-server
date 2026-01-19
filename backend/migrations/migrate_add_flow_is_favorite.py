"""数据库迁移脚本：添加 is_favorite 字段到 api_test_flows 表"""
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
        # 检查并添加 is_favorite 字段
        try:
            conn.execute(text('ALTER TABLE api_test_flows ADD COLUMN is_favorite BOOLEAN DEFAULT FALSE COMMENT \'是否收藏\' AFTER steps'))
            print('✅ Added is_favorite column to api_test_flows table')
        except Exception as e:
            if 'Duplicate column' in str(e) or 'already exists' in str(e).lower():
                print('ℹ️ is_favorite column already exists in api_test_flows table')
            else:
                print(f'⚠️ Error adding is_favorite column: {e}')
                raise
        
        # 检查并添加索引
        try:
            conn.execute(text('ALTER TABLE api_test_flows ADD INDEX idx_flow_favorite (is_favorite)'))
            print('✅ Added index idx_flow_favorite')
        except Exception as e:
            if 'Duplicate key name' in str(e) or 'already exists' in str(e).lower():
                print('ℹ️ Index idx_flow_favorite already exists')
            else:
                print(f'⚠️ Error adding index: {e}')
                # 索引错误不影响功能，只警告
                pass
        
        conn.commit()
        print('\n🎉 Database migration completed!')

if __name__ == '__main__':
    migrate()

