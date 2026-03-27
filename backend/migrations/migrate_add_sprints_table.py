"""数据库迁移脚本：添加 sprints 表（迭代管理）"""
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
    with engine.begin() as conn:  # 使用 begin() 自动管理事务
        # 创建 sprints 表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS sprints (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT NOT NULL COMMENT '项目ID',
            name VARCHAR(100) NOT NULL COMMENT '迭代名称',
            goal TEXT COMMENT '迭代目标',
            owner VARCHAR(50) COMMENT '负责人',
            start_date DATE NOT NULL COMMENT '起始时间',
            end_date DATE NOT NULL COMMENT '截止时间',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            INDEX idx_project_id (project_id),
            INDEX idx_start_date (start_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='迭代表'
        """
        
        try:
            conn.execute(text(create_table_sql))
            print('✅ Created sprints table')
        except Exception as e:
            if 'already exists' in str(e).lower() or 'Duplicate table' in str(e):
                print('ℹ️ sprints table already exists, skipping')
            else:
                print(f'⚠️ Error creating sprints table: {e}')
                raise

if __name__ == "__main__":
    try:
        migrate()
        print("\n🎉 Database migration completed!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise
