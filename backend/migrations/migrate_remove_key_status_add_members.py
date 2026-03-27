"""数据库迁移脚本：删除key和status字段，添加project_members表"""
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text, inspect

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Test@123456")
DB_NAME = os.getenv("DB_NAME", "bug_management")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def table_exists(conn, table_name):
    """检查表是否存在"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def column_exists(conn, table_name, column_name):
    """检查列是否存在"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate():
    with engine.connect() as conn:
        # 1. 创建 project_members 关联表
        if not table_exists(conn, 'project_members'):
            try:
                conn.execute(text("""
                    CREATE TABLE project_members (
                        project_id INT NOT NULL,
                        user_id INT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (project_id, user_id),
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        INDEX idx_project (project_id),
                        INDEX idx_user (user_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='项目成员关联表'
                """))
                print('✅ Created project_members table')
            except Exception as e:
                print(f'⚠️ Error creating project_members table: {e}')
                raise
        else:
            print('ℹ️ project_members table already exists')
        
        # 2. 删除 status 字段（如果存在）
        if column_exists(conn, 'projects', 'status'):
            try:
                conn.execute(text('ALTER TABLE projects DROP COLUMN status'))
                print('✅ Dropped status column from projects table')
            except Exception as e:
                print(f'⚠️ Error dropping status column: {e}')
                raise
        else:
            print('ℹ️ status column does not exist in projects table')
        
        # 3. 删除 key 字段（如果存在）
        if column_exists(conn, 'projects', 'key'):
            try:
                conn.execute(text('ALTER TABLE projects DROP COLUMN `key`'))
                print('✅ Dropped key column from projects table')
            except Exception as e:
                print(f'⚠️ Error dropping key column: {e}')
                raise
        else:
            print('ℹ️ key column does not exist in projects table')
        
        # 4. 删除 key 字段的索引（如果存在）
        try:
            conn.execute(text('ALTER TABLE projects DROP INDEX idx_key'))
            print('✅ Dropped idx_key index')
        except Exception as e:
            if 'Unknown key' in str(e) or "Can't DROP" in str(e):
                print('ℹ️ idx_key index does not exist')
            else:
                print(f'⚠️ Error dropping idx_key index: {e}')
        
        conn.commit()
        print('\n🎉 Database migration completed!')

if __name__ == '__main__':
    migrate()

