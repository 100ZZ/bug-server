"""数据库迁移脚本：将 users 表的 role 字段改为 roles 字段（JSON类型，支持多角色）"""
import os
import json
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
    with engine.begin() as conn:  # 使用 begin() 自动管理事务
        # 1. 添加新的 roles 字段（JSON类型，可为空）
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN roles JSON COMMENT '用户角色列表'"))
            print('✅ Added roles column')
        except Exception as e:
            if 'Duplicate column' in str(e):
                print('ℹ️ roles column already exists, skipping')
            else:
                print(f'⚠️ Error adding roles column: {e}')
                raise
        
        # 2. 将现有的 role 值迁移到 roles 字段（将单个角色转换为数组）
        try:
            # 获取所有用户的 role 值并转换为 JSON 数组
            result = conn.execute(text("SELECT id, role FROM users WHERE role IS NOT NULL"))
            users = result.fetchall()
            
            for user_id, role in users:
                # 将单个角色转换为数组格式的 JSON 字符串，使用 MySQL 的 JSON_ARRAY 函数
                roles_json = json.dumps([role])
                conn.execute(text(
                    "UPDATE users SET roles = CAST(:roles_json AS JSON) WHERE id = :user_id"
                ), {"roles_json": roles_json, "user_id": user_id})
            
            print(f'✅ Migrated {len(users)} user roles to roles array')
        except Exception as e:
            print(f'⚠️ Error migrating role to roles: {e}')
            raise
        
        # 3. 删除旧的 role 字段
        try:
            conn.execute(text("ALTER TABLE users DROP COLUMN role"))
            print('✅ Dropped role column')
        except Exception as e:
            if "doesn't exist" in str(e) or "Unknown column" in str(e):
                print('ℹ️ role column does not exist, skipping')
            else:
                print(f'⚠️ Error dropping role column: {e}')
                raise

if __name__ == "__main__":
    try:
        migrate()
        print("\n🎉 Database migration completed!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise
