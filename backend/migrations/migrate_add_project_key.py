"""数据库迁移脚本：添加项目key字段"""
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text, inspect
import re

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Test@123456")
DB_NAME = os.getenv("DB_NAME", "bug_management")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def column_exists(conn, table_name, column_name):
    """检查列是否存在"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def generate_key_from_name(name):
    """从项目名称生成key"""
    # 移除特殊字符，只保留字母和数字
    key = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', name)
    
    # 如果是中文，取拼音首字母或使用默认前缀
    if re.search(r'[\u4e00-\u9fa5]', key):
        # 简单处理：使用 PROJ 作为默认前缀
        key = 'PROJ'
    else:
        # 取前4个字符，转大写
        key = key[:4].upper()
    
    # 如果key为空或太短，使用默认值
    if len(key) < 2:
        key = 'PROJ'
    
    return key

def migrate():
    with engine.connect() as conn:
        # 1. 添加 key 字段（如果不存在）
        if not column_exists(conn, 'projects', 'key'):
            try:
                # 添加字段（先允许为NULL）
                conn.execute(text("""
                    ALTER TABLE projects 
                    ADD COLUMN `key` VARCHAR(20) NULL
                """))
                print('✅ Added key column to projects table')
                conn.commit()
            except Exception as e:
                print(f'⚠️ Error adding key column: {e}')
                raise
        else:
            print('ℹ️ key column already exists in projects table')
        
        # 2. 为现有项目生成唯一的key
        try:
            # 获取所有项目
            result = conn.execute(text("SELECT id, name, `key` FROM projects"))
            projects = result.fetchall()
            
            existing_keys = set()
            
            for project in projects:
                project_id, name, current_key = project
                
                # 如果已经有key，跳过
                if current_key:
                    existing_keys.add(current_key)
                    continue
                
                # 生成基础key
                base_key = generate_key_from_name(name)
                key = base_key
                
                # 确保key唯一
                counter = 1
                while key in existing_keys:
                    key = f"{base_key}{counter}"
                    counter += 1
                
                # 更新项目的key
                conn.execute(
                    text("UPDATE projects SET `key` = :key WHERE id = :id"),
                    {"key": key, "id": project_id}
                )
                existing_keys.add(key)
                print(f'✅ Generated key "{key}" for project "{name}"')
            
            conn.commit()
            print('✅ Generated keys for all projects')
        except Exception as e:
            print(f'⚠️ Error generating keys: {e}')
            raise
        
        # 3. 修改key字段为NOT NULL并添加唯一索引
        try:
            # 先检查是否有NULL值
            result = conn.execute(text("SELECT COUNT(*) FROM projects WHERE `key` IS NULL"))
            null_count = result.scalar()
            
            if null_count > 0:
                print(f'⚠️ Warning: {null_count} projects still have NULL keys')
                raise Exception('Cannot set key to NOT NULL: some projects have NULL keys')
            
            # 设置为NOT NULL
            conn.execute(text("""
                ALTER TABLE projects 
                MODIFY COLUMN `key` VARCHAR(20) NOT NULL
            """))
            print('✅ Set key column to NOT NULL')
            
            # 添加唯一索引
            conn.execute(text("""
                ALTER TABLE projects 
                ADD UNIQUE INDEX idx_project_key (`key`)
            """))
            print('✅ Added unique index on key column')
            
            conn.commit()
        except Exception as e:
            if 'Duplicate key name' in str(e):
                print('ℹ️ Unique index idx_project_key already exists')
            else:
                print(f'⚠️ Error setting constraints: {e}')
                raise
        
        print('\n🎉 Database migration completed!')

if __name__ == '__main__':
    migrate()
