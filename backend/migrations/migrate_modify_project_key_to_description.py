"""数据库迁移脚本：将 projects 表的 key 字段从 VARCHAR(20) NOT NULL UNIQUE 改为 TEXT NULL（描述字段）"""
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
        # 1. 检查并删除 key 字段上的所有索引和唯一约束
        # 在 MySQL 中，UNIQUE 约束会创建索引，索引名可能是 'key' 或 'idx_key'
        try:
            # 获取所有索引
            result = conn.execute(text("SHOW INDEX FROM projects WHERE Column_name = 'key'"))
            indices = result.fetchall()
            
            # 删除所有与 key 字段相关的索引
            dropped_any = False
            for index_row in indices:
                index_name = index_row[2]  # Key_name 是第3列（索引从0开始）
                if index_name != 'PRIMARY':  # 跳过主键
                    try:
                        conn.execute(text(f"DROP INDEX `{index_name}` ON projects"))
                        print(f'✅ Dropped index: {index_name}')
                        dropped_any = True
                    except Exception as e:
                        if 'Unknown key' in str(e) or "doesn't exist" in str(e):
                            pass  # 索引不存在，忽略
                        else:
                            print(f'⚠️ Error dropping index {index_name}: {e}')
            
            if not dropped_any:
                print('ℹ️ No indices found on key column, skipping')
        except Exception as e:
            print(f'ℹ️ Error checking indices (may not exist): {e}')
        
        # 2. 修改 key 字段类型为 TEXT，并移除 NOT NULL 约束
        try:
            conn.execute(text("ALTER TABLE projects MODIFY COLUMN `key` TEXT COMMENT '描述'"))
            print('✅ Modified key column to TEXT type (nullable)')
        except Exception as e:
            if 'Duplicate column' in str(e):
                print('ℹ️ key column already modified')
            else:
                print(f'⚠️ Error modifying key column: {e}')
                raise
        
        conn.commit()
        print('\n🎉 Database migration completed!')

if __name__ == '__main__':
    migrate()
