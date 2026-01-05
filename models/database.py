"""
数据库连接和初始化模块
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from utils.path_utils import get_data_path

# 数据库文件路径
DB_PATH = get_data_path('property.db')
DATABASE_URL = f'sqlite:///{DB_PATH}'

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=False, connect_args={'check_same_thread': False})

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def init_db():
    """初始化数据库，创建所有表"""
    from models.resident import Resident
    from models.charge_item import ChargeItem
    from models.payment import Payment
    from models.payment_transaction import PaymentTransaction
    
    Base.metadata.create_all(bind=engine)
    # Ensure new columns exist for migrations (SQLite simple ADD COLUMN)
    try:
        conn = engine.connect()
        try:
            # Check if 'usage' column exists in payments table
            res = conn.execute("PRAGMA table_info('payments')").fetchall()
            col_names = [r[1] for r in res] if res else []
            if 'usage' not in col_names:
                # Add usage column (nullable)
                conn.execute("ALTER TABLE payments ADD COLUMN usage NUMERIC(10,2)")
        finally:
            conn.close()
    except Exception:
        # Migration best-effort: if it fails, continue; errors will surface at runtime when accessing the column
        pass


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

