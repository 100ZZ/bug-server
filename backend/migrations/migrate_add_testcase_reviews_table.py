import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Test@123456")
DB_NAME = os.getenv("DB_NAME", "bug_management")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def migrate():
    with engine.begin() as conn:
        try:
            # 检查表是否已存在
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = :db_name 
                AND table_name = 'testcase_reviews'
            """), {"db_name": DB_NAME})
            
            table_exists = result.fetchone()[0] > 0
            
            if table_exists:
                print('⚠️  testcase_reviews table already exists, skipping creation')
            else:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS testcase_reviews (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        project_id INT NOT NULL COMMENT '所属项目ID',
                        sprint_id INT COMMENT '关联迭代ID',
                        name VARCHAR(200) NOT NULL COMMENT '评审名称',
                        initiator_id INT NOT NULL COMMENT '发起人ID',
                        start_date DATE NOT NULL COMMENT '发起时间',
                        end_date DATE NOT NULL COMMENT '截止时间',
                        status ENUM('not_started', 'in_progress', 'ended') DEFAULT 'not_started' COMMENT '状态',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                        FOREIGN KEY (sprint_id) REFERENCES sprints(id) ON DELETE SET NULL,
                        FOREIGN KEY (initiator_id) REFERENCES users(id) ON DELETE RESTRICT,
                        INDEX idx_project_id (project_id),
                        INDEX idx_sprint_id (sprint_id),
                        INDEX idx_initiator_id (initiator_id),
                        INDEX idx_status (status),
                        INDEX idx_start_date (start_date)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用例评审表';
                """))
                print('✅ Created testcase_reviews table')
            
            # 创建 testcase_review_items 表
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = :db_name 
                AND table_name = 'testcase_review_items'
            """), {"db_name": DB_NAME})
            
            items_table_exists = result.fetchone()[0] > 0
            
            if items_table_exists:
                print('⚠️  testcase_review_items table already exists, skipping creation')
            else:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS testcase_review_items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        review_id INT NOT NULL COMMENT '评审ID',
                        testcase_id INT NOT NULL COMMENT '用例ID',
                        reviewer_id INT COMMENT '评审人ID',
                        status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '评审状态：待评审、通过、不通过',
                        comments TEXT COMMENT '评审意见',
                        reviewed_at TIMESTAMP NULL COMMENT '评审时间',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (review_id) REFERENCES testcase_reviews(id) ON DELETE CASCADE,
                        FOREIGN KEY (testcase_id) REFERENCES testcases(id) ON DELETE CASCADE,
                        FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
                        INDEX idx_review_id (review_id),
                        INDEX idx_testcase_id (testcase_id),
                        INDEX idx_reviewer_id (reviewer_id),
                        INDEX idx_status (status),
                        UNIQUE KEY uk_review_testcase (review_id, testcase_id) COMMENT '同一评审中同一用例只能添加一次'
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用例评审项表';
                """))
                print('✅ Created testcase_review_items table')
        except Exception as e:
            print(f'⚠️ Error creating testcase_reviews table: {e}')
            raise

if __name__ == "__main__":
    try:
        migrate()
        print("\n🎉 Database migration completed!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise
